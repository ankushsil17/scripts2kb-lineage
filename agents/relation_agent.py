from scripts2kb.utils.llm_client import call_llm
from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import RELATION_SCHEMA, RELATION_TYPES


def extract_relations(state: ArtifactState, config) -> ArtifactState:
    if not state.entities:
        return state

    entity_names = [e["name"] for e in state.entities]
    entity_list = "\n".join([f"  - {e['name']} ({e['entity_type']}, {e['role']})" for e in state.entities])

    prompt = f"""You are a relation extraction agent for scheduler artifacts.

Given the following unit and its extracted entities, identify directional relationships between them.
Relation types: {RELATION_TYPES}
For each relation, provide: source, target, relation type, and a short evidence string.

Return JSON: {{"relations": [{{"source": "...", "target": "...", "relation": "...", "evidence": "..."}}]}}

Unit: {state.unit_id} ({state.element_name})
Scripts: {', '.join(state.scripts) if state.scripts else 'none'}
Entities:
{entity_list}

Referenced code (first 1500 chars):
{state.referenced_code[:1500] if state.referenced_code else 'not available'}"""

    try:
        result = call_llm(prompt, RELATION_SCHEMA, config)
        state.relations = result.get("relations", [])
    except Exception as e:
        state.validation_errors.append(f"relation_extraction_failed: {str(e)}")

    return state
