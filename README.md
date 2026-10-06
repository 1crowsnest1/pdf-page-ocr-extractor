#   🇵 🇩 🇫   🇵 🇦 🇬 🇪   🇴 🇨 🇷   🇪 🇽 🇹 🇷 🇦 🇨 🇹 🇴 🇷

𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑃𝐷𝐹 𝑝𝑎𝑔𝑒𝑠 𝑎𝑠 **𝑖𝑚𝑎𝑔𝑒𝑠 + 𝑡𝑒𝑥𝑡 𝑤𝑖𝑡ℎ 𝑂𝐶𝑅** 𝑓𝑜𝑟 𝐿𝐿𝑀 𝑝𝑖𝑝𝑒𝑙𝑖𝑛𝑒𝑠.

Every page becomes:

* a PNG image of the page, and
* a plain-text file containing the page’s text

Digital text is taken from the PDF itself. When a page has little or no extractable text (typical of scans) the tool falls back to **Tesseract OCR**.

## Why this exists

Feeding whole PDFs to language models is often lossy or rejected. Page-level images + clean text are ideal for **RAG**, document-AI pipelines, and manual review before prompting ChatGPT / Claude / local LLMs.

## 𝕀𝕟𝕤𝕥𝕒𝕝𝕝𝕒𝕥𝕚𝕠𝕟

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

**𝕆ℂℝ (𝕠𝕡𝕥𝕚𝕠𝕟𝕒𝕝 𝕓𝕦𝕥 𝕣𝕖𝕔𝕠𝕞𝕞𝕖𝕟𝕕𝕖𝕕 𝕗𝕠𝕣 𝕤𝕔𝕒𝕟𝕟𝕖𝕕 ℙ𝔻𝔽𝕤)**

```bash
# Debian/Ubuntu
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```

Without Tesseract the tool still works; it just skips the OCR fallback.

## 𝕌𝕤𝕒𝕘𝕖

```bash
python pdf_page_ocr.py --input-dir ./pdfs --output-dir ./pages_ocr
python pdf_page_ocr.py -i some.pdf --force-ocr --dpi 300
```

### 𝕆𝕦𝕥𝕡𝕦𝕥 𝕝𝕒𝕪𝕠𝕦𝕥
```
pages_ocr/
  MyDoc/
    MyDoc_p001.png
    MyDoc_p001.txt
    MyDoc_p002.png
    MyDoc_p002.txt
    …
```

## 𝕆𝕡𝕥𝕚𝕠𝕟𝕤

| Flag | Default | Meaning |
|------|---------|---------|
| `-i / --input-dir` | `./pdfs` | Folder of PDFs (or a single PDF file) |
| `-o / --output-dir` | `./pages_ocr` | Root for per-document page folders |
| `--dpi` | `200` | Render DPI for page images |
| `--force-ocr` | off | Always run Tesseract |

## 𝕋𝕠𝕡𝕚𝕔𝕤

`pdf` · `ocr` · `tesseract` · `image-extraction` · `text-extraction` · `llm` · `rag` · `document-ai` · `pymupdf` · `python-cli`

## License

MIT – see [LICENSE](LICENSE).
