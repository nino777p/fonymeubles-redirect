# Vidéos produit Fony Meubles — gratuit, sans IA générative

`fony_video.py` transforme **tes vraies photos** en une vidéo de 20 à 30 s au rendu « pub premium » :
mouvements de caméra lents et fluides (avancée, recul, travelling), fondus enchaînés, ouverture et
fermeture en douceur, carton final sobre, musique optionnelle.

**Le meuble n'est jamais modifié** : aucune IA ne redessine le produit. Ce que le client voit est exactement la photo.

## Installation sur Mac (une seule fois, gratuit)

```bash
brew install ffmpeg          # si Homebrew n'est pas installé : https://brew.sh
python3 -m pip install pillow
```

## Utilisation

```bash
# Reel Instagram/TikTok de 25 s, 3 à 6 photos conseillées
python3 fony_video.py photo1.jpg photo2.jpg photo3.jpg photo4.jpg \
    --duree 25 --format reel --texte-fin "Fony Meubles" --sous-titre "fonymeubles.fr" \
    --musique musique.mp3 -o canape_reel.mp4

# Version site web / YouTube (16:9)
python3 fony_video.py photo1.jpg photo2.jpg photo3.jpg --duree 20 --format web -o canape_web.mp4
```

| Option | Effet |
|---|---|
| `--format` | `web` 1920×1080, `reel` 1080×1920, `carre` 1080×1080 |
| `--cadrage` | `auto` (défaut), `remplir` (recadre), `complet` (meuble entier sur fond flouté de la même photo) |
| `--texte-fin` / `--sous-titre` | carton final sobre (blanc cassé, texte foncé) |
| `--police` | police de ta charte (.ttf/.otf/.ttc) ; sinon Didot du Mac |
| `--musique` | piste audio ; fondu d'entrée et de sortie automatiques |

## Conseils pour un rendu pro

- **Photos** : nettes, bien éclairées, au moins 2000 px de large. Varier : vue d'ensemble, 3/4, détail matière.
- **Rythme** : 4 à 5 photos pour 25 s (≈ 5 s par plan). Moins de 3 s par plan = trop nerveux, le script refuse.
- **Musique libre de droits** : bibliothèque audio de YouTube Studio ou Pixabay Music. Vérifie la licence de chaque morceau avant publication commerciale.
- Pas besoin de mention « généré par IA » : rien n'est généré, ce sont tes photos montées.
