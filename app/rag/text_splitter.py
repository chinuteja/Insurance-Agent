
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    pages: list[dict],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[dict]:
    """
    Split extracted PDF pages into smaller text chunks.

    Each chunk retains its original PDF page metadata.
    """

    if not pages:
        raise ValueError("No pages provided for splitting.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = []

    for page in pages:
        content = page["content"]

        if not content.strip():
            continue

        page_chunks = splitter.split_text(content)

        for chunk_index, chunk in enumerate(page_chunks):
            chunks.append({
                "content": chunk,
                "metadata": {
                    **page["metadata"],
                    "chunk_index": chunk_index,
                },
            })

    if not chunks:
        raise ValueError("No text chunks could be generated.")

    return chunks
