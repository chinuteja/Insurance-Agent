from langchain_groq import ChatGroq


def create_llm():

    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
    )