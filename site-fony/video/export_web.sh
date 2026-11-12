#!/usr/bin/env bash
# Prépare une vidéo produit pour le site : MP4 léger (sans son, lecture immédiate) + image d'aperçu AVIF/WebP.
# Usage :  ./export_web.sh video_source.mp4 nom-court      (ex. ./export_web.sh canape_reel.mp4 md-gala-video)
# Sortie : nom-court.mp4, nom-court-poster.avif, nom-court-poster.webp (à copier dans assets/video/ et assets/img/)
set -euo pipefail
SRC="${1:?vidéo source}"; NOM="${2:?nom court, ex. md-gala-video}"
command -v ffmpeg >/dev/null || { echo "ffmpeg requis (brew install ffmpeg)"; exit 1; }

# 1080 px max sur le petit côté, H.264 compatible partout, sans piste audio, démarrage rapide.
ffmpeg -loglevel error -y -i "$SRC" -an \
  -vf "scale='if(gt(iw,ih),-2,min(1080,iw))':'if(gt(iw,ih),min(1080,ih),-2)',fps=30,format=yuv420p" \
  -c:v libx264 -preset slow -crf 26 -profile:v high -movflags +faststart "$NOM.mp4"

# Aperçu : la première image nette (0,8 s, après le fondu d'ouverture).
ffmpeg -loglevel error -y -ss 0.8 -i "$SRC" -frames:v 1 -vf "scale='min(1080,iw)':-2" "$NOM-poster.png"
ffmpeg -loglevel error -y -i "$NOM-poster.png" -c:v libaom-av1 -still-picture 1 -crf 32 "$NOM-poster.avif" 2>/dev/null \
  || echo "(AVIF non disponible dans cet ffmpeg : seul le WebP est produit)"
ffmpeg -loglevel error -y -i "$NOM-poster.png" -quality 82 "$NOM-poster.webp"
rm -f "$NOM-poster.png"

ls -lh "$NOM".mp4 "$NOM"-poster.* | awk '{print $5, $9}'
DIM=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$NOM.mp4")
echo "Dimensions : $DIM — à reporter dans width/height de la balise <video>."
