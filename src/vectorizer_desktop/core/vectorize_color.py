from __future__ import annotations

import cv2
import numpy as np

from .geometry import rgb_to_hex, simplify_contour
from .models import ShapePath, VectorizationResult
from .preprocess import quantize_colors


def vectorize_color(
    image_bgr: np.ndarray,
    n_colors: int = 8,
    epsilon_factor: float = 0.01,
    min_area: float = 20.0,
) -> VectorizationResult:
    reduced_bgr, centers_bgr = quantize_colors(image_bgr, n_colors=n_colors)
    h, w = image_bgr.shape[:2]

    paths = []
    for color in centers_bgr:
        mask = cv2.inRange(reduced_bgr, color, color)
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        rgb = (int(color[2]), int(color[1]), int(color[0]))
        fill = rgb_to_hex(rgb)
        for contour in contours:
            if cv2.contourArea(contour) < min_area:
                continue
            points = simplify_contour(contour, epsilon_factor=epsilon_factor)
            if len(points) < 3:
                continue
            paths.append(ShapePath(points=points, fill=fill))

    return VectorizationResult(width=w, height=h, paths=paths)
