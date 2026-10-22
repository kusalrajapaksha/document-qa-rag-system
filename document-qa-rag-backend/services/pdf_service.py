import pymupdf

def extract_pdf_text(file_bytes: bytes) -> dict:
    """Extract text from a PDF provided as bytes."""
    
    with pymupdf.open(
        stream=file_bytes,
        filetype="pdf"
    ) as document:
        
        pages = []

        for page_number in range(1, document.page_count + 1):
            page = document[page_number - 1]
            text = page.get_text("text")
            pages.append({
                "page_number": page_number,
                "text": text,
            })

    return {
        "page_count": len(pages),
        "pages": pages,
    }