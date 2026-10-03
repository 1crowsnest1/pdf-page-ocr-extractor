<pre style="font-family:'Courier New',Courier,monospace;font-size:12px;line-height:1.17;white-space:pre;background-color:#000;color:#fff;padding:8px;margin:0;"><span style="color:#AAAAAA">             ######  #######   ######       ######   ######   ######   ######  </span>
<span style="color:#AAAAAA">             ##  ##  ##   ##   ##           ##  ##   ##  ##   ##  ##   ##      </span>
<span style="color:#AAAAAA">             ##  ##  ##   ##   ##           ##  ##   ##  ##   ##       ##      </span>
<span style="color:#AAAAAA">            #######  ###  ##  #####        #######  #######  ### ###  #####    </span>
<span style="color:#AAAAAA">            ###      ###  ##  ###          ###      ###  ##  ###  ##  ###      </span>
<span style="color:#AAAAAA">            ###      ###  ##  ###          ###      ###  ##  ###  ##  ###      </span>
<span style="color:#AAAAAA">            ###      #######  ###          ###      ###  ##  #######  #######  </span>
<span style="color:#AAAAAA">                                                                               </span>
<span style="color:#AAAAAA"> ######  #######  ######        ######  ##   ##  #######  ######    ######  #######  #######   ######  ######   </span>
<span style="color:#AAAAAA"> ##  ##  ##   ##  ##  ##        ##      ##   ##    ##     ##  ##    ##  ##  ##   ##    ##      ##  ##  ##  ##   </span>
<span style="color:#AAAAAA"> ##  ##  ##       ##  ##        ##      ##   ##    ##     ##  ##    ##  ##  ##         ##      ##  ##  ##  ##   </span>
<span style="color:#AAAAAA">###  ##  ###      #######      #####      ###      ###    #######  #######  ###        ###    ###  ##  #######  </span>
<span style="color:#AAAAAA">###  ##  ###      ###  ##      ###      ###  ##    ###    ###  ##  ###  ##  ###        ###    ###  ##  ###  ##  </span>
<span style="color:#AAAAAA">###  ##  ###  ##  ###  ##      ###      ###  ##    ###    ###  ##  ###  ##  ###  ##    ###    ###  ##  ###  ##  </span>
<span style="color:#AAAAAA">#######  #######  ###  ##      #######  ###  ##    ###    ###  ##  ###  ##  #######    ###    #######  ###  ##  </span>
<span style="color:#AAAAAA">                                                                                                                </span></pre>


# PDF Page OCR Extractor

Extract PDF pages as **images + text with OCR** for LLM pipelines.

Every page becomes:

* a PNG image of the page, and
* a plain-text file containing the page’s text

Digital text is taken from the PDF itself. When a page has little or no extractable text (typical of scans) the tool falls back to **Tesseract OCR**.

## Why this exists

Feeding whole PDFs to language models is often lossy or rejected. Page-level images + clean text are ideal for **RAG**, document-AI pipelines, and manual review before prompting ChatGPT / Claude / local LLMs.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

**OCR (optional but recommended for scanned PDFs)**

```bash
# Debian/Ubuntu
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```

Without Tesseract the tool still works; it just skips the OCR fallback.

## Usage

```bash
python pdf_page_ocr.py --input-dir ./pdfs --output-dir ./pages_ocr
python pdf_page_ocr.py -i some.pdf --force-ocr --dpi 300
```

### Output layout

```
pages_ocr/
  MyDoc/
    MyDoc_p001.png
    MyDoc_p001.txt
    MyDoc_p002.png
    MyDoc_p002.txt
    …
```

## Options

| Flag | Default | Meaning |
|------|---------|---------|
| `-i / --input-dir` | `./pdfs` | Folder of PDFs (or a single PDF file) |
| `-o / --output-dir` | `./pages_ocr` | Root for per-document page folders |
| `--dpi` | `200` | Render DPI for page images |
| `--force-ocr` | off | Always run Tesseract |

## Topics

`pdf` · `ocr` · `tesseract` · `image-extraction` · `text-extraction` · `llm` · `rag` · `document-ai` · `pymupdf` · `python-cli`

## License

MIT – see [LICENSE](LICENSE).
