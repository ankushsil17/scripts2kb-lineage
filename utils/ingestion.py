import csv
import re
import os
from typing import List
from scripts2kb.utils.state import ArtifactState


COMMENT_PATTERNS = [
    re.compile(r"#\s*(.+)"),
    re.compile(r"--\s*(.+)"),
    re.compile(r"/\*\s*(.+?)\s*\*/", re.DOTALL),
    re.compile(r"//\s*(.+)"),
    re.compile(r"REM\s+(.+)", re.IGNORECASE),
]

SCRIPT_PATTERNS = [
    re.compile(r"(?:sh|bash|\.)\s+['\"]?([/\w.\-]+\.sh)", re.IGNORECASE),
    re.compile(r"(?:python|python3)\s+['\"]?([/\w.\-]+\.py)", re.IGNORECASE),
    re.compile(r"(?:sqlplus|isql|bcp)\s+.*?['\"]?([/\w.\-]+\.sql)", re.IGNORECASE),
    re.compile(r"(?:call|exec(?:ute)?)\s+['\"]?([/\w.\-]+)", re.IGNORECASE),
]

UNIT_DELIMITERS = [
    re.compile(r"^\s*unit\s*=\s*(.+)", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*\[([^\]]+)\]\s*$", re.MULTILINE),
    re.compile(r"^---+\s*$", re.MULTILINE),
]


def normalize_encoding(text: str) -> str:
    return text.encode("utf-8", errors="replace").decode("utf-8")


def normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def normalize_path(raw_path: str) -> str:
    if not raw_path:
        return ""
    cleaned = raw_path.replace("\\", "/")
    cleaned = re.sub(r"/+", "/", cleaned)
    return cleaned.strip()


def ingest_csv(csv_path: str) -> List[dict]:
    rows = []
    with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                key = k.strip() if k else k
                val = normalize_encoding(v.strip()) if v else ""
                cleaned[key] = val
            rows.append(cleaned)
    return rows


def segment_units(rows: List[dict]) -> List[ArtifactState]:
    artifacts = []
    for idx, row in enumerate(rows):
        state = ArtifactState()
        state.unit_id = f"unit_{idx:04d}"
        state.file_name = row.get("File Name", row.get("file_name", f"file_{idx}"))
        state.element_name = row.get("Element name", row.get("element_name", ""))
        state.raw_content = normalize_line_endings(row.get("raw_content", row.get("content", "")))

        seq = row.get("Sequence no", row.get("sequence_no", ""))
        state.sequence_no = int(seq) if seq.isdigit() else idx

        artifacts.append(state)
    return artifacts


def extract_comments(state: ArtifactState) -> ArtifactState:
    comments = []
    for pattern in COMMENT_PATTERNS:
        matches = pattern.findall(state.raw_content)
        comments.extend([m.strip() for m in matches if m.strip()])
    state.comments = comments
    return state


def extract_scripts(state: ArtifactState) -> ArtifactState:
    scripts = []
    for pattern in SCRIPT_PATTERNS:
        matches = pattern.findall(state.raw_content)
        scripts.extend(matches)
    state.scripts = list(set(scripts))
    return state


def resolve_paths(state: ArtifactState) -> ArtifactState:
    if state.scripts:
        state.structured_file_path = normalize_path(state.scripts[0])
    params = re.findall(r"--?\w+[\s=]+['\"]?([^'\"\s]+)", state.raw_content)
    state.parameters = params
    return state


def resolve_code(state: ArtifactState, scripts_dir: str) -> ArtifactState:
    for script in state.scripts:
        fname = os.path.basename(script)
        candidates = [
            os.path.join(scripts_dir, fname),
            os.path.join(scripts_dir, normalize_path(script)),
        ]
        for path in candidates:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        state.referenced_code = f.read()
                except Exception:
                    pass
                break
    return state


def derive_control_flow(artifacts: List[ArtifactState]) -> List[ArtifactState]:
    sorted_arts = sorted(artifacts, key=lambda a: a.sequence_no)
    for i in range(len(sorted_arts) - 1):
        edge = {
            "predecessor": sorted_arts[i].unit_id,
            "successor": sorted_arts[i + 1].unit_id,
            "order": i
        }
        sorted_arts[i].control_flow_edges.append(edge)
    return sorted_arts


def run_layer1(csv_path: str, scripts_dir: str) -> List[ArtifactState]:
    rows = ingest_csv(csv_path)
    artifacts = segment_units(rows)
    for art in artifacts:
        extract_comments(art)
        extract_scripts(art)
        resolve_paths(art)
        resolve_code(art, scripts_dir)
    artifacts = derive_control_flow(artifacts)
    return artifacts
