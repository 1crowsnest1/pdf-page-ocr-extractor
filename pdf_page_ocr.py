#!/usr/bin/env python3
"""
PDF Page OCR Extractor (patched)
================================
Changes against the working copy (pdf_page_ocr.py):

1. The embedded text layer is ALWAYS kept, as <stem>_pNNN.layer.txt, and fresh
   Tesseract OCR is written as <stem>_pNNN.txt when --force-ocr is set (or when
   the layer is shorter than --text-threshold).  The 1893/1896 scans carry an
   embedded layer that clips the first 1-12 characters of most lines; fresh OCR
   of the page image does not.  Keeping both lets you diff them.
2. --force-ocr fails loudly if Tesseract is missing instead of silently writing
   the clipped layer (original behaviour: HAS_TESSERACT False -> text = layer).
3. --psm / --lang / --oem are passed to Tesseract (default psm 4: single column
   of variable-size text, which suits these pages; use 11 or 12 for plates).
4. --index-offset: when the input is a chunk PDF (e.g. ..._p031-045.pdf), pass 30
   so that page 1 of the chunk is written as p031.  --page-offset gives the
   PRINTED page (1893 main body: -1; 1896 supplement: +254) and is recorded in
   index.json and in the file names (_p204_printed203).
5. --pages "30-31,204,246-" restricts the run.
6. index.json per document: pdf index, printed page, chars in layer, chars in OCR,
   method, mean word confidence (Tesseract TSV) so weak pages can be listed.
7. Plate-like pages (very little text) get a second OCR pass with psm 11 and the
   better of the two is kept (more characters of dictionary-like words).
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

import pymupdf as fitz

try:
    import pytesseract
    from PIL import Image

    HAS_TESSERACT = True
except ImportError:  # pragma: no cover
    HAS_TESSERACT = False


DEFAULT_INPUT = "./pdfs"
DEFAULT_OUTPUT = "./pages_ocr"
DEFAULT_DPI = 200
TEXT_THRESHOLD = 40


def parse_pages(spec: str | None, lo: int, hi: int) -> set[int]:
    if not spec:
        return set(range(lo, hi + 1))
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a = int(a) if a else lo
            b = int(b) if b else hi
            out.update(range(a, b + 1))
        else:
            out.add(int(part))
    return out


def ocr_image(img: "Image.Image", psm: int, lang: str, oem: int):
    cfg = f"--psm {psm} --oem {oem}"
    text = pytesseract.image_to_string(img, lang=lang, config=cfg) or ""
    data = pytesseract.image_to_data(
        img, lang=lang, config=cfg, output_type=pytesseract.Output.DICT
    )
    confs = [float(c) for c, t in zip(data["conf"], data["text"])
             if t.strip() and float(c) >= 0]
    return text.strip(), (sum(confs) / len(confs) if confs else 0.0)


def wordish(text: str) -> int:
    return len(re.findall(r"[A-Za-z]{3,}", text))


def process_pdf(pdf_path, out_root, dpi, force_ocr, psm, lang, oem,
                index_offset, page_offset, pages_spec, text_threshold):
    stem = pdf_path.stem
    # chunk names like X_p031-045 -> strip the page range so outputs merge
    stem = re.sub(r"_p\d{3}-\d{3}$", "", stem)
    dest = out_root / stem
    dest.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    first = 1 + index_offset
    last = len(doc) + index_offset
    wanted = parse_pages(pages_spec, first, last)
    index_path = dest / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    done = 0
    for i in range(len(doc)):
        idx = i + 1 + index_offset
        if idx not in wanted:
            continue
        printed = idx + page_offset if page_offset is not None else None
        tag = f"_p{idx:03d}" + (f"_printed{printed:03d}" if printed and printed > 0 else "")
        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        pix.save(dest / f"{stem}{tag}.png")
        layer = page.get_text("text").strip()
        (dest / f"{stem}{tag}.layer.txt").write_text(layer, encoding="utf-8")
        text, method, conf = layer, "layer", None
        if force_ocr or len(layer) < text_threshold:
            if not HAS_TESSERACT:
                if force_ocr:
                    sys.exit("pytesseract/Pillow not installed but --force-ocr was set")
            else:
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                best, conf = ocr_image(img, psm, lang, oem)
                method = f"ocr-psm{psm}"
                if len(best) < 300:  # plate-like: try sparse text mode
                    alt, alt_conf = ocr_image(img, 11, lang, oem)
                    if wordish(alt) > wordish(best):
                        best, conf, method = alt, alt_conf, "ocr-psm11"
                if best:
                    text = best
        (dest / f"{stem}{tag}.txt").write_text(text, encoding="utf-8")
        index[str(idx)] = {
            "pdf_index": idx,
            "printed_page": printed,
            "layer_chars": len(layer),
            "text_chars": len(text),
            "method": method,
            "mean_conf": None if conf is None else round(conf, 1),
        }
        print(f"  idx {idx:03d} printed {printed}  {method}  layer={len(layer)} text={len(text)}"
              + ("" if conf is None else f" conf={conf:.0f}"))
        done += 1
    index_path.write_text(json.dumps(index, indent=1, sort_keys=True))
    doc.close()
    return done


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Extract each PDF page as PNG + layer text + fresh OCR.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--input-dir", "-i", default=DEFAULT_INPUT)
    p.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT)
    p.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    p.add_argument("--force-ocr", action="store_true")
    p.add_argument("--psm", type=int, default=4)
    p.add_argument("--oem", type=int, default=1)
    p.add_argument("--lang", default="eng")
    p.add_argument("--index-offset", type=int, default=0,
                   help="added to the in-file page number (chunk PDFs)")
    p.add_argument("--page-offset", type=int, default=None,
                   help="printed = index + this (1893 body -1; supplement +254)")
    p.add_argument("--pages", default=None, help='e.g. "30-31,204,246-"')
    p.add_argument("--text-threshold", type=int, default=TEXT_THRESHOLD)
    return p.parse_args(argv)


def main(argv=None) -> int:
    a = parse_args(argv)
    src, out = Path(a.input_dir), Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    pdfs = [src] if src.is_file() else sorted(src.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs in {src}")
        return 1
    if not HAS_TESSERACT:
        print("Note: pytesseract not installed - OCR fallback disabled.")
    total = 0
    for pdf in pdfs:
        print(f"Processing {pdf.name} ...")
        total += process_pdf(pdf, out, a.dpi, a.force_ocr, a.psm, a.lang, a.oem,
                             a.index_offset, a.page_offset, a.pages,
                             a.text_threshold)
    print(f"Done. {total} page(s) under {out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
