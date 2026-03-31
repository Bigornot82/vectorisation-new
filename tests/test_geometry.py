import numpy as np

from vectorizer_desktop.core.geometry import simplify_contour


def test_simplify_contour_returns_polygon_points():
    contour = np.array([[[0, 0]], [[10, 0]], [[10, 10]], [[0, 10]]], dtype=np.int32)
    points = simplify_contour(contour, epsilon_factor=0.01)
    assert len(points) >= 4
    assert points[0] == (0.0, 0.0)
