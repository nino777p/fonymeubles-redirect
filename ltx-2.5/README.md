# LTX-2.5 pour Fony Meubles

Kit pour installer **LTX-2.5** (Lightricks) sur un PC équipé d'une carte graphique NVIDIA et produire des vidéos produit **professionnelles**, qui respectent une charte.

## 1. Audit de sécurité (réalisé le 10/11/2026)

| Élément contrôlé | Résultat |
|---|---|
| Poids du modèle (`Lightricks/LTX-2.5`, révision `49b093a3`) | 17 fichiers : **tous en `.safetensors`**, un format qui ne peut pas exécuter de code. Aucun `.bin`, `.pkl` ni script Python. |
| Code officiel (`github.com/Lightricks/LTX-2`, commit `4f521619`) | Lu sans être exécuté. Pas de code obfusqué (base64, marshal), pas d'envoi de données vers des serveurs inconnus, pas de `eval`/`exec`. Les appels système servent uniquement à compiler des modules GPU NVIDIA (CUTLASS), et ce module n'est pas installé par défaut. |
| Sources des paquets | PyPI, download.pytorch.org et whl.natten.org : des sources officielles. |
| Point d'attention | Le module d'entraînement (`ltx-trainer`) ouvre certains fichiers avec `weights_only=False`, ce qui peut exécuter du code caché dans un fichier piégé. **Le kit ne l'utilise pas.** Ne lui donnez jamais de fichiers `.pt` d'origine inconnue. |

**Limites de cet audit** : c'est une relecture ciblée (recherche de motifs dangereux), pas un audit complet ligne par ligne. Les dépendances tierces (PyTorch, transformers…) n'ont pas été auditées ; ce sont des projets majeurs et très surveillés. `install.sh` bloque les versions du code et des poids sur celles qui ont été auditées, et vérifie après téléchargement qu'il n'y a que des fichiers `.safetensors`.

## 2. Licence : à lire avant de publier

- **Gratuit en usage commercial** si le chiffre d'affaires annuel est **inférieur à 10 M$**. Au-delà, il faut une licence payante.
- **Obligation** : toute publication doit **indiquer clairement que le contenu est généré par IA**. Exemple de mention : « Vidéo générée par IA ».
- Interdit : les deepfakes de personnes réelles, les contenus trompeurs, et la désactivation du filigrane ou des protections du modèle.
- Les vidéos produites vous appartiennent (Lightricks ne revendique aucun droit dessus).
- En acceptant l'accès sur Hugging Face, vous **consentez à recevoir de la publicité ciblée** de Lightricks. Vous pouvez vous désabonner.

Licence complète : https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x

## 3. Matériel nécessaire

- Une **carte NVIDIA** est obligatoire. Comptez **24 Go de mémoire vidéo au minimum** avec l'option `--memoire-limitee` (RTX 4090/5090) ; **48 Go ou plus** pour être à l'aise. Ces chiffres sont une **estimation** : le modèle compte 22 milliards de paramètres, plus un encodeur de texte de 12 milliards, et Lightricks ne publie pas de minimum officiel.
- **90 Go d'espace disque libre**, Linux ou Windows avec WSL2, et Python 3.12 via `uv`.
- **Sans carte adaptée**, mieux vaut louer un GPU à l'heure (RunPod, Vast.ai…) ou passer par la version en ligne (LTX Studio). Le kit fonctionne tel quel sur un GPU loué sous Linux.

## 4. Installation

```bash
hf auth login            # jeton Hugging Face en lecture seule, après avoir accepté les conditions du modèle
./install.sh             # ou WITH_DFR=1 ./install.sh pour ajouter la qualité « production »
```

## 5. Utilisation

```bash
# Simulation (n'affiche que le prompt et la commande) :
python3 fony_ltx.py --produit "a three-seat sofa in light grey boucle fabric with oak legs" --scene salon --camera orbite

# Génération à partir d'une vraie photo du produit (recommandé : le meuble reste fidèle) :
python3 fony_ltx.py --produit "a three-seat sofa in light grey boucle fabric with oak legs" \
    --image photos/canape.jpg --scene salon --camera travelling_avant --format reel_9_16 --run
```

| Option | Choix |
|---|---|
| `--scene` | salon, chambre, salle_a_manger, bureau, studio |
| `--camera` | travelling_avant, travelling_arriere, orbite, lateral, fixe, detail |
| `--format` | web_16_9 (1920×1088), reel_9_16 (1088×1920), carre_1_1, brouillon (rapide) |
| `--qualite` | rapide (par défaut) ou production (plus lent, demande plus de mémoire) |
| `--memoire-limitee` | à utiliser si la carte a moins de 48 Go |

**Méthode conseillée** : faites vos essais en `--format brouillon` et changez de `--seed` jusqu'à obtenir un bon rendu, puis relancez avec le même seed en format final et `--qualite production`.

## 6. Comment la charte est appliquée (`charte_fony.json`)

- **Style imposé** sur chaque vidéo : photoréaliste, lumière naturelle, intérieur épuré, matières fidèles, rythme calme, sans texte, sans logo, sans personne. Fond sonore discret, sans musique ni voix.
- **Mouvements de caméra limités** à 6 mouvements lents et professionnels.
- **Filtre de mots** : le script refuse les termes enfantins ou farfelus (cartoon, mignon, paillettes, néon, « qui danse », morphing…). La liste se modifie dans le JSON.
- **Pas de réécriture automatique** : l'option `--enhance-prompt` du modèle, qui reformule le prompt et peut ajouter des éléments, n'est jamais activée.
- Le mode rapide (« distilled ») **n'accepte pas de prompt négatif**. Le cadrage passe donc par le prompt positif et par le filtre ci-dessus.

**Limite** : une IA peut toujours produire un défaut (pied de meuble déformé, reflet bizarre…). **Vérifiez chaque vidéo avant de la publier.** Partir d'une vraie photo (`--image`) réduit fortement ce risque.
