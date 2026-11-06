import shutil
from pathlib import Path

import pytest
from PIL import Image

from md2ti84.cli import main
from md2ti84.pipeline import PaperSize, RenderOptions, parse_size

FIXTURE = Path(__file__).parent / "fixtures" / "sample.md"


def test_parse_size_inches():
    assert parse_size("4x6in") == PaperSize(4.0, 6.0, "in")


def test_parse_size_millimetres_to_pixels():
    assert parse_size("100x150mm").pixels(203) == (799, 1199)


def test_parse_size_rejects_garbage():
    with pytest.raises(ValueError):
        parse_size("4 by 6")


def test_pixel_size_prefers_paper():
    options = RenderOptions(paper=parse_size("4x6in"), output_dpi=203)
    assert options.pixel_size == (812, 1218)


def test_pixel_size_defaults_to_ti84():
    assert RenderOptions().pixel_size == (320, 240)


@pytest.mark.skipif(
    shutil.which("lualatex") is None or shutil.which("pdftoppm") is None,
    reason="needs lualatex and poppler",
)
def test_label_render_is_one_bit_and_exact_size(tmp_path):
    code = main(
        [
            str(FIXTURE),
            "-o", str(tmp_path),
            "--size", "4x6in",
            "--font-size", "14",
            "--margin", "12",
            "--max-lines", "20",
            "--bilevel",
        ]
    )
    assert code == 0
    pages = sorted((tmp_path / "images").glob("*.png"))
    assert pages
    with Image.open(pages[0]) as image:
        assert image.mode == "1"
        assert image.size == (812, 1218)
    assert not list(tmp_path.glob("*.8xv"))
