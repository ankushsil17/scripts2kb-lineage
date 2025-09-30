c1# scripts2kb-lineage
**From legacy job schedules to actionable knowledge.**  
This project provides a generalized framework for transforming raw scheduler/script exports into a **searchable Knowledge Base (KB)** and **execution lineage graph**, with explainability baked in.

---

c2#Features
- **Parsing & Enrichment**
  - Extracts units, scripts, parameters, references.
  - Translates multilingual labels into English.
  - Generates short human-readable descriptions.
- **Validation & Repair**
  - Ensures schema conformity.
  - Flags incomplete rows for further checks.
- **Knowledge Base (SQLite)**
  - Structured metadata stored in `script_metadata`.
  - Indexed for fast search and filtering.
- **Lineage Graph**
  - Nodes: units & scripts.
  - Edges: `unit → script` (execution), `unit → unit` (dependencies).
  - Exported as:
    - `kb_lineage.graphml` (for Gephi/Cytoscape)
    - `nodes.csv` (node attributes)
    - `edges.csv` (relations)
- **Privacy-Safe**
  - Only structure and metadata are retained.
  - No private dataset contents are exposed.
