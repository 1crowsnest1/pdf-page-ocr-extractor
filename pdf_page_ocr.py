#!/usr/bin/env python3
"""
PDF Page OCR Extractor
============
Extract every page of a PDF as:

* a PNG image of the page, and
* a plain-text file containing the page's text

Digital text is taken from the PDF itself.  When a page has little or no
extractable text (typical of scans) the tool falls back to Tesseract OCR
if it is installed.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pymupdf as fitz

try:
    import pytesseract
    from PIL import Image
    import io
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


DEFAULT_INPUT = "./pdfs"
DEFAULT_OUTPUT = "./pages_ocr"
DEFAULT_DPI = 200
TEXT_THRESHOLD = 40  # chars; below this we try OCR


def ocr_pixmap(pix: fitz.Pixmap) -> str:
    """Run Tesseract on a pixmap; return empty string if unavailable."""
    if not HAS_TESSERACT:
        return ""
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    try:
        return pytesseract.image_to_string(img) or ""
    except Exception:
        return ""


def process_pdf(
    pdf_path: Path,
    out_root: Path,
    dpi: int,
    force_ocr: bool,
) -> int:
    stem = pdf_path.stem
    dest = out_root / stem
    dest.mkdir(parents=True, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        print(f"  ERROR opening {pdf_path.name}: {exc}")
        return 0

    pages_done = 0
    for i in range(len(doc)):
        page = doc[i]
        page_no = i + 1

        # --- image ---
        pix = page.get_pixmap(dpi=dpi)
        img_path = dest / f"{stem}_p{page_no:03d}.png"
        pix.save(img_path)

        # --- text ---
        text = page.get_text("text").strip()
        used_ocr = False

        if force_ocr or len(text) < TEXT_THRESHOLD:
            ocr_text = ocr_pixmap(pix)
            if ocr_text.strip():
                text = ocr_text.strip()
                used_ocr = True

        txt_path = dest / f"{stem}_p{page_no:03d}.txt"
        txt_path.write_text(text, encoding="utf-8")

        tag = "OCR" if used_ocr else "text"
        print(f"  p{page_no:03d}  ({tag}, {len(text)} chars)")
        pages_done += 1

    doc.close()
    return pages_done


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract each PDF page as PNG + text (with optional OCR).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--input-dir", "-i", default=DEFAULT_INPUT,
                   help="Folder of source PDFs (or a single PDF file)")
    p.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT,
                   help="Root folder for per-document page folders")
    p.add_argument("--dpi", type=int, default=DEFAULT_DPI,
                   help="Render DPI for page images")
    p.add_argument("--force-ocr", action="store_true",
                   help="Always run Tesseract, even when digital text exists")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    src = Path(args.input_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if src.is_file() and src.suffix.lower() == ".pdf":
        pdfs = [src]
    elif src.is_dir():
        pdfs = sorted(src.glob("*.pdf"))
    else:
        print(f"Not found: {src}", file=sys.stderr)
        return 1

    if not pdfs:
        print(f"No PDFs in {src}")
        return 1

    if not HAS_TESSERACT:
        print("Note: pytesseract not installed – OCR fallback disabled.")
        print("      pip install pytesseract  + system tesseract package\n")

    total = 0
    for pdf in pdfs:
        print(f"Processing {pdf.name} …")
        total += process_pdf(pdf, out, args.dpi, args.force_ocr)

    print(f"\nDone. {total} page(s) written under {out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
