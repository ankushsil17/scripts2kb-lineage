from scripts2kb.utils.llm_client import call_llm
from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import NARRATIVE_SCHEMA


def generate_narrative(state: ArtifactState, config) -> ArtifactState:
    entity_summary = ", ".join([f"{e['name']} ({e['entity_type']})" for e in state.entities[:10]])
    relation_summary = ", ".join([f"{r['source']}->{r['target']} ({r['relation']})" for r in state.relations[:10]])

    prompt = f"""You are a narrative generation agent for scheduler artifacts.

Write a concise 1-2 sentence technical description of what this unit does.
Focus on purpose, major operations, and side effects.
Return JSON: {{"narrative": "...", "confidence": 0.0}}

Unit: {state.unit_id} ({state.element_name})
Scripts: {', '.join(state.scripts) if state.scripts else 'none'}
Entities: {entity_summary or 'none extracted'}
Relations: {relation_summary or 'none extracted'}
Comments: {' | '.join(state.comments[:3]) if state.comments else 'none'}
Translation: {state.translation or 'N/A'}

Referenced code (first 1000 chars):
{state.referenced_code[:1000] if state.referenced_code else 'not available'}"""

    try:
        result = call_llm(prompt, NARRATIVE_SCHEMA, config)
        state.narrative = result.get("narrative", "")
        state.narrative_confidence = result.get("confidence", 0.0)
    except Exception as e:
        state.validation_errors.append(f"narrative_generation_failed: {str(e)}")

    return state
