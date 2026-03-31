"""
Main Window - Interface graphique PySide6 pour la vectorisation.
"""

import os
from pathlib import Path
from typing import Optional
import cv2
import numpy as np

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QSpinBox, QComboBox,
    QFileDialog, QTabWidget, QScrollArea, QStatusBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage

from ..core import ImageProcessor, ColorExtractor
from ..exporters import SVGExporter
from ..utils import ensure_output_dir, get_unique_filename, open_folder


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application de vectorisation."""

    def __init__(self):
        """Initialise la fenêtre principale."""
        super().__init__()
        self.setWindowTitle("Vectorisation d'Images - MVP")
        self.setGeometry(100, 100, 1200, 800)

        self.image_processor: Optional[ImageProcessor] = None
        self.color_extractor: Optional[ColorExtractor] = None
        self.current_image_path: Optional[str] = None

        self._init_ui()
        self.show()

    def _init_ui(self) -> None:
        """Initialise les éléments de l'interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Panel de controls
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 1)

        # Bouton pour charger l'image
        self.load_btn = QPushButton("Charger une image")
        self.load_btn.clicked.connect(self._load_image)
        left_layout.addWidget(self.load_btn)

        # Affichage du chemin de l'image
        self.image_path_label = QLabel("Aucune image chargée")
        left_layout.addWidget(self.image_path_label)

        # Onglets pour les modes
        self.tabs = QTabWidget()
        left_layout.addWidget(self.tabs)

        # Tab Mode Noir et Blanc
        self._setup_bw_tab()

        # Tab Mode Couleur
        self._setup_color_tab()

        # Boutons d'export
        export_layout = QHBoxLayout()

        self.export_btn = QPushButton("Exporter en SVG")
        self.export_btn.clicked.connect(self._export_svg)
        self.export_btn.setEnabled(False)
        export_layout.addWidget(self.export_btn)

        self.open_folder_btn = QPushButton("Ouvrir dossier de sortie")
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        self.open_folder_btn.setEnabled(False)
        export_layout.addWidget(self.open_folder_btn)

        left_layout.addLayout(export_layout)

        # Panel d'aperçu (droite)
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 1)

        self.preview_label = QLabel("Aperçu")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        self.preview_label.setMinimumSize(400, 600)
        right_layout.addWidget(self.preview_label)

        # Status bar
        self.statusBar().showMessage("Prêt")

    def _setup_bw_tab(self) -> None:
        """Configure l'onglet Mode Noir et Blanc."""
        bw_widget = QWidget()
        bw_layout = QVBoxLayout()

        # Conversion en grayscale
        bw_layout.addWidget(QLabel("Conversion en niveaux de gris"))
        self.bw_grayscale_btn = QPushButton("Appliquer la conversion")
        self.bw_grayscale_btn.clicked.connect(self._apply_grayscale)
        bw_layout.addWidget(self.bw_grayscale_btn)

        # Seuillage
        bw_layout.addWidget(QLabel("Seuillage"))

        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Valeur (0-255):"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setValue(127)
        self.threshold_slider.valueChanged.connect(self._on_threshold_change)
        threshold_layout.addWidget(self.threshold_slider)

        self.threshold_value_label = QLabel("127")
        threshold_layout.addWidget(self.threshold_value_label)
        bw_layout.addLayout(threshold_layout)

        threshold_method_layout = QHBoxLayout()
        threshold_method_layout.addWidget(QLabel("Méthode : "))
        self.threshold_method = QComboBox()
        self.threshold_method.addItems(["Manuel", "Otsu", "Adaptif"])
        threshold_method_layout.addWidget(self.threshold_method)
        bw_layout.addLayout(threshold_method_layout)

        self.bw_threshold_btn = QPushButton("Appliquer le seuillage")
        self.bw_threshold_btn.clicked.connect(self._apply_threshold)
        bw_layout.addWidget(self.bw_threshold_btn)

        # Suppression du bruit
        bw_layout.addWidget(QLabel("Suppression du bruit"))
        self.bw_denoise_btn = QPushButton("Appliquer le filtrage")
        self.bw_denoise_btn.clicked.connect(self._apply_denoise)
        bw_layout.addWidget(self.bw_denoise_btn)

        bw_layout.addStretch()
        bw_widget.setLayout(bw_layout)
        self.tabs.addTab(bw_widget, "Noir & Blanc")

    def _setup_color_tab(self) -> None:
        """Configure l'onglet Mode Couleur."""
        color_widget = QWidget()
        color_layout = QVBoxLayout()

        # Réduction du nombre de couleurs
        color_layout.addWidget(QLabel("Réduction des couleurs"))

        num_colors_layout = QHBoxLayout()
        num_colors_layout.addWidget(QLabel("Nombre de couleurs:"))
        self.num_colors_spinbox = QSpinBox()
        self.num_colors_spinbox.setMinimum(2)
        self.num_colors_spinbox.setMaximum(256)
        self.num_colors_spinbox.setValue(8)
        num_colors_layout.addWidget(self.num_colors_spinbox)
        color_layout.addLayout(num_colors_layout)

        self.color_quantize_btn = QPushButton("Quantifier les couleurs")
        self.color_quantize_btn.clicked.connect(self._apply_color_quantization)
        color_layout.addWidget(self.color_quantize_btn)

        # Extraction des couleurs
        color_layout.addWidget(QLabel("Extraction des zones"))
        self.color_extract_btn = QPushButton("Extraire les contours par couleur")
        self.color_extract_btn.clicked.connect(self._extract_color_zones)
        color_layout.addWidget(self.color_extract_btn)

        # Lissage
        color_layout.addWidget(QLabel("Lissage des contours"))
        smooth_layout = QHBoxLayout()
        smooth_layout.addWidget(QLabel("Facteur:"))
        self.smooth_factor = QSlider(Qt.Horizontal)
        self.smooth_factor.setMinimum(1)
        self.smooth_factor.setMaximum(50)
        self.smooth_factor.setValue(2)
        smooth_layout.addWidget(self.smooth_factor)
        color_layout.addLayout(smooth_layout)

        self.color_smooth_btn = QPushButton("Lisser les contours")
        self.color_smooth_btn.clicked.connect(self._smooth_contours)
        color_layout.addWidget(self.color_smooth_btn)

        color_layout.addStretch()
        color_widget.setLayout(color_layout)
        self.tabs.addTab(color_widget, "Couleur")

    def _load_image(self) -> None:
        """Charge une image depuis le disque."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;Tous les fichiers (*)"
        )

        if not file_path:
            return

        try:
            self.image_processor = ImageProcessor(file_path)
            self.color_extractor = None
            self.current_image_path = file_path

            self.image_path_label.setText(f"Image: {Path(file_path).name}")
            self.statusBar().showMessage(f"Image chargée: {Path(file_path).name}")

            self._update_preview()
            self.export_btn.setEnabled(True)

        except ValueError as e:
            self.statusBar().showMessage(f"Erreur: {e}")

    def _apply_grayscale(self) -> None:
        """Applique la conversion en grayscale."""
        if not self.image_processor:
            return

        self.image_processor.to_grayscale()
        self._update_preview()
        self.statusBar().showMessage("Converted to grayscale")

    def _on_threshold_change(self, value: int) -> None:
        """Met à jour l'affichage du seuil."""
        self.threshold_value_label.setText(str(value))

    def _apply_threshold(self) -> None:
        """Applique le seuillage."""
        if not self.image_processor:
            return

        method_index = self.threshold_method.currentIndex()
        methods = ["binary", "otsu", "adaptive"]
        method = methods[method_index]

        threshold_value = self.threshold_slider.value()

        self.image_processor.apply_threshold(threshold_value, method)
        self._update_preview()
        self.statusBar().showMessage(f"Threshold applied ({method})")

    def _apply_denoise(self) -> None:
        """Applique la suppression du bruit."""
        if not self.image_processor:
            return

        self.image_processor.remove_noise()
        self._update_preview()
        self.statusBar().showMessage("Denoising applied")

    def _apply_color_quantization(self) -> None:
        """Applique la quantification des couleurs."""
        if not self.image_processor:
            return

        num_colors = self.num_colors_spinbox.value()

        self.color_extractor = ColorExtractor(self.image_processor.get_original())
        self.color_extractor.quantize_colors(num_colors)

        # Afficher l'image quantifiée
        quantized = self.color_extractor.quantized_image
        self.image_processor.current_image = cv2.cvtColor(quantized, cv2.COLOR_BGR2RGB)

        self._update_preview()
        self.statusBar().showMessage(f"Color quantization applied ({num_colors} colors)")

    def _extract_color_zones(self) -> None:
        """Extrait les contours par couleur."""
        if not self.color_extractor:
            self.statusBar().showMessage("Appliquer d'abord la quantification des couleurs")
            return

        self.color_extractor.extract_color_zones()
        self.statusBar().showMessage("Color zones extracted")

    def _smooth_contours(self) -> None:
        """Lisse les contours."""
        if not self.color_extractor:
            self.statusBar().showMessage("Pas de contours à lisser")
            return

        epsilon_factor = self.smooth_factor.value() / 100.0
        self.color_extractor.smooth_contours(epsilon_factor)
        self.statusBar().showMessage("Contours smoothed")

    def _update_preview(self) -> None:
        """Met à jour l'aperçu de l'image."""
        if not self.image_processor:
            return

        image = self.image_processor.get_current()

        # Convertir en RGB pour l'affichage
        if len(image.shape) == 2:
            # Grayscale
            rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Redimensionner pour l'aperçu
        h, w = rgb_image.shape[:2]
        max_width, max_height = 350, 550

        if w > max_width or h > max_height:
            ratio = min(max_width / w, max_height / h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            rgb_image = cv2.resize(rgb_image, (new_w, new_h))

        # Convertir en QPixmap
        h, w, ch = rgb_image.shape
        bytes_per_line = 3 * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        self.preview_label.setPixmap(pixmap)

    def _export_svg(self) -> None:
        """Exporte en SVG."""
        if not self.image_processor:
            return

        # Déterminer le répertoire de sortie
        output_dir = ensure_output_dir("output")

        # Déterminer le nom du fichier SVG
        if self.current_image_path:
            base_name = Path(self.current_image_path).stem
            output_file = os.path.join(output_dir, f"{base_name}.svg")
            output_file = get_unique_filename(output_file)
        else:
            output_file = os.path.join(output_dir, "export.svg")

        try:
            # Créer l'exporteur SVG
            image = self.image_processor.get_original()
            h, w = image.shape[:2]

            exporter = SVGExporter(w, h)
            exporter.create_svg("white")

            # Si extraction de couleurs
            if self.color_extractor and self.color_extractor.colors:
                exporter.add_colored_contours(self.color_extractor.colors)
            else:
                # Sinon, extraire les contours de l'image actuelle
                current = self.image_processor.get_current()
                if len(current.shape) == 3:
                    gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
                else:
                    gray = current

                contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                exporter.add_contours_as_paths(contours, fill_color="black")

            # Sauvegarder
            exporter.save(output_file)

            self.statusBar().showMessage(f"SVG exporté: {Path(output_file).name}")
            self.open_folder_btn.setEnabled(True)

        except Exception as e:
            self.statusBar().showMessage(f"Erreur lors de l'export: {e}")

    def _open_output_folder(self) -> None:
        """Ouvre le dossier de sortie."""
        output_dir = ensure_output_dir("output")
        open_folder(output_dir)
