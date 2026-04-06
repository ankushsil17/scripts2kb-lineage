from scripts2kb.utils.llm_client import call_llm
from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import ENTITY_SCHEMA, RELATION_SCHEMA
from scripts2kb.agents.entity_agent import extract_entities
from scripts2kb.agents.relation_agent import extract_relations


def reconcile(state: ArtifactState, config) -> ArtifactState:
    if not config.use_reconciliation:
        return state

    state_copy = ArtifactState()
    state_copy.__dict__.update(state.__dict__)
    state_copy.entities = []
    state_copy.relations = []
    state_copy.validation_errors = []

    extract_entities(state_copy, config)
    extract_relations(state_copy, config)

    model_a_entities = state.entities
    model_b_entities = state_copy.entities
    state.entities = _merge_entities(model_a_entities, model_b_entities)

    model_a_relations = state.relations
    model_b_relations = state_copy.relations
    state.relations = _merge_relations(model_a_relations, model_b_relations)

    state.provenance["reconciliation"] = {
        "model_a_entity_count": len(model_a_entities),
        "model_b_entity_count": len(model_b_entities),
        "merged_entity_count": len(state.entities),
        "model_a_relation_count": len(model_a_relations),
        "model_b_relation_count": len(model_b_relations),
        "merged_relation_count": len(state.relations),
    }

    return state


def _merge_entities(list_a: list, list_b: list) -> list:
    merged = {}
    for ent in list_a:
        key = (ent.get("name", "").lower(), ent.get("entity_type", ""))
        merged[key] = ent.copy()
        merged[key]["confidence"] = ent.get("confidence", 0.5)

    for ent in list_b:
        key = (ent.get("name", "").lower(), ent.get("entity_type", ""))
        if key in merged:
            old_conf = merged[key]["confidence"]
            new_conf = ent.get("confidence", 0.5)
            merged[key]["confidence"] = min(1.0, (old_conf + new_conf) / 2 + 0.15)
        else:
            ent_copy = ent.copy()
            ent_copy["confidence"] = ent.get("confidence", 0.5) * 0.7
            merged[key] = ent_copy

    return list(merged.values())


def _merge_relations(list_a: list, list_b: list) -> list:
    merged = {}
    for rel in list_a:
        key = (rel.get("source", ""), rel.get("target", ""), rel.get("relation", ""))
        merged[key] = rel.copy()

    for rel in list_b:
        key = (rel.get("source", ""), rel.get("target", ""), rel.get("relation", ""))
        if key in merged:
            existing_ev = merged[key].get("evidence", "")
            new_ev = rel.get("evidence", "")
            if new_ev and new_ev not in existing_ev:
                merged[key]["evidence"] = f"{existing_ev} | {new_ev}"
        else:
            merged[key] = rel.copy()

    return list(merged.values())
