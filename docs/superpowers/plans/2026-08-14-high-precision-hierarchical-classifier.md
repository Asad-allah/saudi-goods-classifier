# High-Precision Hierarchical Classifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Assign free text to the closest categorical `good_types` row (الأب التصنيفي الأول) plus its root, without product matching, through a selective hybrid classifier that reranks ambiguous requests and abstains when evidence is insufficient.

**Architecture:** Reuse the existing FastAPI, RapidFuzz, SentenceTransformers, JSONL feedback, and offline promotion code. Change ranking identity from root ID to source good-type ID, harden lexical retrieval, add a provider-isolated reranker, then calibrate acceptance from Dandan data. Keep the request path a simple cascade; do not add an Agent, LangGraph, vector database, or live web search.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, RapidFuzz, SentenceTransformers, NumPy, HTTPX, pytest, optional BGE-M3/Jina model, optional Cohere Rerank 4 API.

## Global Constraints

- Keep `DANDAN_INPUT_VALIDATION_ENABLED=false` during the error-collection session.
- Exact and catalog-anchored fuzzy retrieval run before any quality rejection.
- Return both `directGoodType` and `rootGoodType`; never overload the word `category` or `parent` to mean both.
- Treat `directGoodType` as the closest categorical row owning the matched name/alias; expose its real database `parentId` separately.
- Do not query or return a product entity or `productId`; this service classifies only against `good_types`.
- Final candidates must be selectable leaves: a row with children is context, not an allowed result. A root with no children is a leaf and remains selectable.
- Never return fallback ID 31, or any other default ID. An unresolved decision returns `directGoodType=null` and `rootGoodType=null` with review alternatives.
- Preserve raw database labels for output, but exclude unreviewed `en_name` values from retrieval evidence because the current SQL contains incorrect translations.
- Do not claim `99.999%` without adequate independent test evidence.
- Online timeout or malformed provider response must force review, never silent acceptance.
- Never promote from one driver's correction; verified feedback remains offline until promotion gates pass.
- Use `py`, not `python`, in Windows commands.
- Never create per-phrase production exceptions for reported errors; fix the retrieval, ranking, or decision mechanism and lock it with regression tests.
- Never display raw fuzzy, cosine, or rerank scores as accuracy/confidence; `decisionConfidence` is `null` until a promoted calibrator produces it.
- In the MVP, a fuzzy-only route can retrieve alternatives but cannot set `requiresReview=false`; acceptance needs an exact/approved variant or agreement with independent semantic/rerank evidence.

## مخطط التنفيذ

```text
المرحلة A — صحة البنية والعقد
taxonomy → matched good type → lexical guards → API

المرحلة B — رفع الفهم مع منع التخمين
gold set → source documents → local retrieval benchmark → conditional reranker → calibrated review

المرحلة C — التحسن من الاستخدام
verified feedback → offline thin ML → promotion gates → engineering demo
```

---

### Task 1: Preserve the complete two-level taxonomy

**Files:**
- Modify: `app/catalog/models.py`
- Modify: `app/catalog/importer.py`
- Modify: `scripts/build_catalog.py`
- Test: `tests/test_catalog_import.py`

**Interfaces:**
- Consumes: SQL `good_types(id, ar_name, en_name, common_names, parent_id)`.
- Produces: `Catalog.good_types: dict[int, GoodTypeNode]`, `Catalog.good_type(id)`, `Catalog.root_for(id)`, and `Catalog.is_selectable(id)`.

- [ ] **Step 1: Write the failing hierarchy test**

```python
def test_catalog_preserves_child_and_root_metadata() -> None:
    catalog = build_catalog([
        GoodType(12, "مواد غذائية", "Food Items", (), None),
        GoodType(171, "الخضروات والفواكه", "Produce", ("بطاطا",), 12),
    ])
    assert catalog.good_type(171).parent_id == 12
    assert catalog.root_for(171).id == 12
    assert catalog.is_selectable(171) is True
    assert catalog.is_selectable(12) is False

def test_same_alias_is_preserved_and_flagged_across_direct_types() -> None:
    catalog = build_catalog(_two_children_with_alias("أجهزة كهربائية"))
    terms = [t for t in catalog.terms if t.normalized_term == "اجهزه كهربائيه"]
    assert {t.source_good_type_id for t in terms} == {56, 132}
    assert all(t.is_cross_good_type_ambiguous for t in terms)

def test_null_common_name_is_not_converted_to_string_none() -> None:
    assert _parse_common_names('[null, "زيت"]') == ("زيت",)
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_catalog_import.py::test_catalog_preserves_child_and_root_metadata -q`

