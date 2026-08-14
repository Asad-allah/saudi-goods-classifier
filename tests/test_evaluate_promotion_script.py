import json
import subprocess
import sys
from pathlib import Path


def test_promotion_script_writes_a_report_and_uses_nonzero_exit_on_rejection(tmp_path) -> None:
    candidate = {
        "candidateModelVersion": "feedback-tfidf-candidate",
        "promotionStatus": "CANDIDATE_ONLY",
        "datasetSha256": "same-data",
        "split": {"testRows": 120},
        "metrics": {
            "top1Accuracy": 0.91,
            "top3Recall": 0.98,
            "highConfidencePrecision": 0.96,
            "highConfidenceSampleCount": 40,
        },
    }
    baseline = {
        "evaluationDatasetSha256": "same-data",
        "metrics": {
            "top1Accuracy": 0.90,
            "top3Recall": 0.97,
            "highConfidencePrecision": 0.95,
        },
    }
    candidate_path = tmp_path / "candidate.json"
    baseline_path = tmp_path / "baseline.json"
    report_path = tmp_path / "promotion.json"
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    project_root = Path(__file__).resolve().parents[1]

    accepted = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_promotion.py",
            "--candidate",
            str(candidate_path),
            "--baseline",
            str(baseline_path),
            "--report",
            str(report_path),
        ],
        cwd=project_root,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )

    assert accepted.returncode == 0, accepted.stderr
    assert json.loads(report_path.read_text(encoding="utf-8"))["approved"] is True

    candidate["metrics"]["top1Accuracy"] = 0.1
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
    rejected = subprocess.run(
        [
            sys.executable,
            "scripts/evaluate_promotion.py",
            "--candidate",
            str(candidate_path),
            "--baseline",
            str(baseline_path),
            "--report",
            str(report_path),
        ],
        cwd=project_root,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )

    assert rejected.returncode == 2
    rejected_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert rejected_report["approved"] is False
    assert any(item["code"] == "TOP1_BELOW_THRESHOLD" for item in rejected_report["failedGates"])
