import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.document_loader import load_pdf
from app.rag.text_splitter import split_documents

pdf_path = "data/policies/sample_policy.pdf"

pages = load_pdf(pdf_path)
chunks = split_documents(pages)

print(f"Total pages: {len(pages)}")
print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {index + 1} ---")
    print(chunk["content"])
    print("Metadata:", chunk["metadata"])