Expected: failure because `Catalog` stores only roots and search terms.

- [ ] **Step 3: Add the minimal node model and artifact fields**

```python
@dataclass(frozen=True)
class GoodTypeNode:
    id: int
    name_ar: str
    name_en: str
    parent_id: int | None
```

Store every row in `Catalog.good_types`, derive child membership, and expose only leaf rows as selectable final candidates. Parent names remain routing evidence for their children. Serialize the hierarchy under `goodTypes`; when loading the previous artifact format, reject it with a clear rebuild instruction instead of inventing parent data. Change term deduplication and ambiguity detection to use `source_good_type_id`, not root ID. Keep `en_name` in `GoodTypeNode` output metadata but do not create an English search term until that field is explicitly approved.

- [ ] **Step 4: Rebuild and verify**

Run:

```powershell
uv run pytest tests/test_catalog_import.py -q
py scripts/build_catalog.py
```

Expected: 103 nodes, 37 roots, 66 children, 13 nodes with children, 90 selectable leaves, maximum depth one. The generated audit lists unreviewed English labels, including known source inconsistencies, without modifying the SQL dump.

### Task 2: Rank by direct categorical good type instead of root

**Files:**
- Modify: `app/search/fusion.py`
- Modify: `app/classifier/models.py`
- Modify: `app/classifier/service.py`
- Modify: `app/classifier/policy.py`
- Test: `tests/test_fusion.py`
- Test: `tests/test_classifier.py`

**Interfaces:**
- Consumes: `CandidateHit.source_good_type_id` and Task 1 catalog hierarchy.
- Produces: `GoodTypeCandidate(good_type_id, parent_good_type_id, root_good_type_id, rank, score, ...)`.

- [ ] **Step 1: Write failing source-level tests**

```python
def test_potato_returns_produce_child_and_food_root() -> None:
    result = _classifier().classify(request_id="potato", text="بطاطا")
    assert result.direct_good_type.good_type_id == 171
    assert result.direct_good_type.root_good_type_id == 12

def test_electric_pole_returns_wiring_child_and_construction_root() -> None:
    result = _classifier().classify(request_id="pole", text="عمود كهربا")
    assert result.direct_good_type.good_type_id == 56
    assert result.direct_good_type.root_good_type_id == 34
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_fusion.py tests/test_classifier.py -q`

Expected: existing fusion collapses both matches into `root_good_type_id`.

- [ ] **Step 3: Change only the aggregation key**

Replace every root-keyed accumulator in `fuse_hits` with `source_good_type_id`. Preserve `root_good_type_id` on the resulting candidate for hierarchy output. Change exact-hit deduplication from `seen_roots` to `seen_good_types`. Filter final candidates through `Catalog.is_selectable`. A hit on a non-selectable parent name is routing context for its children and can never itself become `directGoodType`; parent-only evidence forces review.

- [ ] **Step 4: Verify GREEN**

Run: `uv run pytest tests/test_fusion.py tests/test_classifier.py -q`

Expected: exact, fuzzy, and semantic evidence remain visible, but alternatives are distinct good types.

### Task 3: Put lexical evidence before the quality gate

**Files:**
- Modify: `app/classifier/service.py`
- Modify: `app/nlp/input_quality.py`
- Test: `tests/test_classifier.py`
- Test: `tests/test_input_quality.py`

**Interfaces:**
- Consumes: normalized input, exact hits, guarded fuzzy hits.
- Produces: quality-gate call only when no catalog lexical anchor exists.

- [ ] **Step 1: Write the failing ordering test**

```python
def test_known_catalog_alias_reaches_exact_before_quality_rejection() -> None:
    result = _classifier(input_validation_enabled=True).classify(
        request_id="short-known",
        text="بط",
    )
    assert result.reason == "EXACT"
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_classifier.py::test_known_catalog_alias_reaches_exact_before_quality_rejection -q`

