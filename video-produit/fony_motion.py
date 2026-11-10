"""Moteur de mouvement Fony Meubles : anime de VRAIES photos sans jamais modifier le produit.

Utilisé par fony_video.py (montage complet autonome) et par l'outil OpenMontage
« fony_photo_motion » (un plan animé par photo, que l'agent OpenMontage monte ensuite).
Dépendances : Pillow + ffmpeg. Aucune IA, aucun coût.
"""
from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

FPS = 30
FOND_GALERIE = (245, 242, 237)      # blanc cassé chaud
TEXTE = (40, 36, 32)
TEXTE_DOUX = (120, 112, 102)
MOUVEMENTS = ["avance", "recule", "derive_droite", "derive_gauche"]
POLICES = [
    "/System/Library/Fonts/Supplemental/Didot.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]


def ease(t: float) -> float:
    """Départ et arrêt progressifs (courbe cosinus)."""
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


@dataclass
class Plan:
    src: Image.Image
    mode: str            # "remplir" ou "galerie"
    w: int
    h: int
    ombre: Image.Image | None = None


def preparer(photo: Path, w: int, h: int, cadrage: str = "auto") -> Plan:
    img = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
    if cadrage == "auto":
        ecart = abs(math.log((img.width / img.height) / (w / h)))
        cadrage = "remplir" if ecart < 0.35 else "galerie"
    if cadrage == "remplir":
        # 12 % de marge autour du cadre final pour bouger sans bord vide
        return Plan(ImageOps.fit(img, (int(w * 1.12), int(h * 1.12)), Image.LANCZOS), "remplir", w, h)
    # galerie : photo entière, posée sur fond uni avec une ombre douce (rendu « catalogue »)
    largeur_max, hauteur_max = int(w * 0.88), int(h * 0.78)
    photo_ok = ImageOps.contain(img, (largeur_max, hauteur_max), Image.LANCZOS)
    return Plan(photo_ok, "galerie", w, h, _ombre(photo_ok.size))


def _ombre(taille: tuple[int, int], flou: int = 28) -> Image.Image:
    m = flou * 2
    masque = Image.new("L", (taille[0] + 2 * m, taille[1] + 2 * m), 0)
    ImageDraw.Draw(masque).rectangle([m, m + flou // 2, m + taille[0], m + taille[1] + flou // 2], fill=70)
    return masque.filter(ImageFilter.GaussianBlur(flou))


def image(plan: Plan, mouvement: str, t: float, amplitude: float = 0.07) -> Image.Image:
    """Image du plan à l'instant t (0→1). Calcul sous-pixel : aucun tremblement."""
    e = ease(t)
    w, h = plan.w, plan.h
    if plan.mode == "galerie":
        # fond fixe, seule la photo grandit (ou rétrécit) très lentement
        s = 1 + 0.04 * (e if mouvement != "recule" else 1 - e)
        pw, ph = int(plan.src.width * s), int(plan.src.height * s)
        ph_img = plan.src.resize((pw, ph), Image.BICUBIC)
        fond = Image.new("RGB", (w, h), FOND_GALERIE)
        x, y = (w - pw) // 2, int((h - ph) * 0.45)
        m0 = (plan.ombre.width - plan.src.width) // 2
        omb = plan.ombre.resize((pw + 2 * m0, ph + 2 * m0), Image.BILINEAR)
        m = m0
        fond.paste((90, 80, 70), (x - m, y - m, x - m + omb.width, y - m + omb.height), omb)
        fond.paste(ph_img, (x, y))
        return fond
    W, H = plan.src.size
    base = min(W / w, H / h)
    if mouvement == "avance":
        z, dx = 1 + amplitude * e, 0.0
    elif mouvement == "recule":
        z, dx = 1 + amplitude * (1 - e), 0.0
    elif mouvement == "derive_droite":
        z, dx = 1 + amplitude * (0.4 + 0.3 * e), (e - 0.5) * 0.6
    else:
        z, dx = 1 + amplitude * (0.4 + 0.3 * e), (0.5 - e) * 0.6
    cw, ch = w * base / z, h * base / z
    cx = W / 2 + dx * (W - cw) / 2
    x0, y0 = cx - cw / 2, (H - ch) / 2
    return plan.src.transform((w, h), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)


def _police(chemin: str | None, taille: int) -> ImageFont.ImageFont:
    for p in ([chemin] if chemin else []) + POLICES:
        if p and Path(p).exists():
            return ImageFont.truetype(p, taille)
    return ImageFont.load_default()


def carton(w: int, h: int, titre: str, sous_titre: str = "", police: str | None = None, t: float = 1.0) -> Image.Image:
    """Carton final sobre ; t (0→1) fait apparaître le texte en douceur."""
    img = Image.new("RGB", (w, h), FOND_GALERIE)
    a = ease(t)
    if a <= 0 or not titre:
        return img
    d = ImageDraw.Draw(img)
    base = min(w, h)
    couleur = lambda c: tuple(int(FOND_GALERIE[i] + (c[i] - FOND_GALERIE[i]) * a) for i in range(3))
    dy = int((1 - a) * base * 0.015)
    d.text((w / 2, h / 2 - base * 0.02 + dy), titre, font=_police(police, int(base * 0.11)), fill=couleur(TEXTE), anchor="mm")
    trait = int(base * 0.06)
    d.line([(w / 2 - trait, h / 2 + base * 0.065), (w / 2 + trait, h / 2 + base * 0.065)], fill=couleur(TEXTE_DOUX), width=2)
    if sous_titre:
        d.text((w / 2, h / 2 + base * 0.12 + dy), sous_titre, font=_police(police, int(base * 0.038)),
               fill=couleur(TEXTE_DOUX), anchor="mm")
    return img


def encodeur(sortie: Path, w: int, h: int, musique: Path | None = None, duree: float = 0, fps: int = FPS) -> subprocess.Popen:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-"]
    if musique:
        cmd += ["-i", str(musique), "-filter_complex",
                f"[1:a]atrim=0:{duree},afade=t=in:d=1,afade=t=out:st={max(duree - 2.5, 0)}:d=2.5,volume=0.8[a]",
                "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(sortie)]
    sortie.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def rendre_plan(photo: Path, sortie: Path, w: int, h: int, secondes: float,
                mouvement: str = "avance", cadrage: str = "auto", fps: int = FPS) -> Path:
    """Un plan animé (sans son) à partir d'une photo — brique utilisée par OpenMontage."""
    plan = preparer(photo, w, h, cadrage)
    n = int(round(secondes * fps))
    proc = encodeur(sortie, w, h, fps=fps)
    for f in range(n):
        proc.stdin.write(image(plan, mouvement, f / max(n - 1, 1)).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg a échoué pour {sortie}")
    return sortie
