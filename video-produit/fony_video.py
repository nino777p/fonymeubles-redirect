#!/usr/bin/env python3
"""Vidéo produit Fony Meubles à partir de VRAIES photos — 100 % gratuit, sans IA générative.

Le meuble n'est jamais modifié : seuls la caméra (zoom/travelling lents), les fondus
et le rythme sont créés. Rendu : mouvements doux type publicité premium.

Prérequis (gratuits) : Python 3, Pillow (pip install pillow), ffmpeg (brew install ffmpeg).

Exemple :
  python3 fony_video.py photos/canape1.jpg photos/canape2.jpg photos/canape3.jpg \
      --duree 25 --format reel --texte-fin "Fony Meubles" --musique musique.mp3 -o canape.mp4
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

FORMATS = {"web": (1920, 1080), "reel": (1080, 1920), "carre": (1080, 1080)}
FPS = 30
FONDU = 1.0          # secondes de fondu enchaîné entre deux photos
ZOOM = 0.07          # amplitude du zoom (7 %) : assez pour sentir le mouvement, sans « effet gadget »
MOUVEMENTS = ["avance", "lateral_droite", "recule", "lateral_gauche"]
POLICES = [
    "/System/Library/Fonts/Supplemental/Didot.ttc",              # macOS, élégant
    "/System/Library/Fonts/HelveticaNeue.ttc",                   # macOS
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",          # Linux
]


def ease(t: float) -> float:
    """Accélération/décélération douce (pas de démarrage brusque)."""
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def preparer(photo: Path, w: int, h: int, cadrage: str) -> Image.Image:
    """Image de travail à 115 % de la taille finale (marge pour bouger sans bords vides)."""
    img = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
    W, H = int(w * 1.15), int(h * 1.15)
    ratio_img, ratio_out = img.width / img.height, w / h
    if cadrage == "auto":
        cadrage = "remplir" if abs(math.log(ratio_img / ratio_out)) < 0.25 else "complet"
    if cadrage == "remplir":
        return ImageOps.fit(img, (W, H), Image.LANCZOS)
    # « complet » : meuble entier visible, fond = même photo floutée et assombrie
    fond = ImageOps.fit(img, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    fond = Image.blend(fond, Image.new("RGB", fond.size, (20, 20, 20)), 0.35)
    premier = ImageOps.contain(img, (int(W * 0.92), int(H * 0.92)), Image.LANCZOS)
    fond.paste(premier, ((W - premier.width) // 2, (H - premier.height) // 2))
    return fond


def image_animee(src: Image.Image, w: int, h: int, mouvement: str, t: float) -> Image.Image:
    """Cadre de la caméra à l'instant t (0→1), avec précision sous-pixel (pas de tremblement)."""
    e = ease(t)
    W, H = src.size
    base = min(W / w, H / h)                      # échelle qui remplit exactement la sortie
    if mouvement == "avance":
        z, dx = 1 + ZOOM * e, 0.0
    elif mouvement == "recule":
        z, dx = 1 + ZOOM * (1 - e), 0.0
    elif mouvement == "lateral_droite":
        z, dx = 1 + ZOOM * 0.5, (e - 0.5)
    else:
        z, dx = 1 + ZOOM * 0.5, (0.5 - e)
    cw, ch = w * base / z, h * base / z           # taille de la zone vue dans l'image source
    marge_x = (W - cw) / 2
    cx = W / 2 + dx * marge_x * 0.9
    cy = H / 2
    x0, y0 = cx - cw / 2, cy - ch / 2
    return src.transform((w, h), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)