Expected: current classifier invokes `require_meaningful` before retrieval.

- [ ] **Step 3: Reorder without weakening boundary validation**

Implement this sequence inside `classify`:

```python
normalized = normalize_text(text)
exact_hits = self._exact_hits(normalized, compact_text(normalized))
fuzzy_hits = [] if exact_hits else self._fuzzy.search(normalized, top_k=20)
if self._quality_gate is not None and not (exact_hits or strong_lexical_anchor(fuzzy_hits)):
    self._quality_gate.require_meaningful(text)
```

Pydantic empty/length validation remains at the API boundary.

- [ ] **Step 4: Verify GREEN**

Run: `uv run pytest tests/test_classifier.py tests/test_input_quality.py tests/test_api_contract.py -q`

### Task 4: Harden Arabic typo, dialect, and short-term retrieval

**Files:**
- Modify: `app/nlp/normalizer.py`
- Create: `app/nlp/dialect_lexicon.py`
- Modify: `app/classifier/service.py`
- Modify: `app/search/fuzzy.py`
- Modify: `app/search/models.py`
- Test: `tests/test_normalizer.py`
- Test: `tests/test_fuzzy.py`
- Test: `tests/test_classifier.py`

**Interfaces:**
- Produces: `RetrievalVariant(text, kind)`, `retrieval_variants(text) -> tuple[RetrievalVariant, ...]`, `DialectLexicon.expand(tokens) -> tuple[RetrievalVariant, ...]`, and length-aware fuzzy evidence.

- [ ] **Step 1: Write failing regression tests**

```python
def test_retrieval_variant_collapses_excessive_arabic_run() -> None:
    assert "بطاطس" in retrieval_variants("بطاااااطس")

def test_short_partial_term_cannot_beat_full_word_typo() -> None:
    hits = _retriever("بطاااااطس").search("بطاااااطس", top_k=3)
    assert hits[0].matched_term == "بطاطا"
    assert hits[0].matched_term != "بط"

def test_two_character_overlap_is_not_a_strong_fuzzy_anchor() -> None:
    hit = score_tokens(query="بطاطس", catalog_term="بط")
    assert hit.is_strong_lexical_anchor is False

def test_fuzzy_only_candidate_requires_review() -> None:
    result = _classifier(semantic_retriever=UnavailableSemantic()).classify(
        request_id="fuzzy-only",
        text="بطاطسز",
    )
    assert result.requires_review is True

def test_water_dialects_expand_to_one_catalog_concept() -> None:
    lexicon = DialectLexicon({"مياه": ("موية", "مويه", "ماي", "مي", "ماء")})
    assert {v.text for v in lexicon.expand(("موية",))} >= {"موية", "مياه"}

def test_conservative_suffix_variant_maps_biscuit_form() -> None:
    assert RetrievalVariant("بسكوت", "MORPHOLOGY") in retrieval_variants("بسكوتة")
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_normalizer.py tests/test_fuzzy.py -q`

- [ ] **Step 3: Implement conservative retrieval variants**

For Arabic runs of three or more identical letters, generate a collapsed copy while retaining the original normalized string. Add only benchmarked conservative morphology variants, beginning with final `ة` removal when the remaining token has at least four letters. In fuzzy scoring, disable partial-substring scorers when either side has fewer than four characters, reject two-character-only anchors, require a minimum token-length ratio before edit similarity can vote, and use full-token normalized edit similarity instead of substring containment. Load a small, versioned concept lexicon from reviewed catalog aliases; expansion adds retrieval variants and never changes the logged normalized input. In `RootCategoryClassifier.classify`, perform exact lookup over the original normalized form and all retrieval variants before the quality gate, so a reviewed two-letter dialect form such as `مي` is allowed without weakening random-text rejection. Variant matches report `LEXICAL_VARIANT`, not `EXACT`; a fuzzy-only route always requires review in the MVP.

- [ ] **Step 4: Verify GREEN**

Run: `uv run pytest tests/test_normalizer.py tests/test_fuzzy.py -q`

