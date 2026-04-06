from scripts2kb.utils.llm_client import call_llm
from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import CONTROL_FLOW_SCHEMA


def extract_control_flow(state: ArtifactState, config) -> ArtifactState:
    if not state.referenced_code and not state.raw_content:
        return state

    code = state.referenced_code[:2000] if state.referenced_code else state.raw_content[:2000]

    prompt = f"""You are a control-flow extraction agent for scheduler artifacts.

Given the following unit, identify execution order edges between substeps.
Return JSON: {{"edges": [{{"predecessor": "...", "successor": "...", "order": 0}}]}}

If no substep ordering is discernible, return {{"edges": []}}.

Unit: {state.unit_id} ({state.element_name})
Code/content:
{code}"""

    try:
        result = call_llm(prompt, CONTROL_FLOW_SCHEMA, config)
        llm_edges = result.get("edges", [])
        state.control_flow_edges = state.control_flow_edges + llm_edges
    except Exception as e:
        state.validation_errors.append(f"control_flow_failed: {str(e)}")

    return state
