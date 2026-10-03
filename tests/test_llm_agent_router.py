from app.graph.llm_agent_router import route_after_llm


def test_route_to_tool():

    class FakeMessage:
        tool_calls = [
            {
                "name": "get_claim",
                "args": {
                    "claim_id": "CLM001"
                },
            }
        ]

    state = {
        "messages": [
            FakeMessage()
        ]
    }

    result = route_after_llm(state)

    assert result == "tool"


def test_route_to_end():

    class FakeMessage:
        tool_calls = []

    state = {
        "messages": [
            FakeMessage()
        ]
    }

    result = route_after_llm(state)

    assert result == "end"
