---
title: Saudi Goods Root Category Classifier
emoji: 📦
colorFrom: green
colorTo: emerald
sdk: docker
app_port: 7860
pinned: false
---

# Saudi Goods Root Category Classifier (دندن)

High-precision hierarchical goods classifier for the Saudi logistics and transport market.

## Architecture
- **Exact / Morphological Lookup**: Direct catalog token indexing.
- **Fuzzy Matcher + TF-IDF**: Weighted edit distance with Arabic dialectal consonant shifts and token mass coverage.
- **Semantic Engine (FAISS + E5-Small)**: Dense vector search over 90 Saudi market category contexts (384 dimensions).
- **Hybrid Decision Policy**: Multi-signal rank fusion with automated quality gates and human-in-the-loop review routing.

## Live Endpoints
- **Web UI**: `/` or `/v19` or `/trace`
- **Classify API**: `POST /demo/classify`
- **Health Check**: `GET /healthz`
