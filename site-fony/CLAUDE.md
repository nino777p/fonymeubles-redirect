# Site fony.be — consignes pour Claude

À copier à la racine du dépôt `nino777p.github.io`. Claude le lit au début de chaque session.

## Le site

- Site vitrine de **Fony Meubles** (FONY — MEUBLES SRL), magasin de meubles à Leval-Trahegnies (Binche), depuis 1991.
- HTML statique publié par **GitHub Pages** sur le domaine `fony.be` (fichier `CNAME`).
  **Tout ce qui arrive sur `main` est en ligne dans la minute.** Travailler sur une branche, faire valider, puis fusionner.
- `fonymeubles.be` est un autre dépôt (`fonymeubles-redirect`) qui redirige vers `fony.be` : ne rien y changer.

## Règles de contenu

- Français de Belgique, vouvoiement, ton calme et précis : conseil, pas de pression commerciale.
- **Aucun prix publié en ligne.** Ne jamais ajouter de montant, de promotion chiffrée ou d'allégation (matière, dimension, délai) que le magasin n'a pas fournie.
- Les avis clients sont cités tels quels (avec « avis Google »), jamais réécrits ni inventés.
- Marques présentées : Max Divani, Nicoletti, Tomasella, Stosa, Velda, Van Landschoot, Cattelan Italia, Sedit, Akante, Movis, Modulax, Di Lazzaro.

## Fichiers à garder synchronisés

| Quand on modifie… | …il faut aussi mettre à jour |
|---|---|
| le texte d'une page `x.html` | sa version texte `x.md`, et `llms.txt` / `llms-full.txt` si l'information y figure |
| la liste des pages | `sitemap.xml`, la navigation de **toutes** les pages, le pied de page |
| le CSS ou le JS (`assets/site.<empreinte>.css/js`) | le nom de fichier (nouvelle empreinte) dans toutes les pages **et** la version dans `sw.js` |
| les horaires, le téléphone, l'adresse | toutes les pages, les `.md`, `llms*.txt`, et les données structurées JSON-LD |

`campagne.txt` est modifié par nino directement sur GitHub (bandeau et pop-up d'opérations) : ne pas le toucher sans demande explicite.

## Images

- Chaque photo existe en **AVIF + WebP**, en 600 / 900 / 1400 / 2000 px, dans `assets/img/`, avec `srcset`, `sizes`, `width`, `height` et un `alt` descriptif.
- **Une seule image par page en `fetchpriority="high"` et `loading="eager"`** : la première visible. Les autres photos du diaporama d'ouverture sont en `low`/`lazy`.
- Le cadrage se règle avec `object-position` image par image : vérifier sur mobile (iPhone) et ordinateur.

## Vidéos produit

- Faites à partir de vraies photos (dossier `video-produit` du dépôt `fonymeubles-redirect`), jamais de produit modifié par IA.
- Exporter avec `export_web.sh`, intégrer avec le bloc `video-produit` (`muted playsinline loop preload="none"` + `poster`) et le script `90-video.js`.

## Accessibilité et performance (à ne pas dégrader)

- Respecter `prefers-reduced-motion` : aucune animation ni lecture automatique dans ce cas.
- Pas de bibliothèque JavaScript externe ni de police chargée depuis un autre domaine.
- Mesure de référence (12/11/2026, mobile, 4G lente simulée, en local) : LCP entre 0,9 et 2,4 s selon les pages, CLS ≈ 0.

## Avant chaque publication

```bash
python3 ../fonymeubles-redirect/site-fony/verifier_site.py .
```

0 erreur exigée. Puis : relire les pages modifiées sur mobile et ordinateur, et ne fusionner sur `main` qu'avec l'accord de nino.

## Construction du CSS et du JS

Il n'y a pas d'outil de construction séparé : c'est Claude qui maintient les fichiers.
Pour modifier le CSS (même méthode pour le JS) :

1. ajouter les règles à la fin de `assets/site.<empreinte>.css`, dans un bloc commenté `/* NN-nom — explication */` ;
2. calculer la nouvelle empreinte : les 10 premiers caractères du SHA-256 du fichier
   (`python3 -c "import hashlib;print(hashlib.sha256(open('F','rb').read()).hexdigest()[:10])"`) ;
3. renommer le fichier avec cette empreinte et remplacer l'ancienne dans **toutes** les pages `.html` **et** dans `sw.js` ;
4. lancer `verifier_site.py` (il contrôle que `sw.js` suit l'empreinte du CSS).

## Publication

Le dépôt contient un fichier `.nojekyll` : **tout fichier du dépôt est publié sur fony.be**.
Ne pas y mettre de notes internes, de scripts ou de brouillons.
