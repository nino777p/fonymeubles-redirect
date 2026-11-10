# Module Fony Meubles pour OpenMontage

Ce module relie **les deux outils** :

| Qui fait quoi | Outil |
|---|---|
| Animer chaque photo produit **sans jamais modifier le meuble** (mouvements lents, cadrage plein écran ou « galerie » sur fond blanc cassé) | `fony_photo_motion` (notre moteur) |
| Ordre des plans, montage, musique libre de droits, carton final, contrôle qualité automatique | OpenMontage (son agent, Remotion/HyperFrames, FFmpeg) |
| Garde-fous : style pro, zéro IA générative, zéro coût, pas d'allégations inventées | style `fony-meubles` + règle `fony-meubles.md` |

Rien n'est modifié dans OpenMontage : on **ajoute** 4 fichiers (et si un fichier du même nom existe déjà, il est sauvegardé en `.bak`).

## Installation (Mac, une fois)

```bash
brew install ffmpeg                         # si ce n'est pas déjà fait
cd fonymeubles-redirect/openmontage-fony
./installer.sh ~/chemin/vers/OpenMontage    # le dossier qui contient tools/base_tool.py
```

L'installateur vérifie à la fin que l'outil et le style sont bien reconnus par OpenMontage.

## Utilisation : prompt à coller dans Claude Code (dans le dossier OpenMontage)

> Lis d'abord `skills/creative/fony-meubles.md` et applique-le strictement.
> Crée une vidéo produit Fony Meubles de 25 s au format 9:16 à partir UNIQUEMENT des photos du dossier `[chemin/des/photos]`.
> Utilise l'outil `fony_photo_motion` pour chaque plan et le style `fony-meubles`.
> Aucune génération d'image ou de vidéo par IA, aucune API payante.
> Ajoute une musique douce libre de droits avec licence commerciale, et un carton final « Fony Meubles » / « fonymeubles.fr ».
> Montre-moi le storyboard avant le rendu final.

## Licence d'OpenMontage

OpenMontage est sous licence **AGPL-3.0**. L'utiliser et le modifier pour produire tes propres vidéos ne t'impose rien. Les obligations (publier le code source) ne s'appliquent que si tu redistribues OpenMontage modifié ou si tu le proposes comme service en ligne à d'autres personnes.
