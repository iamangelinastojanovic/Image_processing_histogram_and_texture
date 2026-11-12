"""Compare brightness texture of uninjured and injured H&E muscle sections."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.data import download_sections, load_brightness, parse_label
from src.texture import describe, tissue_mask

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
PATCH = 512
STRIDE = 512
FEATURES = ("mean", "variance", "skewness", "uniformity", "entropy", "contrast", "homogeneity", "energy", "correlation")


def image_patches(gray: np.ndarray) -> list[np.ndarray]:
    height, width = gray.shape
    return [
        gray[y : y + PATCH, x : x + PATCH]
        for y in range(0, height - PATCH + 1, STRIDE)
        for x in range(0, width - PATCH + 1, STRIDE)
    ]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"no rows for {path.name}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    section_rows = []
    patch_rows = []
    preview = None

    for path in download_sections(DATA):
        label = parse_label(path)
        gray = load_brightness(path)
        mask = tissue_mask(gray)
        # Sections fill the frame, so Otsu splits fiber interiors from dark
        # boundaries instead of removing slide glass. Descriptors use every pixel.
        features = describe(gray)
        section_rows.append({**label, "scope": "section", **{key: f"{features[key]:.6f}" for key in FEATURES}, "n_pixels": features["n_pixels"]})
        for tissue in image_patches(gray):
            patch_features = describe(tissue)
            patch_rows.append({**label, "scope": "patch", **{key: f"{patch_features[key]:.6f}" for key in FEATURES}, "n_pixels": patch_features["n_pixels"]})
        if label["treatment"] == "PBS":
            preview = (gray, mask, label["file"])
        print(f"{label['file']}: {label['condition']} {label['genotype']} {label['day']}  entropy {features['entropy']:.3f}  patches {sum(1 for row in patch_rows if row['file'] == label['file'])}")

    write_csv(RESULTS / "sections.csv", section_rows)
    write_csv(RESULTS / "patches.csv", patch_rows)
    group_summary = summarize_patches(patch_rows)
    (RESULTS / "summary.json").write_text(json.dumps(group_summary, indent=2), encoding="utf-8")
    if preview is not None:
        save_preview(*preview)
    save_feature_plot(patch_rows)
    for condition, stats in group_summary.items():
        print(condition, {key: round(stats[key]["mean"], 3) for key in FEATURES}, "n_patches", stats["n_patches"])


def summarize_patches(rows: list[dict]) -> dict:
    summary = {}
    for condition in ("uninjured", "injured"):
        selected = [row for row in rows if row["condition"] == condition]
        summary[condition] = {"n_patches": len(selected), "n_sections": len({row["file"] for row in selected})}
        for key in FEATURES:
            values = np.array([float(row[key]) for row in selected], dtype=np.float64)
            summary[condition][key] = {"mean": float(values.mean()), "std": float(values.std(ddof=0))}
    return summary


def save_preview(gray: np.ndarray, mask: np.ndarray, name: str) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].imshow(gray, cmap="gray")
    axes[0].set_title(name, fontsize=8)
    axes[1].imshow(mask, cmap="gray")
    axes[1].set_title("Otsu tissue mask")
    for axis in axes:
        axis.axis("off")
    figure.tight_layout()
    figure.savefig(RESULTS / "tissue_mask_preview.png", dpi=140)
    plt.close(figure)


def save_feature_plot(rows: list[dict]) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(8, 4))
    for axis, key in zip(axes, ("entropy", "contrast")):
        for condition, color in (("uninjured", "#2a9d8f"), ("injured", "#e76f51")):
            values = [float(row[key]) for row in rows if row["condition"] == condition]
            axis.hist(values, bins=20, alpha=0.7, label=condition, color=color)
        axis.set_title(f"Patch {key}")
        axis.legend(frameon=False)
    figure.tight_layout()
    figure.savefig(RESULTS / "patch_histograms.png", dpi=140)
    plt.close(figure)


if __name__ == "__main__":
    main()
