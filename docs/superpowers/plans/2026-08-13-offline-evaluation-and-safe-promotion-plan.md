# Offline Evaluation and Safe Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** بناء خط بيانات وتقييم وترقية آمن للنموذج المتعلّم من تصحيحات دندن، من دون أن يغيّر النموذج المرشح مسار تصنيف السائق قبل إثبات تفوقه على baseline ثابت.

**Architecture:** يبقى `Exact + Fuzzy + Embedding` هو النظام الحي. يُصدر backend التصحيحات الموثقة إلى dataset versioned، ويُقسمها زمنياً إلى train/validation/test مع عزل النصوص المتشابهة. تُقيَّم retrieval baseline والنموذج المرشح على test نفسه، ثم يكتب promotion gate تقريراً قابلاً للتدقيق؛ التقرير الموافق يسمح بـshadow ثم canary فقط، ولا يبدّل النموذج تلقائياً.

**Tech Stack:** Python 3.12، FastAPI، RapidFuzz، SentenceTransformers/E5، scikit-learn 1.9، NumPy، joblib، Pytest، JSONL في الـMVP ثم PostgreSQL في الإنتاج.

## Global Constraints

- لا Agent ولا بحث إنترنت ولا LLM API ضمن مسار السائق.
- لا يقرأ `/v1/classify` أي `joblib` artifact خلال هذه الخطة.
- تدعم الخدمة العربية والإنجليزية والمختلط؛ اللغة الأخرى تعود `requiresReview=true`.
- لا تدخل `DRIVER_SELECTION` أو `DEMO` في التدريب؛ `OPERATOR_REVIEW` فقط هو مرشح dataset.
- كل artifact يحمل `datasetSha256` وcatalog/model/normalizer versions ووقت التدريب.
- الاختبار النهائي مقفل زمنياً ولا يستخدم لاختيار model أو threshold.
- الترقية لا تتم إلا إذا: Top-1 ≥ 0.90، Top-3 ≥ 0.97، ودقة القرارات التلقائية ≥ 0.95، ولا يوجد تراجع عن baseline على نفس test set.
- كل قيمة ناقصة، أو dataset غير مطابق، أو عينة غير كافية، تعني رفض الترقية.

---

## حدود هذه الخطة

هذه الخطة تنفذ التقييم والقرار Offline، ثم تحدد عقد shadow/canary. لا تنشئ قاعدة بيانات دندن الإنتاجية ولا تغير تطبيق السائق. قبل Task 1 يجب أن يضيف backend دندن هوية المراجع الموثوق بها إلى event production؛ لا تُقبل هوية مراجِع من تطبيق السائق مباشرة.

## File Structure

```text
app/training/
  feedback_dataset.py       # dataset موثق مع provenance
  splits.py                 # عزل النص المتكرر وتقسيم زمني عالمي
  metrics.py                # Top-k وselective-risk وWilson lower bound
  supervised.py             # challenger: TF-IDF + calibrated LR
  retrieval_evaluator.py    # يقيم النظام الحي frozen على نفس test
  promotion.py              # pure gate: لا deploy ولا load artifact
scripts/
  export_feedback_dataset.py
  train_feedback_model.py
  evaluate_retrieval_baseline.py
  evaluate_candidate_model.py
  check_candidate_promotion.py
tests/
  test_feedback_dataset.py
  test_splits.py
  test_metrics.py
  test_retrieval_evaluator.py
  test_supervised_training.py
  test_promotion.py
```

## Task 1: تثبيت عقد dataset وتتبّع أصله

**Files:**
- Modify: `app/training/feedback_dataset.py`
- Modify: `scripts/export_feedback_dataset.py`
- Modify: `tests/test_feedback_dataset.py`
- Modify: `docs/decisions/ADR-004-feedback-driven-classifier-improvement.md`

**Consumes:** أحداث `CLASSIFICATION` و`CLASSIFICATION_FEEDBACK` الموجودة في JSONL.

**Produces:** صف export ثابت بالشكل:

```python
{
    "feedbackId": str,
    "requestId": str,
    "text": str,
    "normalizedText": str,
    "rootGoodTypeId": int,
    "catalogVersion": str,
    "modelVersion": str,
    "normalizerVersion": str,
    "classificationRecordedAt": str,
    "feedbackRecordedAt": str,
    "reviewerId": str,
}
```

- [ ] **Step 1: Write the failing test for retained provenance.**

```python
def test_dataset_export_retains_trusted_reviewer_and_normalizer_version() -> None:
    rows, _ = build_verified_feedback_dataset([
        {"eventType": "CLASSIFICATION", "requestId": "r1", "text": "كياس زبالة",
         "normalizedText": "كياس زباله", "normalizerVersion": "ar-v2",
         "recordedAt": "2026-08-13T09:00:00+00:00"},
        {"eventType": "CLASSIFICATION_FEEDBACK", "requestId": "r1", "feedbackId": "f1",
         "selectedRootGoodTypeId": 141, "reviewerId": "ops-8",
         "trainingEligibility": "CANDIDATE_AFTER_VALIDATION",
         "recordedAt": "2026-08-13T09:02:00+00:00"},
    ])
    assert rows[0]["normalizerVersion"] == "ar-v2"
    assert rows[0]["reviewerId"] == "ops-8"
```