Expected: `بطاااااطس` retrieves source 171 rather than bird source 123; the genuine exact alias `بط` still works only when entered exactly. `موية`, `ماي`, and `مي` retrieve bottled-water source 166 through the same concept without relying on partial fuzzy similarity.

### Task 5: Define the new API and feedback contract

**Files:**
- Modify: `app/api/schemas.py`
- Modify: `app/api/routes.py`
- Modify: `README.md`
- Create: `docs/decisions/ADR-005-source-good-type-classification.md`
- Test: `tests/test_api_contract.py`

**Interfaces:**
- Produces: nullable `directGoodType`, nullable `rootGoodType`, leaf-only `alternatives`, nullable `decisionConfidence`, `policyVersion`, and `selectedGoodTypeId` feedback.

- [ ] **Step 1: Write the failing contract test**

```python
def test_response_exposes_matched_type_and_root(tmp_path) -> None:
    response = _classify(tmp_path, "بطاطا")
    assert response["directGoodType"]["id"] == 171
    assert response["directGoodType"]["parentId"] == 12
    assert response["rootGoodType"]["id"] == 12

def test_unresolved_text_has_no_fallback_category(tmp_path) -> None:
    response = _classify(tmp_path, "نص غير محسوم")
    assert response["directGoodType"] is None
    assert response["rootGoodType"] is None
    assert response["requiresReview"] is True
    assert all(item["id"] != 31 for item in response["alternatives"])
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_api_contract.py::test_response_exposes_matched_type_and_root -q`

- [ ] **Step 3: Implement explicit schemas**

```python
class GoodTypeResponse(BaseModel):
    id: int
    name_ar: str = Field(alias="nameAr")
    name_en: str = Field(alias="nameEn")
    parent_id: int | None = Field(alias="parentId")
    rank: int

class RootGoodTypeResponse(BaseModel):
    id: int
    name_ar: str = Field(alias="nameAr")
    name_en: str = Field(alias="nameEn")
```

Define `directGoodType: GoodTypeResponse | null` and `rootGoodType: RootGoodTypeResponse | null`. Define `SearchMethod` as `EXACT | LEXICAL_VARIANT | FUZZY | SEMANTIC | RERANK` and extend `Reason` with `RERANKED_STRONG | OUT_OF_DISTRIBUTION | RERANKER_UNAVAILABLE`. Add `decisionConfidence: float | null` and `policyVersion: str`; keep raw method scores only inside `matchSignals`. Change feedback to `selectedGoodTypeId`. Because the main application has not integrated this API yet, update `/v1/classify` once and record the contract change in ADR-005; do not maintain two live versions.

- [ ] **Step 4: Verify GREEN and OpenAPI**

Run: `uv run pytest tests/test_api_contract.py -q`

Manual check: open `http://127.0.0.1:8000/docs` and confirm both hierarchy fields are documented.

### Task 6: Build a reproducible Dandan gold set and evaluator

**Files:**
- Create: `data/evaluation/goods_gold.jsonl`
- Create: `app/evaluation/runner.py`
- Test: `tests/test_evaluation_runner.py`

**Interfaces:**
- Consumes one JSON object per line with `text`, `expectedGoodTypeId`, `expectedDecision`, `forbiddenGoodTypeIds`, `forbiddenRootGoodTypeIds`, `language`, and `tags`.
- Produces model-comparable metrics from identical examples.

- [ ] **Step 1: Seed confirmed and safe-abstention cases**

