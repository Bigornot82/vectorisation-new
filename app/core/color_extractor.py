"""
Color Extractor - Extraction des zones par couleur pour le mode couleur.
"""

from typing import Dict, List, Tuple
import cv2
import numpy as np
from collections import defaultdict


class ColorExtractor:
    """Extrait et regroupe les zones par couleur dans une image."""

    def __init__(self, image: np.ndarray):
        """
        Initialise l'extracteur avec une image.

        Args:
            image: Image numpy (BGR)
        """
        self.image = image
        self.colors: Dict[Tuple[int, int, int], List[np.ndarray]] = defaultdict(list)
        self.quantized_image = None

    def quantize_colors(self, num_colors: int = 8) -> np.ndarray:
        """
        Réduit le nombre de couleurs dans l'image via K-means.

        Args:
            num_colors: Nombre de couleurs cibles

        Returns:
            L'image avec les couleurs quantifiées
        """
        image = self.image.copy()
        h, w = image.shape[:2]
        total_pixels = h * w

        # Cas limite : si l'image est trop petite ou num_colors trop grand
        unique_colors = len(set(tuple(pixel) for pixel in image.reshape(-1, 3)))
        if unique_colors < num_colors:
            num_colors = max(1, unique_colors)
        if total_pixels < num_colors:
            num_colors = max(1, total_pixels // 10)  # Au moins 10 pixels par couleur

        # Redimensionner pour le clustering si nécessaire
        if total_pixels > 100000:
            ratio = np.sqrt(100000 / total_pixels)
            small_h, small_w = int(h * ratio), int(w * ratio)
            small_image = cv2.resize(image, (small_w, small_h))
        else:
            small_image = image

        # Clustering K-means
        data = small_image.reshape(-1, 3).astype(np.float32)
        if len(data) < num_colors:
            num_colors = max(1, len(data))

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(
            data, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )

        # Reconstruire l'image quantifiée
        centers = np.uint8(centers)
        if total_pixels > 100000:
            # Appliquer sur l'image originale via mapping nearest
            small_quantized = centers[labels].reshape(small_h, small_w, 3)
            self.quantized_image = cv2.resize(small_quantized, (w, h), interpolation=cv2.INTER_NEAREST)
        else:
            self.quantized_image = centers[labels].reshape(h, w, 3)

        return self.quantized_image

    def extract_color_zones(self) -> Dict[Tuple[int, int, int], List[np.ndarray]]:
        """
        Extrait les contours pour chaque couleur de l'image quantifiée.

        Returns:
            Dictionnaire {couleur: [contours]}
        """
        if self.quantized_image is None:
            raise ValueError("Appeler quantize_colors() d'abord")

        image = self.quantized_image.copy()
        self.colors.clear()

        # Pour chaque couleur unique
        unique_colors = set()
        for pixel in image.reshape(-1, 3):
            unique_colors.add(tuple(pixel))

        for color in unique_colors:
            # Créer un masque pour cette couleur
            lower = np.array(color, dtype=np.uint8)
            upper = np.array(color, dtype=np.uint8)

            mask = cv2.inRange(image, lower, upper)

            # Trouver les contours
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                self.colors[color] = contours

        return self.colors

    def get_color_contours(self) -> Dict[Tuple[int, int, int], List[np.ndarray]]:
        """Retourne le dictionnaire des couleurs et leurs contours."""
        return self.colors

    def smooth_contours(self, epsilon_factor: float = 0.02) -> Dict[Tuple[int, int, int], List[np.ndarray]]:
        """
        Lisse les contours pour réduire le nombre de points.

        Args:
            epsilon_factor: Facteur d'approximation (0.0-1.0)

        Returns:
            Dictionnaire des contours lissés
        """
        smoothed = {}

        for color, contours in self.colors.items():
            smoothed[color] = []

            for contour in contours:
                if len(contour) < 4:
                    smoothed[color].append(contour)
                    continue

                perimeter = cv2.arcLength(contour, True)
                epsilon = epsilon_factor * perimeter

                approx = cv2.approxPolyDP(contour, epsilon, True)
                smoothed[color].append(approx)

        self.colors = smoothed
        return self.colors

    def filter_small_contours(self, min_area: int = 100) -> None:
        """
        Supprime les contours trop petits.

        Args:
            min_area: Aire minimale des contours à conserver
        """
        filtered = {}

        for color, contours in self.colors.items():
            filtered[color] = [c for c in contours if cv2.contourArea(c) > min_area]

        self.colors = {k: v for k, v in filtered.items() if v}
