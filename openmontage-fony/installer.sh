#!/usr/bin/env bash
# Branche le module Fony Meubles dans une installation OpenMontage existante.
# Usage :  ./installer.sh /chemin/vers/OpenMontage
# Ajoute uniquement des fichiers (aucun fichier OpenMontage existant n'est modifié).
set -euo pipefail

OM="${1:-}"
[ -n "$OM" ] && [ -f "$OM/tools/base_tool.py" ] || { echo "Usage : $0 /chemin/vers/OpenMontage  (dossier contenant tools/base_tool.py)"; exit 1; }
ICI="$(cd "$(dirname "$0")" && pwd)"
MOTEUR="$ICI/../video-produit/fony_motion.py"
[ -f "$MOTEUR" ] || { echo "Moteur introuvable : $MOTEUR"; exit 1; }

for cible in tools/video/fony_photo_motion.py tools/video/_fony_motion.py styles/custom/fony-meubles.yaml skills/creative/fony-meubles.md; do
  if [ -e "$OM/$cible" ]; then cp "$OM/$cible" "$OM/$cible.bak"; echo "Sauvegarde : $cible.bak"; fi
done

cp "$MOTEUR"                                   "$OM/tools/video/_fony_motion.py"
cp "$ICI/tools/video/fony_photo_motion.py"     "$OM/tools/video/fony_photo_motion.py"
mkdir -p "$OM/styles/custom"
cp "$ICI/styles/custom/fony-meubles.yaml"      "$OM/styles/custom/fony-meubles.yaml"
cp "$ICI/skills/creative/fony-meubles.md"      "$OM/skills/creative/fony-meubles.md"

echo "Vérification dans OpenMontage…"
cd "$OM"
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
"$PY" - <<'EOF'
from tools.tool_registry import ToolRegistry
from styles.playbook_loader import load_playbook
r = ToolRegistry(); r.discover("tools")
t = r.get("fony_photo_motion")
assert t is not None, "outil non découvert"
print("Outil fony_photo_motion :", t.get_status().value)
load_playbook("fony-meubles"); print("Style fony-meubles : OK")
EOF
echo "Installé. Dans Claude Code, ouvre le dossier OpenMontage et colle le prompt du README."
