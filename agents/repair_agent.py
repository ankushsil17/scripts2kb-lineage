import json
from scripts2kb.utils.llm_client import call_llm
from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import REPAIR_SCHEMA


def repair(state: ArtifactState, config) -> ArtifactState:
    if not state.validation_errors:
        return state

    error_summary = "\n".join([f"  - {e}" for e in state.validation_errors])
    current_state = json.dumps({
        "entities": state.entities,
        "relations": state.relations,
        "narrative": state.narrative,
        "scripts": state.scripts,
    }, indent=2)

    prompt = f"""You are a repair agent. The following artifact failed validation.
Fix ONLY the specific issues listed below. Do not modify fields that are already valid.

Unit: {state.unit_id} ({state.element_name})

Validation errors:
{error_summary}

Current state:
{current_state}

Referenced code (first 1000 chars):
{state.referenced_code[:1000] if state.referenced_code else 'not available'}

Return JSON: {{"repairs": [{{"field": "...", "old_value": "...", "new_value": "...", "reason": "..."}}]}}"""

    try:
        result = call_llm(prompt, REPAIR_SCHEMA, config)
        repairs = result.get("repairs", [])
        _apply_repairs(state, repairs)
        state.repair_history.append({
            "iteration": state.repair_iterations + 1,
            "errors_before": list(state.validation_errors),
            "repairs_applied": repairs
        })
        state.repair_iterations += 1
    except Exception as e:
        state.repair_history.append({
            "iteration": state.repair_iterations + 1,
            "error": str(e)
        })
        state.repair_iterations += 1

    return state


def _apply_repairs(state: ArtifactState, repairs: list):
    for r in repairs:
        field = r.get("field", "")
        new_val = r.get("new_value", "")

        if field == "narrative" and new_val:
            state.narrative = new_val

        elif field.startswith("entity") and new_val:
            try:
                idx = int(field.split("[")[1].split("]")[0])
                subfield = field.split(".")[-1] if "." in field else None
                if subfield and idx < len(state.entities):
                    state.entities[idx][subfield] = new_val
                elif not subfield and idx < len(state.entities):
                    parsed = json.loads(new_val) if isinstance(new_val, str) else new_val
                    state.entities[idx] = parsed
            except (ValueError, IndexError, json.JSONDecodeError):
                pass

        elif field.startswith("relation") and new_val:
            try:
                idx = int(field.split("[")[1].split("]")[0])
                subfield = field.split(".")[-1] if "." in field else None
                if subfield and idx < len(state.relations):
                    state.relations[idx][subfield] = new_val
            except (ValueError, IndexError):
                pass
