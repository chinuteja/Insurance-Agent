
from app.graph.claim_agent_state import ClaimAgentState


def set_current_agent(agent_name: str) -> dict:
    """Set the agent currently executing."""

    return {
        "current_agent": agent_name
    }


def record_agent_result(
    state: ClaimAgentState,
    agent_name: str,
    result: dict,
) -> dict:
    """Store an agent's result and mark it as completed."""

    agent_results = dict(state.get("agent_results") or {})
    completed_agents = list(state.get("completed_agents") or [])

    agent_results[agent_name] = result

    if agent_name not in completed_agents:
        completed_agents.append(agent_name)

    return {
        "agent_results": agent_results,
        "completed_agents": completed_agents,
        "current_agent": None,
    }


def record_agent_error(
    state: ClaimAgentState,
    agent_name: str,
    error: str,
) -> dict:
    """Record an agent execution error."""

    agent_errors = list(state.get("agent_errors") or [])

    agent_errors.append({
        "agent": agent_name,
        "error": error,
    })

    return {
        "agent_errors": agent_errors,
        "current_agent": agent_name,
    }
