# Vectorisation d'Images - MVP

Logiciel desktop simple pour convertir des images PNG/JPG/JPEG/BMP en SVG éditable.

## Fonctionnalités

- **Import d'images** : Charge des images depuis votre disque
- **Prévisualisation** : Voit avant/après le traitement
- **Mode Noir et Blanc** :
  - Conversion en grayscale
  - Seuillage automatique ou manuel
  - Suppression du bruit
  - Vectorisation via Potrace (si disponible) ou algorithme natif
- **Mode Couleur** :
  - Réduction du nombre de couleurs
  - Extraction des zones par couleur
  - Génération SVG avec groupes par couleur
- **Réglages** : Threshold, nombre de couleurs, lissage, suppression des petites formes
- **Export SVG** : Produit un SVG propre et éditable dans Inkscape ou Affinity Designer

## Installation

### Prérequis

- Python 3.12+
- pip

### Étapes d'installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/Bigornot82/vectorisation-new.git
   cd vectorisation-new
   ```

2. **Créer un environnement virtuel** :
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

   **Optionnel - Pour la vectorisation optimale** :
   - Installer Potrace sous Ubuntu/Debian : `sudo apt-get install potrace`
   - Installer Potrace sur macOS : `brew install potrace`
   - Installer Potrace sur Windows : Télécharger depuis http://potrace.sourceforge.net/

## Utilisation

### Lancer l'application

```bash
python -m app.main
```

L'interface graphique s'ouvre et vous permet de :
1. Charger une image
2. Ajuster les paramètres (threshold, couleurs, lissage)
3. Voir l'aperçu
4. Exporter en SVG
5. Ouvrir le dossier de sortie

### Lancer les tests

```bash
python -m pytest tests/ -v
```

## Structure du projet

```
vectorisation-new/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée de l'application
│   ├── ui/
│   │   ├── __init__.py
│   │   └── main_window.py      # Fenêtre principale PySide6
│   ├── core/
│   │   ├── __init__.py
│   │   ├── image_processor.py  # Traitement des images
│   │   └── color_extractor.py  # Extraction des couleurs
│   ├── exporters/
│   │   ├── __init__.py
│   │   └── svg_exporter.py     # Export SVG
│   └── utils/
│       ├── __init__.py
│       └── helpers.py          # Fonctions utilitaires
├── tests/
│   ├── __init__.py
│   └── test_image_processor.py # Tests unitaires
├── samples/                    # Images d'exemple
├── requirements.txt
└── README.md
```

## Développement

### Ajouter une nouvelle fonctionnalité

1. Placez la logique métier dans `app/core/`
2. Exposez-la dans l'UI via `app/ui/main_window.py`
3. Testez avec des tests unitaires dans `tests/`

### Format de sortie SVG

L'application génère un SVG avec :
- **Paths** bien structurés et optimisés
- **Groupes (layers)** organisés par couleur
- **Attributs** clairs et modifiables
- **Compatibilité** avec Inkscape et Affinity Designer

## Limitations actuelles (MVP)

- Pas de support des dégradés
- Optimisation des chemins basique
- Interface simple sans options avancées
- Traitement optimisé pour logos et pictogrammes

## Licence

MIT

## Auteur

Bigornot82