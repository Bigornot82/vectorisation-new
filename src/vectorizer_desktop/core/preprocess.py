from __future__ import annotations

import cv2
import numpy as np


def load_image(path: str) -> np.ndarray:
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Impossible de lire l'image: {path}")
    return image


def reduce_noise(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    k = max(1, int(kernel_size))
    if k % 2 == 0:
        k += 1
    return cv2.medianBlur(image, k)


def smooth_image(image: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    sigma = max(float(sigma), 0.0)
    if sigma == 0:
        return image
    return cv2.GaussianBlur(image, (0, 0), sigmaX=sigma, sigmaY=sigma)


def to_binary_mask(image: np.ndarray, threshold: int = 128) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, int(threshold), 255, cv2.THRESH_BINARY)
    return binary


def quantize_colors(image: np.ndarray, n_colors: int = 8) -> tuple[np.ndarray, np.ndarray]:
    n_colors = max(2, int(n_colors))
    pixels = image.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.2)
    _, labels, centers = cv2.kmeans(
        pixels,
        n_colors,
        None,
        criteria,
        3,
        cv2.KMEANS_PP_CENTERS,
    )
    centers_u8 = centers.astype(np.uint8)
    reduced = centers_u8[labels.flatten()].reshape(image.shape)
    return reduced, centers_u8
