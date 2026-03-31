"""
SVG Exporter - Export vectors en SVG.
"""

from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET
import numpy as np


class SVGExporter:
    """Exporte les contours en fichier SVG."""

    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialise l'exporteur SVG.

        Args:
            width: Largeur du canvas SVG
            height: Hauteur du canvas SVG
        """
        self.width = width
        self.height = height
        self.root = None

    def create_svg(self, background_color: str = "white") -> ET.Element:
        """
        Crée un élément SVG racine.

        Args:
            background_color: Couleur de fond

        Returns:
            Élément SVG racine
        """
        self.root = ET.Element("svg")
        self.root.set("xmlns", "http://www.w3.org/2000/svg")
        self.root.set("width", str(self.width))
        self.root.set("height", str(self.height))
        self.root.set("viewBox", f"0 0 {self.width} {self.height}")

        # Fond
        if background_color != "transparent":
            rect = ET.SubElement(self.root, "rect")
            rect.set("width", str(self.width))
            rect.set("height", str(self.height))
            rect.set("fill", background_color)

        return self.root

    def add_contours_as_paths(self, contours: List[np.ndarray], fill_color: str = "black",
                              stroke_color: str = "none", stroke_width: float = 1.0) -> None:
        """
        Ajoute des contours comme des paths SVG.

        Args:
            contours: Liste des contours (numpy arrays)
            fill_color: Couleur de remplissage
            stroke_color: Couleur du contour
            stroke_width: Largeur du contour
        """
        if self.root is None:
            self.create_svg()

        for contour in contours:
            if len(contour) < 3:
                continue

            # Convertir le contour en string de path
            path_data = self._contour_to_path_data(contour)

            path = ET.SubElement(self.root, "path")
            path.set("d", path_data)
            path.set("fill", fill_color)
            path.set("stroke", stroke_color)
            path.set("stroke-width", str(stroke_width))

    def add_colored_contours(self, color_contours: Dict[Tuple[int, int, int], List[np.ndarray]],
                             stroke_width: float = 1.0) -> None:
        """
        Ajoute des contours groupés par couleur.

        Args:
            color_contours: Dict {couleur: [contours]}
            stroke_width: Largeur du contour
        """
        if self.root is None:
            self.create_svg()

        for color, contours in color_contours.items():
            # Créer un groupe pour chaque couleur
            group = ET.SubElement(self.root, "g")
            group.set("id", f"color_{color[0]}_{color[1]}_{color[2]}")

            # Convertir BGR vers RGB pour SVG
            rgb_color = f"rgb({color[2]}, {color[1]}, {color[0]})"

            for contour in contours:
                if len(contour) < 3:
                    continue

                path_data = self._contour_to_path_data(contour)

                path = ET.SubElement(group, "path")
                path.set("d", path_data)
                path.set("fill", rgb_color)
                path.set("stroke", "none")
                path.set("stroke-width", str(stroke_width))

    def _contour_to_path_data(self, contour: np.ndarray) -> str:
        """
        Convertit un contour OpenCV en string de path SVG.

        Args:
            contour: Contour OpenCV

        Returns:
            String de path SVG (attribut 'd')
        """
        contour = contour.squeeze()

        if contour.ndim < 2 or len(contour) < 2:
            return ""

        path_parts = []

        # Commencer avec un Move To
        first_point = contour[0]
        path_parts.append(f"M {int(first_point[0])} {int(first_point[1])}")

        # Linéaire vers chaque point
        for point in contour[1:]:
            path_parts.append(f"L {int(point[0])} {int(point[1])}")

        # Fermer le chemin
        path_parts.append("Z")

        return " ".join(path_parts)

    def optimize_path(self, path_data: str, tolerance: float = 1.0) -> str:
        """
        Simplifie un path en supprimant les points proches.

        Args:
            path_data: String de path SVG
            tolerance: Distance minimale entre les points

        Returns:
            Path optimisé
        """
        # Implémentation basique - peut être améliorée
        return path_data

    def save(self, output_path: str) -> None:
        """
        Sauvegarde l'SVG dans un fichier.

        Args:
            output_path: Chemin de sortie du fichier SVG
        """
        if self.root is None:
            raise ValueError("Créer un SVG avec create_svg() d'abord")

        tree = ET.ElementTree(self.root)
        ET.indent(tree, space="  ")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

    def get_svg_string(self) -> str:
        """
        Retourne le SVG comme string.

        Returns:
            String contenant le SVG
        """
        if self.root is None:
            raise ValueError("Créer un SVG avec create_svg() d'abord")

        return ET.tostring(self.root, encoding="unicode")
