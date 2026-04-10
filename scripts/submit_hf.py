"""Submit evaluation results to Hugging Face model repo via PR."""

import os
import sys
from pathlib import Path

from huggingface_hub import CommitOperationAdd, create_commit


def normalize_model_id(model_id: str) -> str:
    """Convert OpenRouter model_id to HF repo format.

    Examples:
        openrouter/anthropic/claude-opus-4-5 -> anthropic/claude-opus-4-5
        anthropic/anthropic/claude-opus-4-5 -> anthropic/claude-opus-4-5

    """
    # Remove openrouter/ prefix
    if model_id.startswith("openrouter/"):
        model_id = model_id.removeprefix("openrouter/")

    # Handle duplicated provider prefix
    parts = model_id.split("/")
    if len(parts) >= 3 and parts[0] == parts[1]:
        model_id = f"{parts[0]}/{parts[2]}"

    return model_id


def main(model_id: str, accuracy: float, run_url: str) -> None:
    """Create PR on HF model repo with eval results."""
    hf_model_id = normalize_model_id(model_id)
    token = os.environ.get("HF_TOKEN")

    if not token:
        print("HF_TOKEN not set")
        sys.exit(1)

    # Create eval results YAML
    eval_results_dir = Path(".eval_results")
    eval_results_dir.mkdir(exist_ok=True)

    yaml_content = f"""- dataset:
    id: couto/bjj-vqa
    task_id: default
  value: {accuracy}
  date: "{os.environ["EVAL_DATE"]}"
  source:
    url: {run_url}
    name: GitHub Actions Eval
"""

    yaml_path = eval_results_dir / "bjj-vqa.yaml"
    yaml_path.write_text(yaml_content)

    # Create PR
    operations = [
        CommitOperationAdd(
            path_in_repo=".eval_results/bjj-vqa.yaml",
            path_or_fileobj=str(yaml_path),
        ),
    ]

    create_commit(
        repo_id=hf_model_id,
        operations=operations,
        commit_message="Add BJJ-VQA evaluation results",
        token=token,
        repo_type="model",
        create_pr=True,
    )

    print(f"Submitted PR to {hf_model_id}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: submit_hf.py <model_id> <accuracy> <run_url>")
        sys.exit(1)

    main(sys.argv[1], float(sys.argv[2]), sys.argv[3])
