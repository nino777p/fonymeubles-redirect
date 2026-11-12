#!/usr/bin/env python3
"""Vérifications avant publication du site fony.be (dépôt nino777p.github.io).

Usage :  python3 verifier_site.py /chemin/vers/nino777p.github.io
Lecture seule : ne modifie aucun fichier. Code de sortie 1 s'il y a une ERREUR.

Contrôles :
  - liens internes et images référencées qui n'existent pas ;
  - images du HTML sans width/height (provoquent des sauts de mise en page) ;
  - plus d'une image en fetchpriority="high" par page (ralentit l'affichage sur mobile) ;
  - page .html sans sa version texte .md (utilisée par llms.txt et les assistants IA) ;
  - page publique absente de sitemap.xml ;
  - version du service worker (sw.js) différente de l'empreinte du CSS ;
  - présence d'un prix en euros (le site ne publie aucun prix) ;
  - vidéos sans muted/playsinline/poster.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

PAGES_PRIVEES = {"404.html", "merci.html"}


class Collecte(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.imgs: list[dict] = []
        self.videos: list[dict] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for cle in ("href", "src", "poster"):
            if a.get(cle):
                self.refs.append((tag, a[cle]))
        for cle in ("srcset",):
            if a.get(cle):
                for part in a[cle].split(","):
                    url = part.strip().split(" ")[0]
                    if url:
                        self.refs.append((tag, url))
        if tag == "img":
            self.imgs.append(a)
        if tag == "video":
            self.videos.append(a)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    racine = Path(sys.argv[1]).resolve()
    if not (racine / "index.html").is_file():
        print(f"index.html introuvable dans {racine}")
        return 2

    erreurs, alertes = [], []
    pages = sorted(racine.glob("*.html"))
    sitemap = (racine / "sitemap.xml").read_text(encoding="utf-8") if (racine / "sitemap.xml").exists() else ""

    for page in pages:
        html = page.read_text(encoding="utf-8")
        c = Collecte()
        c.feed(html)
        nom = page.name

        for tag, ref in c.refs:
            u = urlparse(ref)
            if u.scheme or ref.startswith(("//", "mailto:", "tel:", "data:", "#")):
                continue
            chemin = unquote(u.path)
            if not chemin:
                continue
            cible = (racine / chemin.lstrip("/")) if chemin.startswith("/") else (page.parent / chemin)
            if cible.is_dir():
                cible = cible / "index.html"
            if not cible.exists() and not cible.with_suffix(".html").exists():
                erreurs.append(f"{nom} : lien ou fichier introuvable → {ref}")

        hautes = sum(1 for i in c.imgs if i.get("fetchpriority") == "high")
        if hautes > 1:
            alertes.append(f"{nom} : {hautes} images en fetchpriority=high (une seule conseillée : la première visible)")
        for i in c.imgs:
            if not (i.get("width") and i.get("height")):
                alertes.append(f"{nom} : image sans width/height → {i.get('src', '?')}")
        for v in c.videos:
            manque = [k for k in ("muted", "playsinline", "poster") if k not in v]
            if manque:
                erreurs.append(f"{nom} : vidéo sans {', '.join(manque)}")

        if nom not in PAGES_PRIVEES:
            if not page.with_suffix(".md").exists():
                alertes.append(f"{nom} : pas de version texte {page.stem}.md")
            url = "https://fony.be/" if nom == "index.html" else f"https://fony.be/{page.stem}"
            if sitemap and url not in sitemap and f"{url}.html" not in sitemap:
                alertes.append(f"{nom} : absente de sitemap.xml")

        texte = re.sub(r"<[^>]+>", " ", html)
        if re.search(r"\d[\d\s.,]*\s?€|€\s?\d", texte):
            alertes.append(f"{nom} : un montant en € apparaît (le site ne publie aucun prix)")

    sw = racine / "sw.js"
    css = sorted((racine / "assets").glob("site.*.css"))
    if sw.exists() and css:
        empreinte = css[-1].name.split(".")[1]
        if empreinte not in sw.read_text(encoding="utf-8"):
            erreurs.append(f"sw.js : version différente de l'empreinte du CSS ({empreinte}) — le cache des visiteurs ne sera pas renouvelé")

    for e in erreurs:
        print("ERREUR  ", e)
    for a in alertes:
        print("ALERTE  ", a)
    print(f"\n{len(pages)} pages vérifiées — {len(erreurs)} erreur(s), {len(alertes)} alerte(s).")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
