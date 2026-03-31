from __future__ import annotations

from pathlib import Path
from typing import Optional

from .geometry import points_to_svg_path
from .models import VectorizationResult


def build_svg_from_result(result: VectorizationResult) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            f'width="{result.width}" height="{result.height}" viewBox="0 0 {result.width} {result.height}">'
        ),
    ]

    for path in result.paths:
        d = points_to_svg_path(path.points)
        if not d:
            continue
        lines.append(
            f'<path d="{d}" fill="{path.fill}" stroke="{path.stroke}" stroke-width="{path.stroke_width}" />'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def save_svg(path: str | Path, result: Optional[VectorizationResult] = None, svg_text: Optional[str] = None) -> None:
    if svg_text is None and result is None:
        raise ValueError("Either result or svg_text must be provided")
    content = svg_text if svg_text is not None else build_svg_from_result(result)
    Path(path).write_text(content, encoding="utf-8")
