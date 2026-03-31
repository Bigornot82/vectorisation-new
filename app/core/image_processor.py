"""
Image Processor - Traitement des images (grayscale, seuillage, bruit, etc.)
"""

from typing import Tuple, Optional
import cv2
import numpy as np


class ImageProcessor:
    """Traite les images pour la vectorisation."""

    def __init__(self, image_path: str):
        """
        Initialise le processeur avec une image.

        Args:
            image_path: Chemin vers l'image à traiter
        """
        self.image_path = image_path
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Impossible de charger l'image : {image_path}")

        self.current_image = self.original_image.copy()

    def get_original(self) -> np.ndarray:
        """Retourne l'image originale."""
        return self.original_image

    def get_current(self) -> np.ndarray:
        """Retourne l'image actuelle (après traitements)."""
        return self.current_image

    def reset(self) -> None:
        """Réinitialise l'image actuelle à l'originale."""
        self.current_image = self.original_image.copy()

    def to_grayscale(self) -> np.ndarray:
        """
        Convertit l'image actuelle en niveaux de gris.

        Returns:
            L'image en grayscale
        """
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        return self.current_image

    def apply_threshold(self, threshold_value: int = 127, method: str = "binary") -> np.ndarray:
        """
        Applique un seuillage à l'image grayscale.

        Args:
            threshold_value: Valeur du seuil (0-255)
            method: Type de seuillage ("binary", "otsu", "adaptive")

        Returns:
            L'image seuillée
        """
        if len(self.current_image.shape) == 3:
            self.to_grayscale()

        if method == "otsu":
            _, self.current_image = cv2.threshold(
                self.current_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
        elif method == "adaptive":
            self.current_image = cv2.adaptiveThreshold(
                self.current_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
        else:  # binary
            _, self.current_image = cv2.threshold(
                self.current_image, threshold_value, 255, cv2.THRESH_BINARY
            )

        return self.current_image

    def remove_noise(self, kernel_size: int = 5) -> np.ndarray:
        """
        Supprime le bruit en utilisant un filtre morphologique.

        Args:
            kernel_size: Taille du kernel (doit être impair)

        Returns:
            L'image filtrée
        """
        if kernel_size % 2 == 0:
            kernel_size += 1

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        self.current_image = cv2.morphologyEx(self.current_image, cv2.MORPH_CLOSE, kernel)
        self.current_image = cv2.morphologyEx(self.current_image, cv2.MORPH_OPEN, kernel)

        return self.current_image

    def resize(self, width: Optional[int] = None, height: Optional[int] = None) -> np.ndarray:
        """
        Redimensionne l'image en gardant le ratio d'aspect.

        Args:
            width: Largeur cible
            height: Hauteur cible

        Returns:
            L'image redimensionnée
        """
        h, w = self.current_image.shape[:2]

        if width and not height:
            ratio = width / w
            height = int(h * ratio)
        elif height and not width:
            ratio = height / h
            width = int(w * ratio)
        elif not width and not height:
            return self.current_image

        self.current_image = cv2.resize(self.current_image, (width, height))
        return self.current_image

    def get_dominant_colors(self, num_colors: int = 5) -> list:
        """
        Extrait les couleurs dominantes de l'image.

        Args:
            num_colors: Nombre de couleurs à extraire

        Returns:
            Liste des couleurs RGB dominantes
        """
        image = self.original_image.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Redimensionner pour accélérer le clustering
        small = cv2.resize(image, (100, 100))
        data = small.reshape(-1, 3).astype(np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(data, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        colors = centers.astype(int)
        return [tuple(color) for color in colors]

    def apply_bilateral_filter(self, diameter: int = 9, sigma_color: float = 75.0,
                              sigma_space: float = 75.0) -> np.ndarray:
        """
        Applique un filtre bilatéral pour lisser tout en conservant les contours.

        Args:
            diameter: Diamètre du pixel voisinage
            sigma_color: Filtre sigma dans l'espace de couleur
            sigma_space: Filtre sigma dans l'espace de coordonnées

        Returns:
            L'image filtrée
        """
        if len(self.current_image.shape) == 2:
            # Image en niveaux de gris
            self.current_image = cv2.bilateralFilter(
                self.current_image, diameter, sigma_color, sigma_space
            )
        else:
            # Image en couleur
            self.current_image = cv2.bilateralFilter(
                self.current_image, diameter, sigma_color, sigma_space
            )

        return self.current_image

    def get_contours(self, min_area: int = 50) -> Tuple[list, np.ndarray]:
        """
        Extrait les contours de l'image seuillée.

        Args:
            min_area: Aire minimale des contours à conserver

        Returns:
            Tuple (contours, image_with_contours)
        """
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image

        contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Filtrer par aire minimale
        filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]

        # Créer une image avec les contours
        image_with_contours = self.current_image.copy()
        cv2.drawContours(image_with_contours, filtered_contours, -1, (0, 255, 0), 2)

        return filtered_contours, image_with_contours
