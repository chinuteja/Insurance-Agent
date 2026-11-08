from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingService:

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

    def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            raise ValueError(
                "No text provided for embedding generation."
            )

        if any(not text.strip() for text in texts):
            raise ValueError(
                "Empty text cannot be converted into embeddings."
            )

        return self.model.embed_documents(texts)