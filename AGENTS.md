 AGENTS.md

## Objectif du projet
Construire un logiciel desktop simple de vectorisation d’images.
L’utilisateur charge une image PNG/JPG/JPEG/BMP, l’application la convertit en SVG éditable,
puis ce SVG doit pouvoir être ouvert et modifié dans Inkscape, Affinity Designer 2 ou logiciel équivalent.

## Priorité produit
1. Avoir un MVP fonctionnel rapidement.
2. Produire un SVG propre, structuré, et modifiable.
3. Obtenir de bons résultats sur logos, pictogrammes, signatures, dessins simples.
4. Supporter les photos avec un mode simplifié par aplats de couleurs.

## Stack imposée
- Python 3.12
- PySide6 pour l’interface desktop
- OpenCV pour le prétraitement image
- Potrace si disponible pour le mode noir et blanc
- Export SVG natif si Potrace indisponible
- Pas de backend web
- Projet local exécutable dans VS Code

## Fonctionnalités MVP
- Importer une image
- Afficher aperçu avant/après
- Mode noir et blanc :
  - grayscale
  - seuillage manuel + auto
  - suppression du bruit
  - vectorisation
- Mode couleur :
  - réduction du nombre de couleurs
  - extraction des zones par couleur
  - génération d’un SVG avec groupes/layers par couleur
- Réglages utilisateur :
  - threshold
  - nombre de couleurs
  - lissage
  - suppression des petites formes
- Export SVG propre
- Ouvrir automatiquement le dossier d’export
- README d’installation et d’utilisation

## Contraintes techniques
- Architecture claire et modulaire
- Code commenté avec docstrings utiles
- Typage Python quand c’est raisonnable
- Pas de dépendances inutiles
- Écrire des tests unitaires sur les fonctions critiques
- Prévoir des images d’exemple dans un dossier samples/

## Structure souhaitée
- app/
  - main.py
  - ui/
  - core/
  - exporters/
  - utils/
- tests/
- samples/
- requirements.txt
- README.md

## Qualité attendue
Le SVG exporté doit :
- rester lisible
- contenir des paths/groupes cohérents
- éviter les points inutiles quand possible
- être réouvrable et modifiable dans Inkscape

## Méthode de travail
- Travailler par étapes
- Expliquer brièvement les choix techniques
- Après chaque étape importante, résumer les fichiers créés/modifiés
- Ne pas tout faire en une seule fois si le résultat devient fragile