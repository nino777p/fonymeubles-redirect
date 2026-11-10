#!/usr/bin/env bash
# Installation sécurisée de LTX-2.5 pour Fony Meubles (Linux ou Windows/WSL2 + GPU NVIDIA).
# - Code source figé sur la version auditée (commit ci-dessous).
# - Poids figés sur la révision Hugging Face auditée.
# - Contrôle final : uniquement des fichiers .safetensors (aucun format exécutable type pickle).
set -euo pipefail

LTX_COMMIT="4f521619ae0029e8fbb64d555030c2b121a33b4f"   # Lightricks/LTX-2, audité le 10/11/2026
HF_REVISION="49b093a39c19169a8a81721dcc541e07e945232f"  # Lightricks/LTX-2.5, audité le 10/11/2026
ICI="$(cd "$(dirname "$0")" && pwd)"
MODELES="$ICI/models/ltx-2.5"
WITH_DFR="${WITH_DFR:-0}"   # WITH_DFR=1 ./install.sh  -> ajoute le module "qualité production"

echo "== 1/5 Vérification du matériel"
command -v nvidia-smi >/dev/null || { echo "ERREUR : aucun GPU NVIDIA détecté. LTX-2.5 exige une carte NVIDIA."; exit 1; }
VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1 | tr -d ' ')
echo "GPU : $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1) — ${VRAM_MB} Mo"
if [ "$VRAM_MB" -lt 24000 ]; then
  echo "ATTENTION : moins de 24 Go de mémoire GPU. Ça risque d'être très lent ou d'échouer, même avec --memoire-limitee."
fi
LIBRE_GB=$(df -BG --output=avail "$ICI" | tail -1 | tr -dc '0-9')
[ "$LIBRE_GB" -ge 90 ] || { echo "ERREUR : il faut au moins 90 Go libres (≈66 Go de modèles + environnement). Libre : ${LIBRE_GB} Go"; exit 1; }

echo "== 2/5 Outil uv (gestionnaire Python officiel d'Astral)"
if ! command -v uv >/dev/null; then
  echo "uv absent. Installez-le depuis la source officielle : https://docs.astral.sh/uv/getting-started/installation/"
  echo "puis relancez ce script."; exit 1
fi

echo "== 3/5 Code source LTX-2 (version auditée)"
if [ ! -d "$ICI/LTX-2/.git" ]; then
  git init -q "$ICI/LTX-2"
  git -C "$ICI/LTX-2" remote add origin https://github.com/Lightricks/LTX-2.git
fi
git -C "$ICI/LTX-2" fetch -q --depth 1 origin "$LTX_COMMIT"
git -C "$ICI/LTX-2" checkout -q FETCH_HEAD
( cd "$ICI/LTX-2" && uv sync )

echo "== 4/5 Téléchargement des poids (≈66 Go)"
echo "Prérequis : compte Hugging Face, conditions acceptées sur https://huggingface.co/Lightricks/LTX-2.5"
echo "et jeton en LECTURE seule (hf auth login)."
( cd "$ICI/LTX-2" && uv run hf download Lightricks/LTX-2.5 --revision "$HF_REVISION" \
    diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors \
    text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors \
    vae/ltx-2.5-video-vae-bf16.safetensors \
    vae/ltx-2.5-audio-vae-bf16.safetensors \
    latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors \
    --local-dir "$MODELES" )
if [ "$WITH_DFR" = "1" ]; then
  ( cd "$ICI/LTX-2" && uv run hf download Lightricks/LTX-2.5-22b-IC-LoRA-Pixel-Spatial-Upscaler \
      ltx-2.5-22b-ic-lora-pixel-spatial-upscaler-x2-1.0.safetensors --local-dir "$MODELES/loras" )
fi

echo "== 5/5 Contrôle de sécurité des fichiers téléchargés"
SUSPECTS=$(find "$MODELES" -type f ! -path '*/.cache/*' ! -name '*.safetensors' ! -name '*.md' ! -name '.gitattributes' || true)
if [ -n "$SUSPECTS" ]; then
  echo "ALERTE : fichiers inattendus (non .safetensors) — ne pas utiliser avant vérification :"; echo "$SUSPECTS"; exit 1
fi
echo "OK : uniquement des fichiers .safetensors (format sans code exécutable)."
echo
echo "Installation terminée. Test :"
echo "  python3 $ICI/fony_ltx.py --produit \"a solid oak dining table with six chairs\" --scene salle_a_manger --camera lateral --format brouillon --run"
