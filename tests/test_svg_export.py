from vectorizer_desktop.core.models import ShapePath, VectorizationResult
from vectorizer_desktop.core.svg_export import build_svg_from_result


def test_build_svg_contains_path():
    result = VectorizationResult(
        width=100,
        height=100,
        paths=[ShapePath(points=[(0, 0), (50, 0), (50, 50)], fill="#ff0000")],
    )
    svg = build_svg_from_result(result)
    assert "<svg" in svg
    assert "<path" in svg
    assert "#ff0000" in svg