```json
{"text":"بطاااااطس","expectedGoodTypeId":171,"expectedDecision":"ACCEPT","language":"AR","tags":["repeated-char","typo","short-fuzzy-guard"]}
{"text":"موية","expectedGoodTypeId":166,"expectedDecision":"ACCEPT","language":"AR","tags":["dialect","water"]}
{"text":"ماي","expectedGoodTypeId":166,"expectedDecision":"ACCEPT","language":"AR","tags":["dialect","water"]}
{"text":"مي","expectedGoodTypeId":166,"expectedDecision":"ACCEPT","language":"AR","tags":["dialect","short-term"]}
{"text":"بسكوتة سنيكرز","expectedGoodTypeId":14,"expectedDecision":"ACCEPT","language":"AR","tags":["morphology","brand"]}
{"text":"عمود كهربا","expectedGoodTypeId":56,"expectedDecision":"ACCEPT","language":"AR","tags":["colloquial"]}
{"text":"فوسفات","expectedGoodTypeId":null,"expectedDecision":"REVIEW","forbiddenRootGoodTypeIds":[12],"language":"AR","tags":["underspecified","must-review","ood"]}
{"text":"لمبة كهربائية","expectedGoodTypeId":null,"expectedDecision":"REVIEW","forbiddenGoodTypeIds":[159],"language":"AR","tags":["missing-catalog-alias","must-review","ood"]}
{"text":"كياس زبالة","expectedGoodTypeId":null,"expectedDecision":"REVIEW","forbiddenRootGoodTypeIds":[12],"language":"AR","tags":["business-label-required","must-review","ood"]}
{"text":"شحاطة بلاستيك","expectedGoodTypeId":147,"expectedDecision":"ACCEPT","language":"AR","tags":["dialect","footwear","gold-owner-approval"]}
{"text":"باب خشب","expectedGoodTypeId":54,"expectedDecision":"ACCEPT","language":"AR","tags":["short-valid-input","morphology","known-alias"]}
{"text":"شيء غير معروف","expectedGoodTypeId":null,"expectedDecision":"REVIEW","forbiddenGoodTypeIds":[31],"language":"AR","tags":["no-fallback","must-review","ood"]}
```

- [ ] **Step 2: Write the failing metric test**

```python
def test_runner_reports_precision_coverage_and_top3() -> None:
    report = evaluate(predictions, gold)
    assert report == {
        "acceptedPrecision": 1.0,
        "coverage": 0.5,
        "top1Accuracy": 0.5,
        "top3Recall": 1.0,
    }
```

- [ ] **Step 3: Implement the runner**

Count must-review rows as correct only when the classifier abstains. A forbidden ID/root is always a regression even when it appears as rank 1 under review. Emit metrics by tag as well as globally, plus p50/p95 latency and online call rate. Move a `business-label-required` row to an accepted label only after the catalog owner approves the target ID.

- [ ] **Step 4: Verify the evaluator**

Run: `uv run pytest tests/test_evaluation_runner.py -q`

Expected: metrics are reproducible from an immutable gold-set revision, and forbidden-category regressions fail the run.

### Task 7: Build source-level semantic documents and benchmark local retrievers

**Files:**
- Create: `app/search/documents.py`
- Modify: `app/search/semantic.py`
- Create: `scripts/evaluate_retrievers.py`
- Test: `tests/test_search_documents.py`

**Interfaces:**
- Consumes: Task 1 `Catalog.good_types` and Task 6 gold rows.
- Produces: one `GoodTypeDocument(good_type_id, root_good_type_id, text)` per selectable leaf row and comparable retriever reports.

- [ ] **Step 1: Write the failing document test**

```python
def test_document_is_source_specific_and_excludes_unreviewed_english() -> None:
    document = build_good_type_document(_catalog(), good_type_id=171)
    assert document.good_type_id == 171
    assert document.root_good_type_id == 12
    assert "الخضروات والفواكه" in document.text
    assert "بطاطا" in document.text
    assert "Electrical Appliances" not in document.text
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_search_documents.py -q`

- [ ] **Step 3: Implement source-level documents and index**

Build a compact document from the leaf Arabic name, root Arabic name, deduplicated representative aliases, and reviewed concept variants. Index and return results by `source_good_type_id`; do not concatenate unrelated children into a root document and do not index a parent as an eligible final result.

- [ ] **Step 4: Benchmark challengers on the same gold set**

Run:

```powershell
py scripts/evaluate_retrievers.py --model storage/models/intfloat-multilingual-e5-small
py scripts/evaluate_retrievers.py --model BAAI/bge-m3
py scripts/evaluate_retrievers.py --model jinaai/jina-embeddings-v3
```

Do not download a challenger until the current gold set and disk/RAM preflight are recorded. Select by Dandan `top3Recall`, not by public leaderboard alone.

### Task 8: Add a conditional online reranker

