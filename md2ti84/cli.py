"""CLI entry point for md2ti84."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import hdpic_exporter
from .pipeline import RenderOptions, parse_size, render_pages
from .progress import status


def _load_defaults() -> dict:
    """Try to read [tool.md2ti84] from pyproject.toml in the project root."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # fallback
        except ImportError:
            return {}

    here = Path(__file__).parent
    for parent in [here, here.parent, here.parent.parent]:
        candidate = parent / "pyproject.toml"
        if candidate.exists():
            data = tomllib.loads(candidate.read_text(encoding="utf-8"))
            return data.get("tool", {}).get("md2ti84", {})
    return {}


def main(argv: list[str] | None = None) -> int:
    defaults = _load_defaults()

    ap = argparse.ArgumentParser(
        prog="md2ti84",
        description="Convert Markdown notes to HD Picture Viewer .8xv AppVars for TI-84 CE",
    )
    ap.add_argument("input", type=Path, help="Input Markdown file")
    ap.add_argument(
        "-o", "--output-dir", type=Path, default=None,
        help="Output directory (default: same directory as input file)",
    )
    ap.add_argument(
        "--font-size", type=int, default=defaults.get("font_size", 8),
        help="LaTeX font size in pt (default: 8)",
    )
    ap.add_argument(
        "--margin", type=int, default=defaults.get("margin", 6),
        help="Page margin in pt (default: 6)",
    )
    ap.add_argument(
        "--dpi", type=int, default=defaults.get("render_dpi", 300),
        help="DPI for PDF rendering before downscaling (default: 300)",
    )
    ap.add_argument(
        "--engine", default=defaults.get("latex_engine", "lualatex"),
        choices=["lualatex", "pdflatex"],
        help="LaTeX engine (default: lualatex)",
    )
    ap.add_argument(
        "--max-lines", type=float, default=defaults.get("max_lines_per_page", 24.0),
        help="Estimated max lines per page for pagination (default: 24)",
    )
    ap.add_argument(
        "--no-grayscale", action="store_true",
        help="Keep color output instead of the default grayscale",
    )
    ap.add_argument(
        "--no-8xv", action="store_true",
        help="Skip HD Picture Viewer .8xv export, output PNGs only",
    )
    ap.add_argument(
        "--width", type=int, default=defaults.get("image_width", 320),
        help="Output image width in pixels (default: 320)",
    )
    ap.add_argument(
        "--height", type=int, default=defaults.get("image_height", 240),
        help="Output image height in pixels (default: 240)",
    )
    ap.add_argument(
        "--size", default=None,
        help="Physical paper size such as 4x6in or 100x150mm; overrides --width/--height",
    )
    ap.add_argument(
        "--output-dpi", type=int, default=defaults.get("output_dpi", 203),
        help="Printer DPI used to turn --size into pixels (default: 203)",
    )
    ap.add_argument(
        "--bilevel", action="store_true",
        help="Write 1-bit black and white PNGs for thermal printers; implies --no-8xv",
    )
    ap.add_argument(
        "--threshold", type=int, default=defaults.get("threshold", 160),
        help="Gray level at or above which a pixel becomes white with --bilevel (default: 160)",
    )
    ap.add_argument(
        "--clean", action="store_true",
        help="Delete all files in the output directory before running",
    )

    args = ap.parse_args(argv)

    md_file: Path = args.input.resolve()
    if not md_file.exists():
        print(f"[md2ti84] Error: file not found: {md_file}", file=sys.stderr)
        return 1

    try:
        paper = parse_size(args.size) if args.size else None
    except ValueError as error:
        print(f"[md2ti84] Error: {error}", file=sys.stderr)
        return 1

    output_dir: Path = (args.output_dir or md_file.parent).resolve()

    if args.clean and output_dir.exists():
        status(f"Cleaning {output_dir} ...")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"

    options = RenderOptions(
        font_size=args.font_size,
        margin=args.margin,
        render_dpi=args.dpi,
        engine=args.engine,
        max_lines=args.max_lines,
        grayscale=not args.no_grayscale,
        width=args.width,
        height=args.height,
        paper=paper,
        output_dpi=args.output_dpi,
        bilevel=args.bilevel,
        threshold=args.threshold,
    )

    try:
        png_paths = render_pages(md_file, images_dir, options)
    except RuntimeError as error:
        print(f"[md2ti84] Error on {error}", file=sys.stderr)
        return 1

    if not (args.no_8xv or args.bilevel or paper is not None):
        appvar_files = hdpic_exporter.export(png_paths, output_dir, prefix_base=md_file.stem[0].upper())
        if appvar_files:
            status(f"Exported {len(appvar_files)} .8xv AppVar file(s).")

    status(f"Done. {len(png_paths)} PNG(s) written to {images_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
