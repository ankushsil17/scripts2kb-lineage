from scripts2kb.utils.llm_client import call_llm
from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import ENTITY_SCHEMA, ENTITY_TYPES, ENTITY_ROLES


def extract_entities(state: ArtifactState, config) -> ArtifactState:
    context = _build_context(state)
    prompt = f"""You are an entity extraction agent for scheduler artifacts.

Given the following scheduler unit, identify all entities (files, tables, procedures, commands, parameters).
For each entity, provide: name, entity_type (one of {ENTITY_TYPES}), role (one of {ENTITY_ROLES}), confidence (0-1).

Return JSON matching this schema:
{{"entities": [{{"name": "...", "entity_type": "...", "role": "...", "confidence": 0.0}}]}}

Unit context:
{context}"""

    try:
        result = call_llm(prompt, ENTITY_SCHEMA, config)
        state.entities = result.get("entities", [])
    except Exception as e:
        state.validation_errors.append(f"entity_extraction_failed: {str(e)}")

    return state


def _build_context(state: ArtifactState) -> str:
    parts = [f"Unit ID: {state.unit_id}"]
    parts.append(f"Element: {state.element_name}")
    if state.scripts:
        parts.append(f"Scripts: {', '.join(state.scripts)}")
    if state.structured_file_path:
        parts.append(f"Path: {state.structured_file_path}")
    if state.parameters:
        parts.append(f"Parameters: {', '.join(state.parameters)}")
    if state.comments:
        parts.append(f"Comments: {' | '.join(state.comments[:5])}")
    if state.referenced_code:
        code_snippet = state.referenced_code[:2000]
        parts.append(f"Referenced code:\n{code_snippet}")
    if state.translation:
        parts.append(f"Translation: {state.translation}")
    return "\n".join(parts)
