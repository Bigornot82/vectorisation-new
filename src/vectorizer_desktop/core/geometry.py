from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

import cv2
import numpy as np

Point = Tuple[float, float]


def simplify_contour(contour: np.ndarray, epsilon_factor: float = 0.01) -> List[Point]:
    """Simplify an OpenCV contour into SVG-friendly points."""
    if contour is None or len(contour) < 3:
        return []

    arc_len = cv2.arcLength(contour, True)
    epsilon = max(arc_len * float(epsilon_factor), 0.5)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    return [(float(p[0][0]), float(p[0][1])) for p in approx]


def points_to_svg_path(points: Sequence[Point]) -> str:
    if not points:
        return ""
    head = f"M {points[0][0]:.2f},{points[0][1]:.2f}"
    rest = " ".join(f"L {x:.2f},{y:.2f}" for x, y in points[1:])
    if rest:
        return f"{head} {rest} Z"
    return f"{head} Z"


def rgb_to_hex(rgb: Iterable[int]) -> str:
    r, g, b = [int(v) for v in rgb]
    return f"#{r:02x}{g:02x}{b:02x}"
