"""Convert a single-page PDF to a resized PNG for the TI-84 CE."""

from __future__ import annotations

from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image


def convert(
    pdf_path: Path,
    output_path: Path,
    *,
    target_width: int = 265,
    target_height: int = 165,
    render_dpi: int = 300,
    grayscale: bool = False,
    bilevel: bool = False,
    threshold: int = 160,
) -> Path:
    """Render *pdf_path* at *render_dpi*, resize to target dimensions, save PNG.

    Returns *output_path*.
    """
    images = convert_from_path(str(pdf_path), dpi=render_dpi)
    if not images:
        raise RuntimeError(f"pdf2image produced no pages for {pdf_path}")

    img: Image.Image = images[0]

    if grayscale or bilevel:
        img = img.convert("L")
    else:
        img = img.convert("RGB")

    img = img.resize((target_width, target_height), Image.LANCZOS)

    if bilevel:
        img = img.point(lambda value: 255 if value >= threshold else 0, mode="1")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), format="PNG")
    return output_path
