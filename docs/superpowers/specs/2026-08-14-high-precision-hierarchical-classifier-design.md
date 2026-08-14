# High-Precision Hierarchical Goods Classifier Design

## Objective

Build a selective classifier that assigns free text to its closest categorical row in `good_types` and returns that row plus its root. It does not search, create, or match product entities. Deterministic evidence precedes semantic inference, and the service refuses automatic acceptance when the evidence cannot support the target precision.

`99.999%` is treated as an aspirational precision target for **accepted** predictions, not a promise for every request. With zero observed errors, approximately 300,000 independent accepted examples are required even for a rough one-sided 95% upper error bound near `0.001%`. Until that evidence exists, the service reports measured precision and coverage without claiming five-nines accuracy.

## Taxonomy Contract

The SQL catalog has 103 rows, 37 roots, 66 direct children, and a maximum depth of one edge. `common_names` belong to a specific `good_types` row. Therefore classification targets `source_good_type_id`, while the root remains explicit context.

In business language, **الأب التصنيفي الأول** means the closest selectable categorical row that owns the matched name or alias. The API calls this `directGoodType` to avoid confusing it with a product match or with the database `parentId`. A row that has children is routing context and cannot be the final `directGoodType`; the classifier must select one of its leaf children or abstain. A root with no children remains selectable.

Example:

```text
12 · مواد غذائية
└── 171 · الخضروات والفواكه
    └── common_name: بطاطا
```

The response returns:

```json
{
  "directGoodType": {
    "id": 171,
    "nameAr": "الخضروات والفواكه",
    "nameEn": "Electrical Appliances",
    "parentId": 12,
    "rank": 1
  },
  "rootGoodType": {
    "id": 12,
    "nameAr": "مواد غذائية",
    "nameEn": "Food Items"
  }
}
```

When the service abstains, both `directGoodType` and `rootGoodType` are `null`; ranked leaf alternatives remain available for review. ID `31` is never used as a fallback. The old fallback represented "unknown pending manual correction" and polluted classification data; this service replaces that behavior with explicit abstention.

The inconsistent English value above is preserved from the source database and must be audited separately; the classifier must never silently rewrite catalog data. Unreviewed English labels remain visible as source data but are excluded from lexical and semantic evidence by default, because a corrupt translation must not steer classification. Multilingual retrieval can match an English query against the reviewed Arabic category document until English labels are approved.

## Decision Cascade

```text
API schema
  → conservative normalization + retrieval-only spelling/dialect variants
  → exact/alias match
  → length-aware fuzzy match
  → local hybrid retrieval
  → online multilingual reranker for unresolved requests
  → calibrated accept / review policy
```

### Deterministic path

- Exact and catalog-anchored fuzzy retrieval run before the linguistic quality gate.
- Arabic character runs of three or more produce a retrieval-only collapsed variant, so `بطاااااطس` can retrieve `بطاطس` without altering the audited raw input.
- Conservative Arabic morphology produces retrieval-only variants, such as `بسكوتة → بسكوت`; derived variants carry their own evidence type and do not masquerade as raw exact matches.
- Partial fuzzy matching is disabled when either compared token is shorter than four characters. A two-character overlap cannot become a strong lexical anchor, and length-incompatible tokens cannot vote together. This prevents `بط` from defeating `بطاطس`.
- An unambiguous exact alias can be accepted without any model call.
- Short aliases remain valid only as full exact matches; the rule blocks fuzzy substring leakage, not genuine catalog entries such as exact `بط`.
- Duplicate aliases are preserved per `source_good_type_id` and flagged ambiguous across direct good types, including duplicates under the same root.

### Semantic path

- Candidate documents are built per `source_good_type_id`, not per root.
- Each document contains the Arabic/English child name, root name, representative aliases, and reviewed category description.
- Dialect variants are retrieval evidence, not destructive rewrites. Catalog aliases and a versioned concept lexicon connect forms such as `موية`, `ماي`, `مي`, `مويه`, `ماء`, and `مياه`; multilingual subword retrieval and reranking cover unseen spelling/context variants. Verified feedback extends the lexicon offline rather than adding request-time exceptions.
- Benchmark the current E5-small against BGE-M3 and Jina Embeddings v3 on Dandan's gold set; no replacement is promoted from generic benchmarks alone.
- For unresolved inputs, use a provider-isolated online reranker. The first candidate is Cohere `rerank-v4.0-pro`; `rerank-v4.0-fast` is the latency challenger.
- If the online service fails or times out, the service keeps local candidates and forces `requiresReview=true`.
- Live internet search is not part of request-time classification.

### Decision safety

- Raw cosine/fuzzy scores are evidence, not probabilities.
- The API and demo never label a cosine, fuzzy, or rerank score as "accuracy". `decisionConfidence` is nullable and appears only when produced by a promoted calibrator.
- A calibrator learns acceptance probability from held-out Dandan examples using method scores, rank margin, language, token count, local/online agreement, and out-of-distribution indicators.
- Auto-accept requires a calibrated threshold established from the precision–coverage curve.
- A parent row with children is never accepted as the final type. Exact input `مواد غذائية` routes to its children and requires review until one child is supported.
- No fallback category exists. Low evidence returns `directGoodType=null`, `rootGoodType=null`, and `requiresReview=true`; in particular it never returns ID 31 merely because the text is unknown.
- Unknown or underspecified inputs such as `فوسفات` may return ranked candidates but remain under review when fertilizer versus mining material cannot be distinguished.
- A nearest semantic neighbor is never sufficient for auto-accepting an out-of-catalog item. `لمبة كهربائية` must not become generator `159`, and `كياس زبالة` must not become food, merely because those are the nearest available vectors.

## Learning Loop

- Demo and application feedback records `selectedGoodTypeId`, reviewer identity/source, catalog version, model version, and original request evidence.
- One click never retrains production directly.
- Verified corrections are deduplicated, quarantined on conflict, split temporally, and evaluated offline.
- A champion/challenger report gates every promotion. Thin ML remains offline until enough verified data exists.

## Quality Measurement

Primary metrics:

- `acceptedPrecision`: correctness among `requiresReview=false`.
- `coverage`: fraction automatically accepted.
- `top1Accuracy` and `top3Recall` across all requests.
- selective risk–coverage curve.
- calibration error, p50/p95 latency, online call rate, and cost per 1,000 requests.

Gold-set strata include Arabic dialects, English, mixed text, brands, transliteration, repeated characters, short terms, typos, unseen goods, multi-category text, and deliberate noise. Mandatory regressions include `بطاااااطس`, `موية/ماي/مي`, `بسكوتة سنيكرز`, `كياس زبالة`, `شحاطة بلاستيك`, `باب خشب`, `فوسفات`, `عمود كهربا`, and `لمبة كهربائية`.

Initial release gates:

- No automatic promotion without at least 1,000 independently reviewed examples spanning every active category.
- `acceptedPrecision >= 99.0%` on temporal holdout for the first controlled release.
- Raise the threshold only with enough new evidence; never market `99.999%` until its statistical evidence requirement is met.

## External Basis

- BGE-M3 supports dense, sparse, and multi-vector retrieval and recommends hybrid retrieval followed by reranking: https://huggingface.co/BAAI/bge-m3
- Cohere Rerank 4 is multilingual and explicitly supports Arabic: https://docs.cohere.com/docs/rerank-overview
- Conformal risk control provides a model-agnostic direction for post-MVP statistical risk control: https://arxiv.org/html/2208.02814
