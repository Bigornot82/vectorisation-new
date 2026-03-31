from dataclasses import dataclass
from typing import List, Sequence, Tuple

Point = Tuple[float, float]


@dataclass
class ShapePath:
    points: Sequence[Point]
    fill: str
    stroke: str = "none"
    stroke_width: float = 1.0


@dataclass
class VectorizationResult:
    width: int
    height: int
    paths: List[ShapePath]
