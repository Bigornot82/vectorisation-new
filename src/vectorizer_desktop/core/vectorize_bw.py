from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from .geometry import points_to_svg_path, simplify_contour
from .models import ShapePath, VectorizationResult


def potrace_available() -> bool:
    return shutil.which("potrace") is not None


def vectorize_bw_with_potrace(binary_mask: np.ndarray) -> Optional[str]:
    """Return SVG text produced by potrace, or None if unavailable/failure."""
    if not potrace_available():
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        pbm_path = Path(tmpdir) / "input.pbm"
        out_path = Path(tmpdir) / "output.svg"
        cv2.imwrite(str(pbm_path), binary_mask)
        cmd = ["potrace", str(pbm_path), "-s", "-o", str(out_path)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return out_path.read_text(encoding="utf-8")
        except Exception:
            return None


def vectorize_bw_fallback(binary_mask: np.ndarray, epsilon_factor: float = 0.01) -> VectorizationResult:
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    paths = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 16:
            continue
        points = simplify_contour(contour, epsilon_factor=epsilon_factor)
        d = points_to_svg_path(points)
        if not d:
            continue
        paths.append(ShapePath(points=points, fill="#000000"))

    h, w = binary_mask.shape[:2]
    return VectorizationResult(width=w, height=h, paths=paths)


def vectorize_bw(binary_mask: np.ndarray, epsilon_factor: float = 0.01) -> Tuple[Optional[VectorizationResult], Optional[str]]:
    svg = vectorize_bw_with_potrace(binary_mask)
    if svg:
        return None, svg
    return vectorize_bw_fallback(binary_mask, epsilon_factor=epsilon_factor), None
