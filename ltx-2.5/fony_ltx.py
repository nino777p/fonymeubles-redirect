#!/usr/bin/env python3
"""Génère une vidéo produit Fony Meubles avec LTX-2.5, dans le cadre de la charte.

- Construit un prompt structuré (produit + pièce + mouvement de caméra + style pro).
- Refuse les termes hors charte (enfantin, farfelu, effets gadgets).
- N'active jamais l'« enhancer » de prompt (il réécrit et peut inventer des éléments).
- Par défaut : affiche seulement la commande (--dry-run). Ajouter --run pour lancer.

Exemple :
  python fony_ltx.py --produit "a three-seat sofa in light grey bouclé fabric with oak legs" \
      --scene salon --camera orbite --format web_16_9 --image photos/canape.jpg --run
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
CHARTE = ICI / "charte_fony.json"
MODELES = ICI / "models" / "ltx-2.5"

FICHIERS = {
    "--transformer-path": "diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors",
    "--text-encoder-path": "text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors",
    "--video-vae-path": "vae/ltx-2.5-video-vae-bf16.safetensors",
    "--audio-vae-path": "vae/ltx-2.5-audio-vae-bf16.safetensors",
    "--spatial-upsampler-path": "latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors",
}
LORA_DFR = "loras/ltx-2.5-22b-ic-lora-pixel-spatial-upscaler-x2-1.0.safetensors"


def _norm(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", txt.lower())
    return "".join(c for c in txt if not unicodedata.combining(c))


def termes_interdits(texte: str, interdits: list[str]) -> list[str]:
    t = _norm(texte)
    return sorted({m for m in interdits if re.search(r"\b" + re.escape(_norm(m)) + r"\b", t)})


def nb_images(secondes: float, fps: int) -> int:
    """Le modèle exige un nombre d'images de la forme 8k+1."""
    n = round(secondes * fps)
    return max(9, (n // 8) * 8 + 1)


def construire_prompt(charte: dict, produit: str, scene: str, camera: str, details: str) -> str:
    morceaux = [
        f"{charte['mouvements_camera'][camera]}",
        f"The shot shows {produit}, placed in {charte['scenes'][scene]}.",
        details.strip(),
        charte["style_global"],
        charte["audio_par_defaut"],
    ]
    return " ".join(m for m in morceaux if m)


def main() -> int:
    charte = json.loads(CHARTE.read_text(encoding="utf-8"))
    formats = {k: v for k, v in charte["formats"].items() if not k.startswith("_")}

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--produit", required=True, help="Description du meuble, en anglais (matière, couleur, forme).")
    p.add_argument("--scene", choices=sorted(charte["scenes"]), default="salon")
    p.add_argument("--camera", choices=sorted(charte["mouvements_camera"]), default="travelling_avant")
    p.add_argument("--format", choices=sorted(formats), default="web_16_9")
    p.add_argument("--duree", type=float, default=charte["duree_secondes_defaut"], help="Secondes (3 à 10 conseillé).")
    p.add_argument("--details", default="", help="Précisions facultatives, en anglais.")
    p.add_argument("--image", help="Photo du produit (JPG/PNG) utilisée comme première image : rendu fidèle au vrai meuble.")
    p.add_argument("--force-image", type=float, default=1.0, help="Fidélité à la photo (0.6 à 1.0).")
    p.add_argument("--qualite", choices=["rapide", "production"], default="rapide",
                   help="rapide = pipeline distillé ; production = DFR (plus lent, plus de mémoire GPU).")
    p.add_argument("--memoire-limitee", action="store_true", help="Active FP8 + déchargement CPU (GPU < 48 Go).")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--sortie", default="sorties/video.mp4")
    p.add_argument("--run", action="store_true", help="Lance réellement la génération (sinon affiche la commande).")
    a = p.parse_args()

    a.duree = min(max(a.duree, 2.0), 10.0)
    # La génération tourne dans le dossier LTX-2 : on passe des chemins absolus.
    a.sortie = str(Path(a.sortie).resolve())
    if a.image:
        img = Path(a.image).resolve()
        if not img.is_file():
            print(f"Image introuvable : {img}", file=sys.stderr)
            return 1
        a.image = str(img)

    prompt = construire_prompt(charte, a.produit, a.scene, a.camera, a.details)
    bad = termes_interdits(a.produit + " " + a.details, charte["mots_interdits"])
    if bad:
        print(f"REFUSÉ — termes hors charte : {', '.join(bad)}", file=sys.stderr)
        return 2

    fmt = formats[a.format]
    module = "ltx_pipelines.dfr_pipeline" if a.qualite == "production" else "ltx_pipelines.distilled"
    cmd = ["uv", "run", "python", "-m", module]
    for flag, rel in FICHIERS.items():
        cmd += [flag, str(MODELES / rel)]
    if a.qualite == "production":
        cmd += ["--detailing-lora", str(MODELES / LORA_DFR)]
    cmd += [
        "--width", str(fmt["width"]), "--height", str(fmt["height"]),
        "--frame-rate", str(fmt["fps"]), "--num-frames", str(nb_images(a.duree, fmt["fps"])),
        "--seed", str(a.seed), "--output-path", a.sortie, "--prompt", prompt,
    ]
    if a.image:
        cmd += ["--image", a.image, "0", str(a.force_image)]
    if a.memoire_limitee:
        cmd += ["--quantization", "fp8-cast", "--offload", "cpu"]
    # Volontairement absent : --enhance-prompt (réécriture automatique = risque d'éléments farfelus).

    print("PROMPT :\n" + prompt + "\n")
    print("COMMANDE :\n" + shlex.join(cmd) + "\n")
    print("RAPPEL : " + charte["mention_obligatoire"])
    if not a.run:
        print("\n(simulation — ajoutez --run pour générer)")
        return 0
    Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
    return subprocess.call(cmd, cwd=ICI / "LTX-2")


if __name__ == "__main__":
    sys.exit(main())
