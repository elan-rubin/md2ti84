"""Markdown to page images, independent of the command line and of the TI-84 export."""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from . import compiler, image_converter, latex_builder, paginator, renderer
from . import parser as md_parser
from .progress import status, track

_SIZE_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)(in|mm|cm)$")
_INCHES_PER_UNIT = {"in": 1.0, "mm": 1 / 25.4, "cm": 1 / 2.54}


@dataclass(frozen=True)
class PaperSize:
    width: float
    height: float
    unit: str

    @property
    def width_inches(self) -> float:
        return self.width * _INCHES_PER_UNIT[self.unit]

    @property
    def height_inches(self) -> float:
        return self.height * _INCHES_PER_UNIT[self.unit]

    def pixels(self, dpi: int) -> tuple[int, int]:
        return round(self.width_inches * dpi), round(self.height_inches * dpi)


def parse_size(text: str) -> PaperSize:
    match = _SIZE_PATTERN.match(text.strip().lower())
    if not match:
        raise ValueError(f"invalid size {text!r}, expected e.g. 4x6in, 100x150mm")
    width, height, unit = match.groups()
    return PaperSize(float(width), float(height), unit)


@dataclass(frozen=True)
class RenderOptions:
    font_size: int = 8
    margin: int = 6
    render_dpi: int = 300
    engine: str = "lualatex"
    max_lines: float = 24.0
    grayscale: bool = True
    width: int = 320
    height: int = 240
    paper: PaperSize | None = None
    output_dpi: int = 203
    bilevel: bool = False
    threshold: int = 160

    @property
    def pixel_size(self) -> tuple[int, int]:
        if self.paper is not None:
            return self.paper.pixels(self.output_dpi)
        return self.width, self.height


def render_pages(md_file: Path, images_dir: Path, options: RenderOptions) -> list[Path]:
    images_dir.mkdir(parents=True, exist_ok=True)
    stem = md_file.stem
    pixel_width, pixel_height = options.pixel_size

    status(f"Parsing {md_file.name} ...")
    tokens = md_parser.parse(md_file.read_text(encoding="utf-8"))

    status("Rendering to LaTeX chunks ...")
    chunks = renderer.render(tokens)

    status(f"Paginating (max {options.max_lines} lines/page) ...")
    pages = paginator.paginate(chunks, max_lines=options.max_lines)
    status(f"{len(pages)} page(s) to render.")

    if options.paper is not None:
        page_width, page_height, unit = options.paper.width, options.paper.height, options.paper.unit
    else:
        page_width, page_height, unit = options.width, options.height, "pt"

    png_paths: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="md2ti84_") as tmpdir:
        tmp = Path(tmpdir)
        with track(pages, "Compiling pages") as bar:
            for index, page_chunks in bar:
                page_num = index + 1
                tex_content = latex_builder.build(
                    page_chunks,
                    font_size=options.font_size,
                    image_width=page_width,
                    image_height=page_height,
                    unit=unit,
                    margin=options.margin,
                    use_lualatex=(options.engine == "lualatex"),
                )
                tex_path = tmp / f"{stem}_page{page_num:02d}.tex"
                tex_path.write_text(tex_content, encoding="utf-8")

                try:
                    pdf_path = compiler.compile_tex(tex_path, tmp, engine=options.engine)
                except RuntimeError as error:
                    raise RuntimeError(f"page {page_num}: {error}") from error

                png_path = images_dir / f"{stem}_page{page_num:02d}.png"
                image_converter.convert(
                    pdf_path,
                    png_path,
                    target_width=pixel_width,
                    target_height=pixel_height,
                    render_dpi=options.render_dpi,
                    grayscale=options.grayscale,
                    bilevel=options.bilevel,
                    threshold=options.threshold,
                )
                png_paths.append(png_path)
    return png_paths
