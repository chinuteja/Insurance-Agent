from app.llm import create_llm


def test_llm_creation():

    llm = create_llm()

    assert llm is not None