import logging
from typing import List
from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import PipelineConfig
from scripts2kb.agents.translation_agent import translate
from scripts2kb.agents.entity_agent import extract_entities
from scripts2kb.agents.relation_agent import extract_relations
from scripts2kb.agents.narrative_agent import generate_narrative
from scripts2kb.agents.control_flow_agent import extract_control_flow
from scripts2kb.agents.validation_agent import validate
from scripts2kb.agents.repair_agent import repair
from scripts2kb.agents.reconciliation_agent import reconcile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("supervisor")


def process_artifact(state: ArtifactState, config: PipelineConfig) -> ArtifactState:
    log.info(f"Processing {state.unit_id}: {state.element_name}")

    state = translate(state, config)
    log.info(f"  Translation done")

    state = extract_entities(state, config)
    log.info(f"  Entities: {len(state.entities)} found")

    state = extract_relations(state, config)
    log.info(f"  Relations: {len(state.relations)} found")

    state = extract_control_flow(state, config)
    log.info(f"  Control flow: {len(state.control_flow_edges)} edges")

    state = generate_narrative(state, config)
    log.info(f"  Narrative generated (confidence={state.narrative_confidence:.2f})")

    if config.use_reconciliation and state.narrative_confidence < config.reconciliation_threshold:
        log.info(f"  Low confidence — running reconciliation")
        state = reconcile(state, config)

    state = validate(state)
    log.info(f"  Validation: {state.validation_flag} ({len(state.validation_errors)} errors)")

    iteration = 0
    while state.validation_flag == "Incomplete" and iteration < config.max_repair_iterations:
        log.info(f"  Repair iteration {iteration + 1}")
        state = repair(state, config)
        state = validate(state)
        log.info(f"  Post-repair: {state.validation_flag} ({len(state.validation_errors)} errors)")
        iteration += 1

    if state.validation_flag == "Complete":
        state.status = "Completed"
    else:
        state.status = "NeedsReview"

    state.provenance["pipeline"] = {
        "repair_iterations": state.repair_iterations,
        "final_validation_flag": state.validation_flag,
        "entity_count": len(state.entities),
        "relation_count": len(state.relations),
    }

    log.info(f"  Final status: {state.status}")
    return state


def process_batch(artifacts: List[ArtifactState], config: PipelineConfig) -> List[ArtifactState]:
    results = []
    total = len(artifacts)
    for i, art in enumerate(artifacts):
        log.info(f"[{i+1}/{total}] Starting {art.unit_id}")
        processed = process_artifact(art, config)
        results.append(processed)
    return results
