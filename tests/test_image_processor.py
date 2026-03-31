"""
Tests unitaires pour le module ImageProcessor.
"""

import unittest
import numpy as np
import os
import tempfile
import cv2

from app.core import ImageProcessor


class TestImageProcessor(unittest.TestCase):
    """Tests du ImageProcessor."""

    @classmethod
    def setUpClass(cls):
        """Crée une image de test avant les tests."""
        # Créer une image de test temporaire
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_image_path = os.path.join(cls.temp_dir, "test.png")

        # Créer une image simple (200x200 avec un gradient)
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        for i in range(200):
            image[i, :] = [i, i, i]  # Gradient de gris

        cv2.imwrite(cls.test_image_path, image)

    @classmethod
    def tearDownClass(cls):
        """Nettoie après les tests."""
        import shutil
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        """Initialise un ImageProcessor avant chaque test."""
        self.processor = ImageProcessor(self.test_image_path)

    def test_initialization(self):
        """Test l'initialisation du processeur."""
        self.assertIsNotNone(self.processor.original_image)
        self.assertIsNotNone(self.processor.current_image)
        self.assertEqual(self.processor.original_image.shape, (200, 200, 3))

    def test_to_grayscale(self):
        """Test la conversion en grayscale."""
        result = self.processor.to_grayscale()
        self.assertEqual(len(result.shape), 2)
        self.assertEqual(result.shape, (200, 200))

    def test_apply_threshold(self):
        """Test l'application du seuillage."""
        self.processor.to_grayscale()
        result = self.processor.apply_threshold(127, "binary")

        self.assertEqual(len(result.shape), 2)
        # Vérifier que l'image contient seulement 0 et 255
        unique_values = np.unique(result)
        self.assertTrue(all(v in [0, 255] for v in unique_values))

    def test_reset(self):
        """Test la réinitialisation."""
        self.processor.to_grayscale()
        self.processor.reset()

        # L'image actuelle doit être à nouveau en couleur
        self.assertEqual(len(self.processor.current_image.shape), 3)

    def test_resize(self):
        """Test le redimensionnement."""
        original_h, original_w = self.processor.current_image.shape[:2]

        self.processor.resize(width=100)
        new_h, new_w = self.processor.current_image.shape[:2]

        self.assertEqual(new_w, 100)
        # Vérifier que le ratio aspect est conservé
        self.assertAlmostEqual(new_h / new_w, original_h / original_w, places=0)

    def test_get_dominant_colors(self):
        """Test l'extraction des couleurs dominantes."""
        colors = self.processor.get_dominant_colors(num_colors=5)

        self.assertEqual(len(colors), 5)
        # Vérifier que ce sont des tuples RGB
        for color in colors:
            self.assertEqual(len(color), 3)
            self.assertTrue(all(0 <= c <= 255 for c in color))

    def test_remove_noise(self):
        """Test la suppression du bruit."""
        # Créer une image avec du bruit
        self.processor.to_grayscale()
        noisy = self.processor.current_image.copy()
        noisy[50:60, 50:60] = 0  # Ajouter du bruit blanc

        result = self.processor.remove_noise()

        # L'image ne devrait pas être identique à l'originale
        self.assertFalse(np.array_equal(result, noisy))

    def test_small_image_handling(self):
        """Test la gestion des petites images."""
        # Créer une petite image
        small_image = np.zeros((10, 10, 3), dtype=np.uint8)
        small_image[:, :] = [255, 0, 0]  # Rouge

        small_path = os.path.join(self.temp_dir, "small.png")
        cv2.imwrite(small_path, small_image)

        processor = ImageProcessor(small_path)
        self.assertEqual(processor.original_image.shape, (10, 10, 3))

        # Test get_dominant_colors avec petite image
        colors = processor.get_dominant_colors(num_colors=5)
        self.assertGreater(len(colors), 0)
        self.assertLessEqual(len(colors), 5)

    def test_very_small_image(self):
        """Test avec une image très petite (1x1)."""
        tiny_image = np.zeros((1, 1, 3), dtype=np.uint8)
        tiny_image[0, 0] = [128, 128, 128]

        tiny_path = os.path.join(self.temp_dir, "tiny.png")
        cv2.imwrite(tiny_path, tiny_image)

        processor = ImageProcessor(tiny_path)
        self.assertEqual(processor.original_image.shape, (1, 1, 3))

        # Test get_dominant_colors
        colors = processor.get_dominant_colors(num_colors=1)
        self.assertEqual(len(colors), 1)

    def test_few_colors_quantization(self):
        """Test la quantification avec peu de couleurs."""
        # Image avec seulement 2 couleurs
        two_color_image = np.zeros((50, 50, 3), dtype=np.uint8)
        two_color_image[:25, :] = [255, 0, 0]  # Rouge
        two_color_image[25:, :] = [0, 255, 0]  # Vert

        two_color_path = os.path.join(self.temp_dir, "two_colors.png")
        cv2.imwrite(two_color_path, two_color_image)

        processor = ImageProcessor(two_color_path)
        colors = processor.get_dominant_colors(num_colors=10)  # Demander plus que disponible
        self.assertGreater(len(colors), 0)
        self.assertLessEqual(len(colors), 2)  # Ne devrait pas dépasser le nombre réel


if __name__ == "__main__":
    unittest.main()
