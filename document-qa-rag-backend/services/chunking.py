
def chunk_pages(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """Split extracted PDF pages into overlapping word chunks."""
    
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be a non-negative integer and less than chunk_size.")
    
    chunks = []
    chunk_id = 0
    step = chunk_size - overlap
    
    for page in pages:
        words = page["text"].split()
        page_number = page["page_number"]
        
        for start in range(0, len(words), step):
            chunk_words = words[start:start + chunk_size]
            
            if not chunk_words:
                break
            
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "chunk_id": chunk_id,
                "page_number": page_number,
                "text": chunk_text,
                "word_count": len(chunk_words)
            })
            
            chunk_id += 1
            
            if start + chunk_size >= len(words):
                break
            
    return chunks