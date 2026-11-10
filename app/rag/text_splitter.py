
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    pages: list[dict],
    chunk_size: int = 150,
    chunk_overlap: int = 0,
) -> list[dict]:
    """
    Split PDF pages into sentence-level policy chunks.

    Section headings are attached to their corresponding clauses.
    Original PDF page metadata is retained.
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

    # Fallback splitter for unusually long sentences.
    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=[" ", ""],
    )

    chunks = []

    for page in pages:

        content = page["content"]

        if not content.strip():
            continue

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        sentence_units = []
        current_heading = None

        for line in lines:

            # Ignore PDF title and footer noise.
            if re.fullmatch(
                r"Sample Motor Insurance Policy",
                line,
                flags=re.IGNORECASE,
            ):
                continue

            if re.fullmatch(
                r"Sample Motor Insurance Policy\s+Page\s+\d+\s+of\s+\d+",
                line,
                flags=re.IGNORECASE,
            ):
                continue

            # Retain section headings with their clauses.
            if re.match(r"^PAGE\s+\d+\s*[—-]", line, re.IGNORECASE):
                current_heading = line
                continue

            # Split the line into individual sentences.
            sentences = re.split(
                r"(?<=[.!?])\s+",
                line,
            )

            for sentence in sentences:

                sentence = sentence.strip()

                if not sentence:
                    continue

                if current_heading:
                    sentence = f"{current_heading}\n{sentence}"
                    current_heading = None

                sentence_units.append(sentence)

        # Handle any heading without following text.
        if current_heading:
            sentence_units.append(current_heading)

        # Create one chunk per policy sentence.
        page_chunks = []

        for sentence in sentence_units:

            if len(sentence) <= chunk_size:
                page_chunks.append(sentence)

            else:
                page_chunks.extend(
                    fallback_splitter.split_text(sentence)
                )

        for chunk_index, chunk in enumerate(page_chunks):

            if not chunk.strip():
                continue

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
