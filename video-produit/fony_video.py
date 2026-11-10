#!/usr/bin/env python3
"""Vidéo produit Fony Meubles à partir de VRAIES photos — 100 % gratuit, sans IA générative.

Le meuble n'est jamais modifié : seuls la caméra (zoom/dérive lents), les fondus et le
rythme sont créés. Rendu sobre type catalogue / publicité mobilier premium.

Prérequis (gratuits) : Python 3, Pillow (pip install pillow), ffmpeg (brew install ffmpeg).

Exemple :
  python3 fony_video.py photos/*.jpg --duree 25 --format reel \
      --texte-fin "Fony Meubles" --sous-titre "fonymeubles.fr" --musique musique.mp3 -o canape.mp4
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image

import fony_motion as fm

FORMATS = {"web": (1920, 1080), "reel": (1080, 1920), "carre": (1080, 1080)}
FONDU = 0.8


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("photos", nargs="+", type=Path, help="Photos du produit, dans l'ordre voulu (3 à 8 conseillé).")
    p.add_argument("--duree", type=float, default=25, help="Durée totale en secondes (défaut 25).")
    p.add_argument("--format", choices=FORMATS, default="reel", help="reel 9:16, web 16:9, carre 1:1.")
    p.add_argument("--cadrage", choices=["auto", "remplir", "galerie"], default="auto",
                   help="remplir = plein cadre recadré ; galerie = photo entière sur fond uni ; auto = choisit.")
    p.add_argument("--texte-fin", default="", help="Texte du carton final (ex. « Fony Meubles »).")
    p.add_argument("--sous-titre", default="", help="Ligne sous le texte final (ex. site web).")
    p.add_argument("--police", help="Police de la charte (.ttf/.otf/.ttc).")
    p.add_argument("--musique", type=Path, help="Piste audio libre de droits (fortement conseillé).")
    p.add_argument("-o", "--sortie", type=Path, default=Path("video_fony.mp4"))
    a = p.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg introuvable. Sur Mac : brew install ffmpeg", file=sys.stderr)
        return 1
    for f in a.photos + ([a.musique] if a.musique else []):
        if not f.is_file():
            print(f"Fichier introuvable : {f}", file=sys.stderr)
            return 1

    w, h = FORMATS[a.format]
    d_fin = 3.5 if a.texte_fin else 0.0
    n = len(a.photos)
    plan = (a.duree - d_fin + FONDU * (n - 1 + (1 if a.texte_fin else 0))) / n
    if plan < 2.5:
        print(f"Trop de photos pour {a.duree:.0f} s (plans de {plan:.1f} s). Retirez des photos ou allongez.", file=sys.stderr)
        return 1
    if plan > 6:
        print(f"Conseil : plans de {plan:.1f} s, c'est long. Ajoutez des photos (angles, détails) pour plus de rythme.")

    plans = [fm.preparer(ph, w, h, a.cadrage) for ph in a.photos]
    pas = plan - FONDU
    debut_fin = n * pas                         # début du fondu vers le carton
    noir = Image.new("RGB", (w, h), (0, 0, 0))

    def img_plan(k: int, s: float) -> Image.Image:
        return fm.image(plans[k], fm.MOUVEMENTS[k % len(fm.MOUVEMENTS)], (s - k * pas) / plan)

    def frame(s: float) -> Image.Image:
        if a.texte_fin and s >= debut_fin + FONDU:
            img = fm.carton(w, h, a.texte_fin, a.sous_titre, a.police, (s - debut_fin - FONDU) / 0.9)
        else:
            i = min(int(s // pas), n - 1)
            img = img_plan(i, s)
            if s >= (i + 1) * pas:
                alpha = fm.ease((s - (i + 1) * pas) / FONDU)
                suivant = img_plan(i + 1, s) if i + 1 < n else (fm.carton(w, h, "", "", a.police) if a.texte_fin else None)
                if suivant is not None:
                    img = Image.blend(img, suivant, alpha)
        if s < 0.6:
            img = Image.blend(noir, img, fm.ease(s / 0.6))
        if not a.texte_fin and s > a.duree - 0.8:   # sans carton : fermeture au noir
            img = Image.blend(img, noir, fm.ease((s - (a.duree - 0.8)) / 0.8))
        return img

    total = int(round(a.duree * fm.FPS))
    proc = fm.encodeur(a.sortie, w, h, a.musique, a.duree)
    for f in range(total):
        proc.stdin.write(frame(f / fm.FPS).tobytes())
        if f % fm.FPS == 0:
            print(f"\r{100 * f // total} %", end="", flush=True)
    proc.stdin.close()
    code = proc.wait()
    print(f"\r100 % — vidéo créée : {a.sortie}" if code == 0 else "\nErreur ffmpeg")
    return code


if __name__ == "__main__":
    sys.exit(main())
