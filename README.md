# Scripts2KB

**From Scheduler Artifacts to Structured Knowledge via Agentic Extraction and Repair**

A framework that converts enterprise scheduler exports into structured, reviewable knowledge base artifacts using deterministic parsing, multi-agent LLM orchestration, schema-constrained validation, and targeted repair.

## Architecture

```
Layer 1 (Deterministic)          Layer 2 (Agentic)              Layer 3 (Governance)
─────────────────────           ──────────────────              ────────────────────
CSV Ingestion                   Entity Agent                    Validation
Unit Segmentation         →     Relation Agent            →     Targeted Repair
Comment Extraction              Narrative Agent                 Reconciliation
Script/Path Resolution          Control-Flow Agent              KB Export
Translation                     Supervisor Orchestration
```

## Project Structure

```
scripts2kb/
├── main.py                      # CLI entry point
├── requirements.txt
├── config/
│   └── settings.py              # Pipeline config, schemas, enums
├── agents/
│   ├── supervisor.py            # Orchestrator — routes artifacts through agents
│   ├── entity_agent.py          # Pass 1: entity extraction
│   ├── relation_agent.py        # Pass 2: relation extraction
│   ├── narrative_agent.py       # Pass 3: narrative generation
│   ├── control_flow_agent.py    # Pass 4: control flow extraction
│   ├── validation_agent.py      # Syntactic + semantic validation
│   ├── repair_agent.py          # Targeted field-level repair
│   ├── reconciliation_agent.py  # Cross-model merging
│   └── translation_agent.py     # Multilingual normalization
└── utils/ac
    ├── ingestion.py             # Layer 1: CSV parsing, segmentation, path resolution
    ├── llm_client.py            # OpenAI API wrapper
    ├── state.py                 # Shared artifact state dataclass
    └── kb_exporter.py           # JSON export for KB insertion
```

## Usage

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."

python -m scripts2kb.main \
  --input data/scheduler_export.csv \
  --scripts-dir data/scripts/ \
  --output output/kb/ \
  --model gpt-4o
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | (required) | Path to scheduler CSV export |
| `--scripts-dir` | `data/scripts/` | Directory with referenced script files |
| `--output` | `output/kb/` | KB output directory |
| `--model` | `gpt-4o` | OpenAI model to use |
| `--max-repair` | `3` | Max repair iterations per artifact |
| `--no-reconciliation` | `false` | Disable cross-model reconciliation |
| `--api-key` | env var | OpenAI API key |

## Input Format

CSV with columns (flexible naming):

| Column | Description |
|--------|-------------|
| `File Name` / `file_name` | Canonical file identifier |
| `Element name` / `element_name` | Unit or subtask label |
| `Sequence no` / `sequence_no` | Execution order index |
| `raw_content` / `content` | Raw unit content (scripts, commands, SQL) |

## Output

Four JSON files in the output directory:

- `kb_artifacts.json` — Full artifact records with entities, relations, narratives, provenance
- `kb_summary.json` — Aggregate statistics (counts, repair distribution, coverage)
- `kb_entities.json` — Flat entity list across all units
- `kb_relations.json` — Flat relation list across all units

## Pipeline Flow

1. **Ingest** CSV → normalize encodings, segment units, extract comments
2. **Resolve** script paths, match to repository files
3. **Translate** non-English labels/comments (cached)
4. **Extract** entities → relations → control flow → narrative (schema-anchored)
5. **Validate** syntactic + semantic constraints
6. **Repair** failed fields only (up to N iterations)
7. **Reconcile** ambiguous cases via cross-model comparison
8. **Export** to KB-ready JSON
