from pathlib import Path
import fitz


def extract_pdf_pages(pdf_path: str) -> list[dict]:
    pages: list[dict] = []

    doc = fitz.open(pdf_path)
    try:
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            text = text.strip()
            pages.append(
                {
                    "page_number": index,
                    "text": text,
                    "char_count": len(text),
                }
            )
    finally:
        doc.close()

    return pages


def write_extracted_text(output_path: str, pages: list[dict]) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for page in pages:
            f.write(f"\n\n===== PAGE {page['page_number']} =====\n\n")
            f.write(page["text"])
            f.write("\n")
