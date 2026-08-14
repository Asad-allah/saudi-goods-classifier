import json
import subprocess
import sys
from pathlib import Path

import joblib


def test_training_script_writes_a_candidate_artifact_and_metrics(tmp_path) -> None:
    terms = {
        12: "شوكولاتة وحلوى",
        141: "كياس نفايات سوداء",
        5: "عبوات بلاستيك صناعية",
    }
    rows = [
        {
            "normalizedText": f"{term} نموذج {index}",
            "goodTypeId": root_id,
            "feedbackRecordedAt": f"2026-08-{index:02d}T00:00:00+00:00",
        }
        for root_id, term in terms.items()
        for index in range(1, 11)
    ]
    dataset = tmp_path / "verified-feedback.jsonl"
    dataset.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    model_output = tmp_path / "candidate.joblib"
    metadata_output = tmp_path / "candidate.json"
    project_root = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/train_feedback_model.py",
            "--dataset",
            str(dataset),
            "--model-output",
            str(model_output),
            "--metadata-output",
            str(metadata_output),
        ],
        cwd=project_root,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    metadata = json.loads(metadata_output.read_text(encoding="utf-8"))
    artifact = joblib.load(model_output)
    assert metadata["promotionStatus"] == "CANDIDATE_ONLY"
    assert artifact["metadata"]["candidateModelVersion"] == metadata["candidateModelVersion"]
    assert artifact["model"].predict(["كياس نفايات سوداء"])[0] == 141
