"""First-order brightness texture measures and an Otsu tissue mask."""

from __future__ import annotations

import numpy as np

Array = np.ndarray


def histogram_features(values: Array) -> dict[str, float]:
    """Moments, uniformity and entropy of an 8-bit brightness sample.

    Definitions follow Gonzalez and Woods: the histogram is treated as a
    probability mass function over gray levels 0..255.
    """
    values = np.asarray(values, dtype=np.uint8).ravel()
    if values.size == 0:
        raise ValueError("no pixels")
    counts = np.bincount(values, minlength=256).astype(np.float64)
    probability = counts / counts.sum()
    levels = np.arange(256, dtype=np.float64)
    mean = float(np.sum(levels * probability))
    centered = levels - mean
    variance = float(np.sum((centered ** 2) * probability))
    std = variance ** 0.5
    third = float(np.sum((centered ** 3) * probability))
    skewness = float(third / (std ** 3)) if std > 1e-8 else 0.0
    positive = probability[probability > 0]
    return {
        "mean": mean,
        "variance": variance,
        "skewness": skewness,
        "uniformity": float(np.sum(probability ** 2)),
        "entropy": float(-np.sum(positive * np.log2(positive))),
        "n_pixels": int(values.size),
    }


def glcm_features(image: Array, levels: int = 32) -> dict[str, float]:
    """Haralick features from a symmetric gray-level co-occurrence matrix.

    Pairs are horizontal and vertical neighbors at distance 1. Brightness is
    quantized to `levels` bins so a full section stays comparable to a patch.
    """
    image = np.asarray(image)
    if image.ndim != 2:
        raise ValueError("GLCM needs a 2-D image")
    quantized = np.clip((image.astype(np.uint16) * levels) // 256, 0, levels - 1)
    accumulated = np.zeros((levels, levels), dtype=np.float64)
    pairs = ((quantized[:, :-1], quantized[:, 1:]), (quantized[:-1, :], quantized[1:, :]))
    for left, right in pairs:
        index = left.ravel().astype(np.int64) * levels + right.ravel().astype(np.int64)
        accumulated += np.bincount(index, minlength=levels * levels).reshape(levels, levels)
    accumulated += accumulated.T
    probability = accumulated / accumulated.sum()
    grid = np.arange(levels, dtype=np.float64)
    rows, cols = np.meshgrid(grid, grid, indexing="ij")
    squared_diff = (rows - cols) ** 2
    mean = float(np.sum(rows * probability))
    variance = float(np.sum((rows - mean) ** 2 * probability))
    if variance <= 1e-12:
        correlation = 0.0
    else:
        correlation = float(np.sum((rows - mean) * (cols - mean) * probability) / variance)
    return {
        "contrast": float(np.sum(squared_diff * probability)),
        "homogeneity": float(np.sum(probability / (1.0 + squared_diff))),
        "energy": float(np.sum(probability ** 2)),
        "correlation": correlation,
    }


def describe(image: Array) -> dict[str, float]:
    features = histogram_features(image)
    features.update(glcm_features(image))
    return features


def otsu_threshold(gray: Array) -> int:
    gray = np.asarray(gray, dtype=np.uint8)
    counts = np.bincount(gray.ravel(), minlength=256).astype(np.float64)
    probability = counts / counts.sum()
    omega = np.cumsum(probability)
    mu = np.cumsum(probability * np.arange(256))
    mu_total = mu[-1]
    between = (mu_total * omega - mu) ** 2 / (omega * (1.0 - omega) + 1e-12)
    between[~np.isfinite(between)] = 0
    return int(np.argmax(between))


def tissue_mask(gray: Array) -> Array:
    """Keep the darker class. H&E tissue is darker than the slide background."""
    threshold = otsu_threshold(gray)
    dark = gray < threshold
    if dark.mean() < 0.05 or dark.mean() > 0.95:
        return gray < np.percentile(gray, 90)
    return dark
