from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ArtifactState:
    unit_id: str = ""
    file_name: str = ""
    element_name: str = ""
    sequence_no: int = 0
    raw_content: str = ""
    scripts: list = field(default_factory=list)
    structured_file_path: str = ""
    parameters: list = field(default_factory=list)
    referenced_code: str = ""
    comments: list = field(default_factory=list)
    translation: str = ""
    original_language_text: str = ""
    entities: list = field(default_factory=list)
    relations: list = field(default_factory=list)
    control_flow_edges: list = field(default_factory=list)
    narrative: str = ""
    narrative_confidence: float = 0.0
    confidence: float = 0.0
    validation_errors: list = field(default_factory=list)
    validation_flag: str = "Incomplete"
    repair_history: list = field(default_factory=list)
    repair_iterations: int = 0
    status: str = ""
    provenance: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "file_name": self.file_name,
            "element_name": self.element_name,
            "sequence_no": self.sequence_no,
            "scripts": self.scripts,
            "structured_file_path": self.structured_file_path,
            "parameters": self.parameters,
            "referenced_code": self.referenced_code,
            "comments": self.comments,
            "translation": self.translation,
            "entities": self.entities,
            "relations": self.relations,
            "control_flow_edges": self.control_flow_edges,
            "narrative": self.narrative,
            "narrative_confidence": self.narrative_confidence,
            "validation_flag": self.validation_flag,
            "repair_iterations": self.repair_iterations,
            "status": self.status,
            "provenance": self.provenance
        }
