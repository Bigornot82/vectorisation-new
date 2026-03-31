from __future__ import annotations

from pathlib import Path

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from vectorizer_desktop.core.pipeline import VectorizationSettings, run_vectorization
from vectorizer_desktop.core.svg_export import build_svg_from_result, save_svg


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Vectorisation MVP")
        self.resize(1200, 700)

        self.image_bgr = None
        self.last_svg_text: str | None = None

        self.import_btn = QPushButton("Importer image")
        self.vectorize_btn = QPushButton("Vectoriser")
        self.export_btn = QPushButton("Exporter SVG")

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["bw", "color"])

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(128)

        self.colors_spin = QSpinBox()
        self.colors_spin.setRange(2, 32)
        self.colors_spin.setValue(8)

        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setRange(0, 50)
        self.smoothing_slider.setValue(10)

        self.noise_spin = QSpinBox()
        self.noise_spin.setRange(1, 9)
        self.noise_spin.setSingleStep(2)
        self.noise_spin.setValue(3)

        self.source_label = QLabel("Aperçu source")
        self.source_label.setAlignment(Qt.AlignCenter)
        self.source_label.setMinimumSize(480, 480)
        self.source_label.setStyleSheet("border: 1px solid #888;")

        self.vector_label = QLabel("Aperçu vectorisé")
        self.vector_label.setAlignment(Qt.AlignCenter)
        self.vector_label.setMinimumSize(480, 480)
        self.vector_label.setStyleSheet("border: 1px solid #888;")

        form = QFormLayout()
        form.addRow("Mode", self.mode_combo)
        form.addRow("Threshold", self.threshold_slider)
        form.addRow("Nombre de couleurs", self.colors_spin)
        form.addRow("Lissage", self.smoothing_slider)
        form.addRow("Suppression bruit", self.noise_spin)

        controls = QVBoxLayout()
        controls.addWidget(self.import_btn)
        controls.addLayout(form)
        controls.addWidget(self.vectorize_btn)
        controls.addWidget(self.export_btn)
        controls.addStretch()

        previews = QHBoxLayout()
        previews.addWidget(self.source_label)
        previews.addWidget(self.vector_label)

        root = QHBoxLayout()
        root.addLayout(controls, 1)
        root.addLayout(previews, 3)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self.import_btn.clicked.connect(self.import_image)
        self.vectorize_btn.clicked.connect(self.vectorize)
        self.export_btn.clicked.connect(self.export_svg)

    def import_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not file_path:
            return
        image = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if image is None:
            QMessageBox.critical(self, "Erreur", "Impossible de lire l'image.")
            return

        self.image_bgr = image
        self.last_svg_text = None
        self.source_label.setPixmap(self._bgr_to_pixmap(image, self.source_label.size()))
        self.vector_label.setText("Aperçu vectorisé")

    def vectorize(self) -> None:
        if self.image_bgr is None:
            QMessageBox.information(self, "Info", "Importez d'abord une image.")
            return

        settings = VectorizationSettings(
            mode=self.mode_combo.currentText(),
            threshold=self.threshold_slider.value(),
            n_colors=self.colors_spin.value(),
            smoothing=self.smoothing_slider.value() / 10.0,
            noise_reduction=self.noise_spin.value(),
            epsilon_factor=0.01,
        )

        output = run_vectorization(self.image_bgr, settings)
        if output.svg_text:
            svg_text = output.svg_text
        else:
            svg_text = build_svg_from_result(output.result)

        self.last_svg_text = svg_text
        pixmap = self._svg_to_pixmap(svg_text, self.vector_label.size())
        if pixmap is None:
            self.vector_label.setText("Vectorisation OK, aperçu indisponible")
        else:
            self.vector_label.setPixmap(pixmap)

    def export_svg(self) -> None:
        if not self.last_svg_text:
            QMessageBox.information(self, "Info", "Lancez la vectorisation avant l'export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter SVG", "output.svg", "SVG (*.svg)")
        if not file_path:
            return

        out_path = Path(file_path)
        if out_path.suffix.lower() != ".svg":
            out_path = out_path.with_suffix(".svg")

        save_svg(out_path, svg_text=self.last_svg_text)
        QMessageBox.information(self, "Succès", f"SVG exporté: {out_path}")

    @staticmethod
    def _bgr_to_pixmap(image_bgr, target_size) -> QPixmap:
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        qimage = QImage(rgb.data, w, h, rgb.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    @staticmethod
    def _svg_to_pixmap(svg_text: str, target_size) -> QPixmap | None:
        renderer = QSvgRenderer(svg_text.encode("utf-8"))
        if not renderer.isValid():
            return None
        image = QImage(target_size, QImage.Format_ARGB32)
        image.fill(Qt.white)
        painter = None
        try:
            from PySide6.QtGui import QPainter

            painter = QPainter(image)
            renderer.render(painter)
        finally:
            if painter is not None:
                painter.end()
        return QPixmap.fromImage(image)
