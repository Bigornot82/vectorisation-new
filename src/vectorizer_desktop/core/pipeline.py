from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .models import VectorizationResult
from .preprocess import reduce_noise, smooth_image, to_binary_mask
from .vectorize_bw import vectorize_bw
from .vectorize_color import vectorize_color


@dataclass
class VectorizationSettings:
    mode: str = "bw"  # bw | color
    threshold: int = 128
    n_colors: int = 8
    smoothing: float = 1.0
    noise_reduction: int = 3
    epsilon_factor: float = 0.01


@dataclass
class PipelineOutput:
    result: Optional[VectorizationResult]
    svg_text: Optional[str]


def run_vectorization(image_bgr: np.ndarray, settings: VectorizationSettings) -> PipelineOutput:
    pre = reduce_noise(image_bgr, settings.noise_reduction)
    pre = smooth_image(pre, settings.smoothing)

    if settings.mode == "color":
        result = vectorize_color(
            pre,
            n_colors=settings.n_colors,
            epsilon_factor=settings.epsilon_factor,
        )
        return PipelineOutput(result=result, svg_text=None)

    binary = to_binary_mask(pre, settings.threshold)
    result, svg_text = vectorize_bw(binary, epsilon_factor=settings.epsilon_factor)
    return PipelineOutput(result=result, svg_text=svg_text)
