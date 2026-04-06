from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import ENTITY_TYPES, ENTITY_ROLES, RELATION_TYPES


def validate(state: ArtifactState) -> ArtifactState:
    state.validation_errors = []
    _check_entities(state)
    _check_relations(state)
    _check_narrative(state)
    _check_scripts(state)

    if not state.validation_errors:
        state.validation_flag = "Complete"
    else:
        state.validation_flag = "Incomplete"

    return state


def _check_entities(state: ArtifactState):
    for i, ent in enumerate(state.entities):
        if not ent.get("name"):
            state.validation_errors.append(f"entity[{i}]: missing name")
        if ent.get("entity_type") not in ENTITY_TYPES:
            state.validation_errors.append(f"entity[{i}]: invalid type '{ent.get('entity_type')}'")
        if ent.get("role") not in ENTITY_ROLES:
            state.validation_errors.append(f"entity[{i}]: invalid role '{ent.get('role')}'")
        conf = ent.get("confidence")
        if conf is None or not (0 <= conf <= 1):
            state.validation_errors.append(f"entity[{i}]: confidence out of range")


def _check_relations(state: ArtifactState):
    entity_names = {e["name"] for e in state.entities}
    for i, rel in enumerate(state.relations):
        if not rel.get("source"):
            state.validation_errors.append(f"relation[{i}]: missing source")
        if not rel.get("target"):
            state.validation_errors.append(f"relation[{i}]: missing target")
        if rel.get("relation") not in RELATION_TYPES:
            state.validation_errors.append(f"relation[{i}]: invalid type '{rel.get('relation')}'")
        if rel.get("source") and rel["source"] not in entity_names:
            state.validation_errors.append(f"relation[{i}]: source '{rel['source']}' not in entities")
        if rel.get("target") and rel["target"] not in entity_names:
            state.validation_errors.append(f"relation[{i}]: target '{rel['target']}' not in entities")


def _check_narrative(state: ArtifactState):
    if not state.narrative:
        state.validation_errors.append("narrative: empty")
    elif len(state.narrative.split()) < 5:
        state.validation_errors.append("narrative: too short (< 5 words)")


def _check_scripts(state: ArtifactState):
    if not state.scripts and state.raw_content:
        state.validation_errors.append("scripts: none extracted despite content present")