**Files:**
- Create: `app/rerank/base.py`
- Create: `app/rerank/cohere.py`
- Modify: `app/core/config.py`
- Modify: `app/classifier/service.py`
- Test: `tests/test_reranker.py`
- Test: `tests/test_classifier.py`

**Interfaces:**
- Produces: `RerankResult(good_type_id, relevance_score, rank)` from `rerank(query, candidate_documents)`.

- [ ] **Step 1: Write provider-independent failure and success tests**

```python
def test_ambiguous_local_candidates_are_reranked() -> None:
    reranker = FakeReranker([RerankResult(158, 0.91, 1), RerankResult(6, 0.72, 2)])
    result = _classifier(reranker=reranker).classify(request_id="p", text="فوسفات سماد")
    assert result.direct_good_type.good_type_id == 158

def test_reranker_timeout_forces_review() -> None:
    result = _classifier(reranker=TimeoutReranker()).classify(request_id="p", text="فوسفات")
    assert result.requires_review is True
    assert result.reason == "RERANKER_UNAVAILABLE"
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_reranker.py tests/test_classifier.py -q`

- [ ] **Step 3: Implement HTTPX adapter with strict response parsing**

Configure `DANDAN_RERANK_PROVIDER`, `DANDAN_COHERE_API_KEY`, `DANDAN_RERANK_MODEL=rerank-v4.0-pro`, and `DANDAN_RERANK_TIMEOUT_MS=1200`. Send only normalized goods text and catalog category documents. Never log the API key or provider authorization header.

- [ ] **Step 4: Route only unresolved traffic**

Skip online calls for unambiguous exact aliases. Call the reranker for weak, conflicting, out-of-distribution, or unknown inputs. Cache category documents, not user decisions.

- [ ] **Step 5: Verify GREEN**

Run: `uv run pytest tests/test_reranker.py tests/test_classifier.py -q`

Manual benchmark: compare `rerank-v4.0-fast` and `rerank-v4.0-pro` on the same gold-set revision, including cost and p95 latency.

### Task 9: Calibrate acceptance instead of trusting raw scores

**Files:**
- Create: `app/classifier/calibration.py`
- Modify: `app/classifier/policy.py`
- Modify: `scripts/evaluate_promotion.py`
- Test: `tests/test_calibration.py`
- Test: `tests/test_policy.py`

**Interfaces:**
- Consumes held-out features: exact/fuzzy/semantic/rerank scores, margins, method agreement, language, token count, and OOD flags.
- Produces `AcceptanceDecision(accept, calibrated_probability, policy_version)`.

- [ ] **Step 1: Write failing selective-policy tests**

```python
def test_high_raw_similarity_without_calibration_is_not_auto_accepted() -> None:
    decision = policy.decide(_candidate(semantic=0.99), calibrator=None)
    assert decision.requires_review is True

def test_threshold_is_selected_by_precision_not_accuracy() -> None:
    threshold = select_threshold(rows, minimum_precision=0.99)
    assert precision_at(rows, threshold) >= 0.99
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_calibration.py tests/test_policy.py -q`

- [ ] **Step 3: Implement a small calibrated selector**

Use the existing offline ML dependencies. Fit logistic regression followed by isotonic calibration only when the calibration split is sufficiently large; otherwise use conservative route-specific thresholds and report `policyVersion=rules-v1`.

- [ ] **Step 4: Add promotion gates**

Promotion requires measured accepted precision, coverage floor, category-stratified recall, and no regression in Arabic typo/OOD slices. The artifact stays candidate-only until reviewed.

- [ ] **Step 5: Verify GREEN**

Run: `uv run pytest tests/test_calibration.py tests/test_policy.py tests/test_promotion.py -q`

### Task 10: Migrate feedback and thin ML to good-type labels

**Files:**
- Modify: `app/training/feedback_dataset.py`
- Modify: `app/training/supervised.py`
- Modify: `app/training/promotion.py`
- Modify: `app/classifier/events.py`
- Test: `tests/test_feedback_dataset.py`
- Test: `tests/test_supervised_training.py`

**Interfaces:**
- Consumes `selectedGoodTypeId` verified corrections.
- Produces source-level candidate artifacts; never mutates the online classifier during a request.

- [ ] **Step 1: Write failing source-label tests**

