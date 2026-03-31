"""
Tests unitaires pour le module ColorExtractor.
"""

import unittest
import numpy as np
import os
import tempfile
import cv2

from app.core import ColorExtractor


class TestColorExtractor(unittest.TestCase):
    """Tests du ColorExtractor."""

    @classmethod
    def setUpClass(cls):
        """Crée des images de test avant les tests."""
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        """Nettoie après les tests."""
        import shutil
        shutil.rmtree(cls.temp_dir)

    def test_quantize_colors_normal(self):
        """Test la quantification normale."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        extractor = ColorExtractor(image)
        quantized = extractor.quantize_colors(num_colors=4)
        self.assertEqual(quantized.shape, image.shape)

    def test_quantize_colors_few_unique(self):
        """Test avec peu de couleurs uniques."""
        image = np.zeros((50, 50, 3), dtype=np.uint8)
        image[:25, :] = [255, 0, 0]  # Rouge
        image[25:, :] = [0, 255, 0]  # Vert

        extractor = ColorExtractor(image)
        quantized = extractor.quantize_colors(num_colors=10)  # Plus que disponible
        self.assertEqual(quantized.shape, image.shape)

        # Vérifier que l'extraction fonctionne
        zones = extractor.extract_color_zones()
        self.assertGreater(len(zones), 0)

    def test_quantize_colors_small_image(self):
        """Test avec une petite image."""
        image = np.zeros((5, 5, 3), dtype=np.uint8)
        image[:, :] = [128, 128, 128]

        extractor = ColorExtractor(image)
        quantized = extractor.quantize_colors(num_colors=8)
        self.assertEqual(quantized.shape, image.shape)

    def test_extract_color_zones(self):
        """Test l'extraction des zones par couleur."""
        image = np.zeros((50, 50, 3), dtype=np.uint8)
        image[:25, :] = [255, 0, 0]
        image[25:, :] = [0, 255, 0]

        extractor = ColorExtractor(image)
        extractor.quantize_colors(num_colors=2)
        zones = extractor.extract_color_zones()

        self.assertGreater(len(zones), 0)
        for color, contours in zones.items():
            self.assertGreater(len(contours), 0)  # Au moins un contour par couleur


if __name__ == "__main__":
    unittest.main()