# Vectorisation Desktop MVP

Application desktop locale (Python + PySide6) pour vectoriser des images raster (`png`, `jpg`, `jpeg`, `bmp`) et exporter un SVG éditable (Inkscape, Illustrator, etc.).

## Fonctionnalités MVP

- Import image raster.
- Prétraitement OpenCV : réduction du bruit + lissage.
- Mode **noir et blanc** :
  - utilise **Potrace** si la commande `potrace` est disponible,
  - sinon fallback interne par extraction/simplification de contours.
- Mode **couleur simplifié** :
  1. réduction du nombre de couleurs (k-means),
  2. masque par couleur,
  3. extraction de contours,
  4. génération de paths SVG groupés par couleur (fill).
- Aperçu source + aperçu vectorisé.
- Réglages UI : threshold, nombre de couleurs, lissage, suppression du bruit.
- Export SVG.

## Architecture

```text
src/vectorizer_desktop/
  core/
    preprocess.py      # OpenCV preprocessing, thresholding, quantization
    geometry.py        # simplification de contours + helpers SVG
    vectorize_bw.py    # mode BW (Potrace + fallback)
    vectorize_color.py # mode couleur simplifié
    pipeline.py        # orchestration de vectorisation
    svg_export.py      # génération/sauvegarde SVG
    models.py          # dataclasses métier
  ui/
    main_window.py     # interface PySide6
  main.py              # point d'entrée app

tests/
  test_preprocess.py
  test_geometry.py
  test_svg_export.py
```

## Prérequis

- Python 3.10+
- (Optionnel mais recommandé pour le mode BW) Potrace installé sur la machine.

### Installer Potrace

- Ubuntu/Debian : `sudo apt install potrace`
- macOS (brew) : `brew install potrace`
- Windows : installer Potrace et ajouter `potrace` au `PATH`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pip install -e .
```

## Lancement

```bash
vectorizer-desktop
```

Alternative :

```bash
python -m vectorizer_desktop.main
```

## Tests

```bash
PYTHONPATH=src pytest -q
```

## Limitations actuelles (MVP)

- Le mode couleur crée des formes par cluster sans hiérarchie avancée (pas d'analyse sémantique des régions).
- Pas de post-traitement géométrique avancé (fusion de paths, élimination de self-intersections).
- UI synchrone (pas de thread séparé pour les grosses images).
- Potrace n'est utilisé que sur le mode BW; pas de chaîne externe avancée pour le mode couleur.

## Améliorations recommandées

1. Ajouter exécution asynchrone (QThread) avec barre de progression.
2. Ajouter simplification adaptative selon la taille de contour.
3. Ajouter options de palette (median-cut, octree, palette custom).
4. Ajouter aperçu superposé (source + vector) et zoom/pan.
5. Ajouter tests d'intégration sur images de référence.
