# Bug: the loop stopped at len(text) - size, so the final chunk (and any short tail) was dropped.


def chunk_text(text: str, size: int, overlap: int = 0) -> list[str]:
    """Split text into chunks of `size` characters, each overlapping the previous by `overlap`.

    The last chunk may be shorter. Every character of text appears in some chunk.
    Raises ValueError unless 0 <= overlap < size.
    """
    if not 0 <= overlap < size:
        raise ValueError("need 0 <= overlap < size")
    step = size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunks.append(text[start : start + size])
        if start + size >= len(text):
            break  # this chunk reached the end; another would only repeat the overlap
    return chunks
