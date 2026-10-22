from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def search_chunks(
    chunks: list[dict],
    question: str,
    top_k: int = 3
) -> list[dict]:
    
    if not chunks or not question.strip():
        return []
    
    model = get_embedding_model()
    
    chunk_texts = [chunk["text"] for chunk in chunks]
    
    chunk_vectors = model.encode(
        chunk_texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        )
    
    question_vector = model.encode(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    
    # Normalized vectors: dot product gives cosine similarity.
    scores = chunk_vectors @ question_vector
    
    ranked_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    
    for index in ranked_indices:
        results.append({
            **chunks[index],
            "similarity_score": round(float(scores[index]), 4)
        })
    
    return results
    
    chunk_embeddings = np.array([model.encode([chunk["text"]])[0] for chunk in chunks])
    similarities = np.dot(chunk_embeddings, question_embedding) / (
        np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(question_embedding)
    )
    
    top_indices = similarities.argsort()[-top_k:][::-1]
    return [chunks[i] for i in top_indices]