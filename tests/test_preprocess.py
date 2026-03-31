import numpy as np

from vectorizer_desktop.core.preprocess import quantize_colors, to_binary_mask


def test_to_binary_mask_threshold():
    image = np.zeros((2, 2, 3), dtype=np.uint8)
    image[0, 0] = [255, 255, 255]
    mask = to_binary_mask(image, threshold=127)
    assert mask[0, 0] == 255
    assert mask[1, 1] == 0


def test_quantize_colors_reduces_palette():
    image = np.array(
        [
            [[0, 0, 0], [255, 255, 255]],
            [[0, 0, 255], [0, 255, 0]],
        ],
        dtype=np.uint8,
    )
    reduced, centers = quantize_colors(image, n_colors=2)
    assert reduced.shape == image.shape
    assert len(centers) == 2
