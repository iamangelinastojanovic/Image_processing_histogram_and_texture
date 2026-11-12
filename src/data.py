"""Download MyoAnalyst H&E skeletal-muscle sections."""

from __future__ import annotations

import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ZENODO_URL = "https://zenodo.org/records/14915567/files/HE_input.zip?download=1"
Image.MAX_IMAGE_PIXELS = None


def download_sections(directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    archive = directory / "HE_input.zip"
    if not archive.exists() or archive.stat().st_size < 1_000_000:
        urllib.request.urlretrieve(ZENODO_URL, archive)
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(directory)
    paths = sorted(directory.rglob("*.tif"))
    if len(paths) < 4:
        raise RuntimeError(f"expected 4 H&E sections, found {len(paths)}")
    return paths


def load_brightness(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        gray = image.convert("L")
        return np.asarray(gray, dtype=np.uint8)


def parse_label(path: Path) -> dict[str, str]:
    """Filenames look like '329 ctrl PBS P21 20211216-subset.tif'."""
    parts = path.stem.replace("-", " ").split()
    genotype = "ko" if "ko" in parts else "ctrl"
    treatment = "CTX" if "CTX" in parts else "PBS"
    day = next((part for part in parts if part.startswith("P") and part[1:].isdigit()), "unknown")
    condition = "uninjured" if treatment == "PBS" else "injured"
    return {
        "file": path.name,
        "genotype": genotype,
        "treatment": treatment,
        "day": day,
        "condition": condition,
    }
