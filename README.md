# md2ti84

Markdown is parsed, converted to LaTeX, compiled with lualatex, and rendered to grayscale 320x240 `.png` files. Exports to [HD Picture Viewer](https://github.com/TheLastMillennial/HD-Picture-Viewer) `.8xv` AppVar files for transfer to TI-84 CE via TI Connect CE.

## Dependencies

Python packages:

```
pip install -e .
```

Or manually:

```
pip install "markdown-it-py[linkify]" mdit-py-plugins jinja2 pdf2image Pillow imagequant zx0
```

System dependencies (must be installed separately):

- **lualatex** - via [MiKTeX](https://miktex.org/) (Windows) or `texlive-full` (Linux/Mac)
- **poppler** - via [poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) or `poppler-utils` (Linux/Mac)

## Usage

```bash
md2ti84 notes.md -o output/
```

Common options:

- `--engine pdflatex` - use pdflatex instead of lualatex (faster, less complete Unicode)
- `--font-size 6` - smaller font to fit more content per page
- `--no-grayscale` - keep color output (grayscale is the default)
- `--max-lines 28` - adjust pagination threshold
- `--no-8xv` - skip `.8xv` export, output PNGs only
- `--clean` - delete all files in the output directory before running

Output PNGs are placed in `<output>/images/` and named `<stem>_page01.png`, `<stem>_page02.png`, etc. Each page also produces a set of `.8xv` AppVar files (one per 80x80 tile, plus one palette file) directly in the output directory.

## Label and printer output

```bash
md2ti84 board.md -o out/ --size 4x6in --font-size 14 --margin 12 --max-lines 20 --bilevel
```

- `--size 4x6in` (or `100x150mm`) sets the physical paper size; pixels are size times `--output-dpi` (default 203)
- `--bilevel` writes 1-bit PNGs and `--threshold` sets the cutoff
- With `--size` or `--bilevel` the `.8xv` export is skipped

The pipeline is also importable: `from md2ti84.pipeline import RenderOptions, render_pages`.

## Viewing on the calculator

1. Install [HD Picture Viewer](https://github.com/TheLastMillennial/HD-Picture-Viewer) (`HDPICV.8xp`) on your calculator via TI Connect CE
2. Transfer all `.8xv` files from the output directory to the calculator (archive memory)
3. Run the `HDPICV` program on the calculator
4. Select an image from the menu and press `[ENTER]` to view it
5. Use arrow keys to pan, `[+]`/`[-]` to zoom, `[Graph]`/`[Y=]` to go to the next/previous image

## Note

This tool is intended for studying - not for cheating. Don't get me in trouble if you get caught.

## License

MIT License

Copyright 2026