- [ ] **Step 2: Run the test and verify it fails because those fields are absent.**

Run: `uv run pytest tests/test_feedback_dataset.py::test_dataset_export_retains_trusted_reviewer_and_normalizer_version -q`

Expected: `FAIL` with missing field assertion.

- [ ] **Step 3: Extend the event export and reject incomplete production labels.**

```python
reviewer_id = _nonempty_string(feedback.get("reviewerId"))
normalizer_version = _nonempty_string(classification.get("normalizerVersion"))
if reviewer_id is None or normalizer_version is None:
    report["quarantinedIncompleteProvenance"] += 1
    continue
```

Add the two fields to the export row and add `quarantinedIncompleteProvenance` to the report. Keep local legacy events exportable only when the script receives `--allow-legacy-provenance`; default production behavior must reject them.

- [ ] **Step 4: Run focused tests.**

Run: `uv run pytest tests/test_feedback_dataset.py -q`

Expected: all dataset tests pass, including missing provenance quarantine.

- [ ] **Step 5: Document the trusted source boundary.**

State in ADR-004 that Dandan backend stamps `reviewerId` from its authenticated operator session; API payloads from a driver cannot self-declare `OPERATOR_REVIEW`.

- [ ] **Step 6: Commit the isolated change.**

```powershell
git add app/training/feedback_dataset.py scripts/export_feedback_dataset.py tests/test_feedback_dataset.py docs/decisions/ADR-004-feedback-driven-classifier-improvement.md
git commit -m "feat: retain trusted label provenance in training exports"
```

## Task 2: تقسيم زمني عالمي وعزل التسرب

**Files:**
- Create: `app/training/splits.py`
- Create: `tests/test_splits.py`
- Modify: `app/training/supervised.py`

**Consumes:** صفوف verified feedback من Task 1.

**Produces:**

```python
@dataclass(frozen=True)
class DatasetSplit:
    train: list[dict[str, Any]]
    validation: list[dict[str, Any]]
    test: list[dict[str, Any]]
    metadata: dict[str, Any]

def make_temporal_grouped_split(
    rows: list[dict[str, Any]], *, validation_fraction: float = 0.15,
    test_fraction: float = 0.15,
) -> DatasetSplit: ...
```

- [ ] **Step 1: Write the failing test for global temporal order.**

```python
def test_temporal_split_never_trains_on_a_row_newer_than_validation_or_test() -> None:
    split = make_temporal_grouped_split(rows_from_three_months())
    assert max(row["feedbackRecordedAt"] for row in split.train) < min(
        row["feedbackRecordedAt"] for row in split.validation
    )
    assert max(row["feedbackRecordedAt"] for row in split.validation) < min(
        row["feedbackRecordedAt"] for row in split.test)
```

- [ ] **Step 2: Write the failing test for duplicate-group isolation.**

```python
def test_same_normalized_text_group_is_never_split_between_train_and_test() -> None:
    split = make_temporal_grouped_split(rows_with_repeated_normalized_text())
    partitions = [split.train, split.validation, split.test]
    memberships = [any(row["normalizedText"] == "كيس زباله" for row in part) for part in partitions]
    assert sum(memberships) == 1
```

- [ ] **Step 3: Run both tests and verify they fail because `splits.py` does not exist.**

Run: `uv run pytest tests/test_splits.py -q`

Expected: import error for `app.training.splits`.

- [ ] **Step 4: Implement deterministic grouped chronological splitting.**

```python
def group_key(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(row["normalizedText"].encode("utf-8")).hexdigest()

groups = sorted(grouped_rows.values(), key=lambda group: max_timestamp(group))
```

Assign a complete group to exactly one partition. Compute cutoffs by cumulative row count but never move an older group after a newer group. If a root category is absent from train, mark it `unsupportedRoots` in metadata; do not duplicate a future sample into train merely to satisfy stratification.

- [ ] **Step 5: Replace `_temporal_stratified_split` in `supervised.py`.**

Train only on `split.train`; fit calibration inside train with cross-validation; use `split.validation` only to choose automatic-decision threshold; reserve `split.test` for final metrics.

- [ ] **Step 6: Run split and training tests.**

Run: `uv run pytest tests/test_splits.py tests/test_supervised_training.py -q`

Expected: all pass; a category missing from train causes `TrainingDataInsufficient`, never a fabricated split.

- [ ] **Step 7: Commit the isolated change.**

```powershell
git add app/training/splits.py app/training/supervised.py tests/test_splits.py tests/test_supervised_training.py
git commit -m "feat: use grouped global temporal splits for model evaluation"
```
