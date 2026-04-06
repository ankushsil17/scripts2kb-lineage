import argparse
import os
import sys

from scripts2kb.config.settings import PipelineConfig
from scripts2kb.utils.ingestion import run_layer1
from scripts2kb.agents.supervisor import process_batch
from scripts2kb.utils.kb_exporter import export_to_kb


def main():
    parser = argparse.ArgumentParser(description="Scripts2KB: Scheduler Artifacts to Knowledge Base")
    parser.add_argument("--input", required=True, help="Path to scheduler CSV export")
    parser.add_argument("--scripts-dir", default="data/scripts/", help="Directory containing referenced scripts")
    parser.add_argument("--output", default="output/kb/", help="KB output directory")
    parser.add_argument("--model", default="gpt-4o", help="Primary OpenAI model")
    parser.add_argument("--max-repair", type=int, default=3, help="Max repair iterations")
    parser.add_argument("--no-reconciliation", action="store_true", help="Disable cross-model reconciliation")
    parser.add_argument("--api-key", default=None, help="OpenAI API key (or set OPENAI_API_KEY env var)")
    args = parser.parse_args()

    config = PipelineConfig()
    config.input_csv = args.input
    config.scripts_dir = args.scripts_dir
    config.kb_output_dir = args.output
    config.model_primary = args.model
    config.max_repair_iterations = args.max_repair
    config.use_reconciliation = not args.no_reconciliation

    if args.api_key:
        config.openai_api_key = args.api_key
    if not config.openai_api_key:
        print("Error: Set OPENAI_API_KEY or pass --api-key")
        sys.exit(1)

    print(f"Input: {config.input_csv}")
    print(f"Scripts dir: {config.scripts_dir}")
    print(f"Output: {config.kb_output_dir}")
    print(f"Model: {config.model_primary}")
    print(f"Reconciliation: {'enabled' if config.use_reconciliation else 'disabled'}")
    print()

    print("Layer 1: Ingestion & deterministic parsing...")
    artifacts = run_layer1(config.input_csv, config.scripts_dir)
    print(f"  Segmented {len(artifacts)} units")
    print()

    print("Layer 2: Agentic extraction & Layer 3: Validation/Repair...")
    results = process_batch(artifacts, config)
    print()

    print("Exporting to KB...")
    kb_path, summary_path, ent_path, rel_path = export_to_kb(results, config.kb_output_dir)
    print(f"  Artifacts: {kb_path}")
    print(f"  Summary:   {summary_path}")
    print(f"  Entities:  {ent_path}")
    print(f"  Relations: {rel_path}")
    print()

    completed = sum(1 for r in results if r.status == "Completed")
    review = sum(1 for r in results if r.status == "NeedsReview")
    print(f"Done. {completed} completed, {review} need review out of {len(results)} total.")


if __name__ == "__main__":
    main()
