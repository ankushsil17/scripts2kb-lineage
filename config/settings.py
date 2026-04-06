import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PipelineConfig:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model_primary: str = "gpt-4o"
    model_secondary: str = "gpt-4o-mini"
    max_repair_iterations: int = 3
    translation_cache_path: str = "cache/translations.json"
    input_csv: str = "data/scheduler_export.csv"
    scripts_dir: str = "data/scripts/"
    output_dir: str = "output/"
    kb_output_dir: str = "output/kb/"
    use_reconciliation: bool = True
    reconciliation_threshold: float = 0.7


ENTITY_TYPES = ["file", "table", "procedure", "command", "parameter"]
ENTITY_ROLES = ["read", "write", "execute", "reference"]
RELATION_TYPES = ["invokes", "depends_on", "reads", "writes"]
VALIDATION_STATUSES = ["valid", "invalid"]

ENTITY_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "entity_type": {"type": "string", "enum": ENTITY_TYPES},
                    "role": {"type": "string", "enum": ENTITY_ROLES},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["name", "entity_type", "role", "confidence"]
            }
        }
    },
    "required": ["entities"]
}

RELATION_SCHEMA = {
    "type": "object",
    "properties": {
        "relations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "relation": {"type": "string", "enum": RELATION_TYPES},
                    "evidence": {"type": "string"}
                },
                "required": ["source", "target", "relation", "evidence"]
            }
        }
    },
    "required": ["relations"]
}

NARRATIVE_SCHEMA = {
    "type": "object",
    "properties": {
        "narrative": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "required": ["narrative", "confidence"]
}

CONTROL_FLOW_SCHEMA = {
    "type": "object",
    "properties": {
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "predecessor": {"type": "string"},
                    "successor": {"type": "string"},
                    "order": {"type": "integer"}
                },
                "required": ["predecessor", "successor", "order"]
            }
        }
    },
    "required": ["edges"]
}

TRANSLATION_SCHEMA = {
    "type": "object",
    "properties": {
        "source": {"type": "string"},
        "english": {"type": "string"}
    },
    "required": ["source", "english"]
}

REPAIR_SCHEMA = {
    "type": "object",
    "properties": {
        "repairs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "old_value": {"type": "string"},
                    "new_value": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["field", "new_value", "reason"]
            }
        }
    },
    "required": ["repairs"]
}
