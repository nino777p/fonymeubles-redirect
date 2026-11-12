# Améliorations du site fony.be — 12/11/2026

Préparées depuis une session qui n'a qu'un accès **en lecture** au dépôt du site (`nino777p.github.io`).
Rien n'a été publié. Tout est prêt à être appliqué après validation.

## 1. Espace de travail Claude

| Fichier | Rôle |
|---|---|
| `CLAUDE.md` | Consignes à copier à la racine du dépôt du site : règles de contenu, fichiers à synchroniser, images, publication |
| `verifier_site.py` | Contrôle avant publication (liens cassés, images, version du cache, pages absentes du sitemap, prix en €…). Lecture seule. |

État actuel du site : **0 erreur**, 14 alertes (13 concernent les images prioritaires, corrigées par le patch ci-dessous).
La dernière vient d'un avis client sur `magasin-contact.html` qui cite « un gain de 150 € » : ce n'est pas un prix, à toi de voir si tu le gardes.

## 2. Vitesse réelle (mesure)

Mesure faite **en local** sur une copie du site (fony.be n'est pas joignable depuis cette session), sur un téléphone simulé (Pixel 7) avec une 4G lente (1,6 Mbit/s, 150 ms de latence) et un processeur ralenti ×4.
Il manque donc le temps de réponse réel de GitHub Pages. Les chiffres servent à comparer, pas de valeur absolue.

| Page | Affichage du contenu principal (LCP) | Poids chargé |
|---|---|---|
| Accueil | 1,4 à 1,7 s | 591 Ko |
| Salon | 1,5 s | 444 Ko |
| Salle à manger | **2,4 s** | **902 Ko** |
| Cuisine | 1,3 s | 293 Ko |
| Chambre | 2,0 s | 336 Ko |
| Séjour | 1,2 s | 391 Ko |
| Sur mesure | 2,1 s | 344 Ko |
| Magasin | 0,9 s | 147 Ko |
| Offres | 1,4 s | 273 Ko |
| Tendances | **2,4 s** | 550 Ko |

Seuil « bon » de Google : 2,5 s. **Toutes les pages passent.** Mise en page stable (CLS ≈ 0).

### Correctif proposé : `patches/0001-…patch`

Sur 13 pages, le diaporama d'ouverture chargeait 2 ou 3 photos en priorité maximale alors qu'une seule est visible (la suivante apparaît après 6,5 s).
Le patch garde la priorité sur la première et passe les autres en priorité basse. Aucun changement visuel.

| Page | LCP avant | LCP après |
|---|---|---|
| Accueil | 1,42 s | 1,11 s |
| Salle à manger | 2,38 s | 1,32 s |
| Tendances | 2,37 s | 1,74 s |
| Chambre | 2,01 s | 1,87 s |
| Sur mesure | 2,06 s | 1,79 s |

Une seule mesure par page : l'écart peut varier de quelques centaines de ms d'un essai à l'autre.

Appliquer (dans le dépôt du site) : `git am chemin/vers/0001-…patch`

## 3. Design

Le site est déjà soigné : style éditorial cohérent, cadrage des photos réglé image par image, accessibilité prise en compte (animations réduites, navigation clavier).
**Je ne recommande pas de refonte.** Pistes à valider une par une, sur capture :

1. **Ouverture sur mobile** : la photo est recadrée en hauteur et le titre en couvre le bas. Sur l'accueil, on voit surtout le mur, peu le mobilier. Une image d'ouverture propre au mobile (cadrée sur le meuble) le mettrait en valeur.
2. **Vidéos produit** : c'est le meilleur ajout possible (voir point 4), dans les pages pièces, sous les photos d'ambiance.

## 4. Vidéos produit sur le site

Dossier `video/` :

| Fichier | Rôle |
|---|---|
| `export_web.sh` | Transforme une vidéo de `video-produit` en MP4 léger sans son + image d'aperçu AVIF/WebP |
| `fony-video.css` / `fony-video.js` | Bloc vidéo : lecture en boucle seulement quand elle est à l'écran, pause en dehors, rien n'est téléchargé avant |
| `exemple.html` | Code à coller dans une page |

Testé (navigateur simulé) : la vidéo démarre quand elle est visible et se met en pause quand elle sort de l'écran. Avec « animations réduites », rien ne se lance et un bouton « Lire » s'affiche.
La vidéo de démonstration (20 s, Reel) pèse 259 Ko. Avec de vraies photos, ce sera plus lourd : probablement 1 à 3 Mo (estimation, à mesurer). Elle n'est chargée que si le visiteur arrive jusqu'à elle.

## Pour appliquer le tout

Il faut une session Claude Code ouverte **sur le dépôt `nino777p.github.io`** avec droit d'écriture, ou appliquer toi-même sur ton Mac :

1. Vérifier d'abord où se trouve l'outil qui construit le site (voir la fin de `CLAUDE.md`).
2. Copier `CLAUDE.md` à la racine du dépôt du site.
3. Appliquer le patch sur une branche, relire sur mobile et ordinateur, puis fusionner.
4. Ajouter le module vidéo quand les premières vraies vidéos sont prêtes.