```python
def test_verified_feedback_preserves_child_label() -> None:
    rows, _ = build_verified_feedback_dataset(events_for(selected_good_type_id=171))
    assert rows[0]["selectedGoodTypeId"] == 171
```

- [ ] **Step 2: Verify RED**

Run: `uv run pytest tests/test_feedback_dataset.py tests/test_supervised_training.py -q`

- [ ] **Step 3: Migrate field names and artifact format**

Change `rootGoodTypeId` training labels to `goodTypeId` and version the artifact as `dandan-feedback-good-type-tfidf-v2`. Reject mixed v1/v2 datasets rather than guessing label semantics.

- [ ] **Step 4: Verify GREEN**

Run: `uv run pytest tests/test_feedback_dataset.py tests/test_supervised_training.py tests/test_promotion.py -q`

### Task 11: Update the engineering demo and end-to-end gates

**Files:**
- Modify: `app/api/static/demo.html`
- Modify: `app/api/static/demo.css`
- Modify: `app/api/static/demo.js`
- Test: `tests/test_api_contract.py`

**Interfaces:**
- Displays actual `directGoodType`, `rootGoodType`, local evidence, reranker usage, nullable calibrated decision confidence, policy version, review decision, latency, and catalog/model versions. Raw method scores are labelled evidence scores, never accuracy.

- [ ] **Step 1: Add contract assertions before UI edits**

```python
def test_demo_assets_reference_new_hierarchy_contract() -> None:
    response = _request("GET", "/")
    assert "directGoodType" in response.text
    assert "rootGoodType" in response.text
```

- [ ] **Step 2: Show the execution cascade visually**

Render:

```text
INPUT → NORMALIZE → EXACT/FUZZY → HYBRID → RERANK? → CALIBRATE → ACCEPT/REVIEW
```

Every displayed value must come from the current API response. On a failed request, clear the previous result before rendering the error.

- [ ] **Step 3: Run complete verification**

Run:

```powershell
uv run pytest -q
uvx ruff check .
py -m compileall -q app tests
uv lock --check
```

Manual checks:

- `بطاااااطس` → good type 171, root 12; the two-letter `بط` candidate cannot win via fuzzy matching.
- `موية`, `ماي`, `مي` → good type/root 166 through dialect-aware retrieval.
- `عمود كهربا` → good type 56, root 34.
- `فوسفات` → alternatives include plausible fertilizer/mining types and remains review unless context resolves it.
- `لمبة كهربائية` → never auto-accepts generator 159; it remains review until the catalog owner approves its direct type or the catalog supplies evidence.
- `كياس زبالة` → never returns food; it remains review until waste/cleaning/plastic ownership is defined.
- `بسكوتة سنيكرز` retrieves good type 14; `شحاطة بلاستيك` retrieves 147 after catalog-owner gold approval; `باب خشب` retrieves the existing alias owner 54. None is rejected as meaningless input.
- unknown input → `directGoodType=null`, `rootGoodType=null`; ID 31 never appears as a fallback.
- exact known alias never calls the online reranker.
- simulated provider timeout returns local alternatives with review.
- validation remains disabled for the current exploratory session.

## Delivery Checkpoints

### Checkpoint A — Tasks 1–5

- Source-level taxonomy and API work end to end without changing model provider.
- Existing root is still available explicitly.
- Every reported regression case has an automated acceptance, abstention, or forbidden-result test.

### Checkpoint B — Tasks 6–9

- Every model/provider is compared on the same immutable gold-set revision.
- Acceptance threshold is selected from precision–coverage evidence.
- Online failure cannot produce an auto-accepted result.

### Checkpoint C — Tasks 10–11

- Corrections train source-level candidates offline.
- Demo explains the real route and hierarchy.
- Full tests, lint, compile, lock, API, and browser checks pass.

## Explicitly Deferred

- Agent/LangGraph request path.
- Vector database for 103 catalog rows.
- Live internet search during driver classification.
- Automatic production retraining from individual clicks.
- Formal five-nines claim before sufficient independent evidence exists.
- Independent verifier/LLM call after reranking; add it only if gold-set evidence shows the reranker cannot reach the required precision–coverage point.
