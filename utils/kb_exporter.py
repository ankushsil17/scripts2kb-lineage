import json
import os
from typing import List
from scripts2kb.utils.state import ArtifactState


def export_to_kb(artifacts: List[ArtifactState], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    kb_records = []
    for art in artifacts:
        record = {
            "unit_id": art.unit_id,
            "file_name": art.file_name,
            "element_name": art.element_name,
            "sequence_no": art.sequence_no,
            "scripts": art.scripts,
            "structured_file_path": art.structured_file_path,
            "parameters": art.parameters,
            "referenced_code_available": bool(art.referenced_code),
            "translation": art.translation,
            "narrative": art.narrative,
            "narrative_confidence": art.narrative_confidence,
            "entities": art.entities,
            "relations": art.relations,
            "control_flow_edges": art.control_flow_edges,
            "validation_flag": art.validation_flag,
            "status": art.status,
            "repair_iterations": art.repair_iterations,
            "provenance": art.provenance,
        }
        kb_records.append(record)

    kb_path = os.path.join(output_dir, "kb_artifacts.json")
    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(kb_records, f, indent=2, ensure_ascii=False)

    summary = _build_summary(artifacts)
    summary_path = os.path.join(output_dir, "kb_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    entities_path = os.path.join(output_dir, "kb_entities.json")
    all_entities = []
    for art in artifacts:
        for ent in art.entities:
            all_entities.append({"unit_id": art.unit_id, **ent})
    with open(entities_path, "w", encoding="utf-8") as f:
        json.dump(all_entities, f, indent=2, ensure_ascii=False)

    relations_path = os.path.join(output_dir, "kb_relations.json")
    all_relations = []
    for art in artifacts:
        for rel in art.relations:
            all_relations.append({"unit_id": art.unit_id, **rel})
    with open(relations_path, "w", encoding="utf-8") as f:
        json.dump(all_relations, f, indent=2, ensure_ascii=False)

    return kb_path, summary_path, entities_path, relations_path


def _build_summary(artifacts: List[ArtifactState]) -> dict:
    total = len(artifacts)
    completed = sum(1 for a in artifacts if a.status == "Completed")
    needs_review = sum(1 for a in artifacts if a.status == "NeedsReview")
    scripts_nonempty = sum(1 for a in artifacts if a.scripts)
    narratives_nonempty = sum(1 for a in artifacts if a.narrative)
    translations_nonempty = sum(1 for a in artifacts if a.translation)
    total_entities = sum(len(a.entities) for a in artifacts)
    total_relations = sum(len(a.relations) for a in artifacts)
    avg_repair = sum(a.repair_iterations for a in artifacts) / max(total, 1)

    repair_dist = {"0": 0, "1": 0, "2": 0, "3": 0, "3+": 0}
    for a in artifacts:
        if a.repair_iterations == 0:
            repair_dist["0"] += 1
        elif a.repair_iterations == 1:
            repair_dist["1"] += 1
        elif a.repair_iterations == 2:
            repair_dist["2"] += 1
        elif a.repair_iterations == 3:
            repair_dist["3"] += 1
        else:
            repair_dist["3+"] += 1

    return {
        "total_artifacts": total,
        "status_completed": completed,
        "status_needs_review": needs_review,
        "scripts_nonempty": scripts_nonempty,
        "narratives_nonempty": narratives_nonempty,
        "translations_nonempty": translations_nonempty,
        "total_entities": total_entities,
        "total_relations": total_relations,
        "avg_entities_per_unit": total_entities / max(total, 1),
        "avg_relations_per_unit": total_relations / max(total, 1),
        "avg_repair_iterations": avg_repair,
        "repair_distribution": repair_dist,
    }
