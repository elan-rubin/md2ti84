"""Render a page's chunks into a complete .tex file using the Jinja2 template."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .renderer import LatexChunk

# Locate the templates directory relative to this file
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )


def build(
    page_chunks: list[LatexChunk],
    *,
    font_size: int = 7,
    image_width: float = 265,
    image_height: float = 165,
    unit: str = "pt",
    margin: int = 4,
    use_lualatex: bool = True,
) -> str:
    """Return a complete LaTeX document string for *page_chunks*."""
    body = "".join(chunk.latex for chunk in page_chunks)
    leading = font_size + 2  # standard leading = font_size + 2pt

    env = _get_env()
    template = env.get_template("base.tex.jinja2")
    return template.render(
        font_size=font_size,
        leading=leading,
        image_width=image_width,
        image_height=image_height,
        unit=unit,
        margin=margin,
        use_lualatex=use_lualatex,
        body=body,
    )