def carton_fin(w: int, h: int, texte: str, sous_titre: str, police: str | None) -> Image.Image:
    img = Image.new("RGB", (w, h), (245, 242, 237))   # blanc cassé chaud, sobre
    d = ImageDraw.Draw(img)
    chemins = [police] if police else POLICES
    f1 = f2 = None
    for p in chemins:
        if p and Path(p).exists():
            f1 = ImageFont.truetype(p, int(min(w, h) * 0.08))
            f2 = ImageFont.truetype(p, int(min(w, h) * 0.032))
            break
    f1, f2 = f1 or ImageFont.load_default(), f2 or ImageFont.load_default()
    d.text((w / 2, h / 2), texte, font=f1, fill=(40, 36, 32), anchor="mm")
    if sous_titre:
        d.text((w / 2, h / 2 + min(w, h) * 0.09), sous_titre, font=f2, fill=(110, 104, 96), anchor="mm")
    return img


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("photos", nargs="+", type=Path, help="Photos du produit (JPG/PNG), dans l'ordre voulu.")
    p.add_argument("--duree", type=float, default=25, help="Durée totale en secondes (défaut 25).")
    p.add_argument("--format", choices=FORMATS, default="web", help="web 16:9, reel 9:16, carre 1:1.")
    p.add_argument("--cadrage", choices=["auto", "remplir", "complet"], default="auto",
                   help="remplir = recadre ; complet = meuble entier sur fond flouté ; auto = choisit.")
    p.add_argument("--texte-fin", default="", help="Texte du carton final (ex. « Fony Meubles »). Vide = pas de carton.")
    p.add_argument("--sous-titre", default="", help="Ligne sous le texte final (ex. site web).")
    p.add_argument("--police", help="Chemin d'une police .ttf/.ttc (sinon police élégante du Mac).")
    p.add_argument("--musique", type=Path, help="Fichier audio libre de droits (optionnel).")
    p.add_argument("-o", "--sortie", type=Path, default=Path("video_fony.mp4"))
    a = p.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg introuvable. Sur Mac : brew install ffmpeg", file=sys.stderr)
        return 1
    for ph in a.photos:
        if not ph.is_file():
            print(f"Photo introuvable : {ph}", file=sys.stderr)
            return 1
    if a.musique and not a.musique.is_file():
        print(f"Musique introuvable : {a.musique}", file=sys.stderr)
        return 1

    w, h = FORMATS[a.format]
    duree_fin = 3.0 if a.texte_fin else 0.0
    n = len(a.photos)
    # durée de chaque plan, fondus compris (les fondus se chevauchent)
    plan = (a.duree - duree_fin + FONDU * (n - 1 + (1 if a.texte_fin else 0))) / n
    if plan < 2.5:
        print(f"Trop de photos pour {a.duree:.0f} s (plans de {plan:.1f} s). Retirez des photos ou allongez.", file=sys.stderr)
        return 1

    sources = [preparer(ph, w, h, a.cadrage) for ph in a.photos]
    fin = carton_fin(w, h, a.texte_fin, a.sous_titre, a.police) if a.texte_fin else None
    noir = Image.new("RGB", (w, h), (0, 0, 0))
    total = int(round(a.duree * FPS))
    pas = plan - FONDU                                  # décalage entre débuts de plans

    def image_au_temps(s: float) -> Image.Image:
        i = min(int(s // pas), n - 1)
        def plan_i(k: int) -> Image.Image:
            return image_animee(sources[k], w, h, MOUVEMENTS[k % len(MOUVEMENTS)], (s - k * pas) / plan)
        img = plan_i(i)
        debut_suivant = (i + 1) * pas
        if s >= debut_suivant:                          # zone de fondu enchaîné
            alpha = ease((s - debut_suivant) / FONDU)
            suivant = plan_i(i + 1) if i + 1 < n else fin
            if suivant is not None:
                img = Image.blend(img, suivant, alpha)
        if fin is not None and s >= n * pas + FONDU:
            img = fin
        if s < 0.6:                                     # ouverture depuis le noir
            img = Image.blend(noir, img, ease(s / 0.6))
        if s > a.duree - 0.8:                           # fermeture en douceur
            img = Image.blend(img, noir, ease((s - (a.duree - 0.8)) / 0.8))
        return img

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-"]
    if a.musique:
        cmd += ["-i", str(a.musique), "-filter_complex",
                f"[1:a]atrim=0:{a.duree},afade=t=in:d=1,afade=t=out:st={a.duree - 2}:d=2,volume=0.8[a]",
                "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(a.sortie)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(total):
        proc.stdin.write(image_au_temps(f / FPS).tobytes())
        if f % FPS == 0:
            print(f"\r{100 * f // total} %", end="", flush=True)
    proc.stdin.close()
    code = proc.wait()
    print(f"\r100 % — vidéo créée : {a.sortie}" if code == 0 else "\nErreur ffmpeg")
    return code


if __name__ == "__main__":
    sys.exit(main())
