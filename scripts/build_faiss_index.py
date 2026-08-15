#!/usr/bin/env python3
"""Dual-Stream Disentangled Semantic Index Builder.
Builds two orthogonal, high-precision semantic search indices for all 90 Saudi categories:
1. Stream 1 (Concept Index): Pure ontological identity of the 90 categories (Zero noise).
2. Stream 2 (Evidence Index): Fine-grained trade terms, regional cultivars, dialect names, and brands.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.catalog.importer import load_catalog_artifact


def get_embedding_function(model_choice: str, gemini_api_key: str = ""):
    raw_key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")
    key = raw_key.strip("'\" \t\r\n")
    use_gemini = model_choice.lower() in ("google-gemini", "gemini", "text-embedding-004")

    if use_gemini and key:
        import urllib.request
        masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
        print(f"🔑 Using Gemini API Key: {masked_key} (length: {len(key)})")

        def embed_single_or_batch(texts: list[str], is_query: bool = False) -> np.ndarray:
            task_type = "RETRIEVAL_QUERY" if is_query else "RETRIEVAL_DOCUMENT"
            all_vecs = []
            batch_size = 50
            for i in range(0, len(texts), batch_size):
                chunk = texts[i : i + batch_size]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={key}"
                requests_body = [
                    {
                        "model": "models/text-embedding-004",
                        "content": {"parts": [{"text": t}]},
                        "taskType": task_type,
                    }
                    for t in chunk
                ]
                req_data = json.dumps({"requests": requests_body}).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                )
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        res = json.loads(resp.read().decode("utf-8"))
                        for emb in res.get("embeddings", []):
                            all_vecs.append(emb["values"])
                except urllib.error.HTTPError as http_err:
                    err_body = http_err.read().decode("utf-8", errors="ignore")
                    raise RuntimeError(f"Google Gemini API error ({http_err.code}): {err_body}")
                except Exception as exc:
                    raise RuntimeError(f"Gemini request failed: {exc}")
                time.sleep(0.05)

            vecs = np.array(all_vecs, dtype=np.float32)
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return vecs / norms

        try:
            test_vec = embed_single_or_batch(["test"], is_query=True)
            dim = int(test_vec.shape[1])
            print(f"✅ Connected to Google Gemini Embeddings via REST API (dim: {dim})")
            return embed_single_or_batch, dim, "google-gemini"
        except Exception as test_exc:
            print(f"⚠️ Gemini Connection failed: {test_exc}")
            print("🔄 Falling back automatically to 'BAAI/bge-m3' (Runs 100% on GPU with no API key needed)...")
            model_choice = "BAAI/bge-m3"

    if use_gemini and not key:
        print("⚠️ GEMINI_API_KEY was not provided. Automatically switching to 'BAAI/bge-m3' (Runs 100% free on Colab GPU with no API key needed)!")
        model_choice = "BAAI/bge-m3"

    from sentence_transformers import SentenceTransformer
    print(f"🧠 Loading SentenceTransformer on GPU/CPU: {model_choice}...")
    model = SentenceTransformer(model_choice)
    is_e5 = "e5" in model_choice.lower()

    def embed_fn(texts: list[str], is_query: bool = False) -> np.ndarray:
        if is_e5:
            prefix = "query: " if is_query else "passage: "
            texts = [prefix + t if not t.startswith(prefix) else t for t in texts]
        vecs = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
        return np.array(vecs, dtype=np.float32)

    test_vec = model.encode(["test"], normalize_embeddings=True)
    dim = int(test_vec.shape[1])
    print(f"✅ Loaded SentenceTransformer model: {model_choice} (dim: {dim})")
    return embed_fn, dim, model_choice


def build_dual_stream_faiss_index(
    catalog_path: str = "storage/catalog/catalog.json",
    contexts_path: str = "storage/catalog/saudi_market_category_contexts.json",
    model_choice: str = "storage/models/intfloat-multilingual-e5-small",
    gemini_api_key: str = "",
    output_dir: str = "storage/semantic",
) -> None:
    print("=" * 88)
    print("🚀 BUILDING DUAL-STREAM DISENTANGLED FAISS RETRIEVAL ARTIFACTS")
    print(f"🤖 Selected Engine: {model_choice}")
    print("=" * 88)

    catalog = load_catalog_artifact(catalog_path)
    leaves = [g for g in catalog.good_types.values() if len(g.child_ids) == 0]
    
    with open(contexts_path, "r", encoding="utf-8") as f:
        contexts = json.load(f)

    print(f"📖 Loaded {len(leaves)} leaf categories & {len(contexts)} market contexts.")

    embed_fn, embedding_dim, model_tag = get_embedding_function(model_choice, gemini_api_key)

    # -------------------------------------------------------------------------
    # STREAM 1: PURE CONCEPT VECTORS (Canonical Identity - Zero Ambient Noise)
    # -------------------------------------------------------------------------
    print("\n🎯 [STREAM 1] Encoding Pure Category Concepts (90 canonical classes)...")
    concept_docs: list[dict] = []
    for leaf in leaves:
        leaf_id = leaf.id
        root_id = catalog.root_id_for(leaf_id)
        root = catalog.root(root_id)
        ctx = contexts.get(str(leaf_id), {})

        # Precise concept text without wordy filler
        concept_ar = f"تصنيف بضائع {leaf.name_ar} التابع للمجموعة الرئيسية {root.name_ar}"
        concept_en = f"Goods Category {leaf.name_en or leaf.name_ar} under Root Category {root.name_en or root.name_ar}"
        
        # Primary anchor synonyms (first 3 direct terms)
        primary_terms = ", ".join(ctx.get("trade_terms_ar", [])[:4])
        if primary_terms:
            concept_text = f"{concept_ar}. المنتجات الأساسية: {primary_terms}. {concept_en}."
        else:
            concept_text = f"{concept_ar}. {concept_en}."

        concept_docs.append({
            "root_good_type_id": root_id,
            "source_good_type_id": leaf_id,
            "name_ar": leaf.name_ar,
            "name_en": leaf.name_en or "",
            "root_name_ar": root.name_ar,
            "root_name_en": root.name_en or "",
            "text": concept_text,
        })

    concept_texts = [d["text"] for d in concept_docs]
    concept_embeddings = embed_fn(concept_texts, is_query=False)
    print(f"✅ Stream 1 Concepts encoded: {len(concept_embeddings)} vectors (dim: {embedding_dim})")

    # -------------------------------------------------------------------------
    # STREAM 2: DEEP EVIDENCE VECTORS (Trade Terms, Cultivars, Brands, Dialects)
    # -------------------------------------------------------------------------
    print("\n🔍 [STREAM 2] Encoding Fine-Grained Evidence & Trade Manifest...")
    evidence_docs: list[dict] = []
    for leaf in leaves:
        leaf_id = leaf.id
        root_id = catalog.root_id_for(leaf_id)
        root = catalog.root(root_id)
        ctx = contexts.get(str(leaf_id), {})

        trade_terms_ar = ctx.get("trade_terms_ar", [])
        trade_terms_en = ctx.get("trade_terms_en", [])
        key_brands = ctx.get("key_brands", [])

        # Individual trade terms
        for term in trade_terms_ar:
            if not term or len(term.strip()) < 2:
                continue
            evidence_docs.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "TRADE_TERM_AR",
                "matched_term": term,
                "text": f"{term} - {leaf.name_ar} ({root.name_ar})",
            })

        for term_en in trade_terms_en:
            if not term_en or len(term_en.strip()) < 2:
                continue
            evidence_docs.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "TRADE_TERM_EN",
                "matched_term": term_en,
                "text": f"{term_en} - {leaf.name_en or leaf.name_ar} ({root.name_en or root.name_ar})",
            })

        # Key brands & cultivars
        for brand in key_brands:
            if not brand or len(brand.strip()) < 2:
                continue
            evidence_docs.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "BRAND_CULTIVAR",
                "matched_term": brand,
                "text": f"ماركة وصنف {brand} ضمن {leaf.name_ar}",
            })

    evidence_texts = [d["text"] for d in evidence_docs]
    evidence_embeddings = embed_fn(evidence_texts, is_query=False)
    print(f"✅ Stream 2 Evidence encoded: {len(evidence_embeddings):,} vectors (dim: {embedding_dim})")

    # -------------------------------------------------------------------------
    # COMPILE DUAL FAISS INDICES & METADATA
    # -------------------------------------------------------------------------
    import faiss
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Concept FAISS Index (Stream 1)
    concept_index = faiss.IndexFlatIP(embedding_dim)
    concept_index.add(concept_embeddings)
    faiss.write_index(concept_index, str(out_dir / "catalog_concept_faiss.index"))

    with open(out_dir / "catalog_concept_metadata.json", "w", encoding="utf-8") as f:
        json.dump(concept_docs, f, ensure_ascii=False, indent=2)

    # 2. Evidence FAISS Index (Stream 2)
    evidence_index = faiss.IndexFlatIP(embedding_dim)
    evidence_index.add(evidence_embeddings)
    faiss.write_index(evidence_index, str(out_dir / "catalog_evidence_faiss.index"))

    # Also save standard catalog_faiss.index for backward-compatibility
    faiss.write_index(evidence_index, str(out_dir / "catalog_faiss.index"))

    with open(out_dir / "catalog_evidence_metadata.json", "w", encoding="utf-8") as f:
        json.dump(evidence_docs, f, ensure_ascii=False, indent=2)
    with open(out_dir / "catalog_faiss_metadata.json", "w", encoding="utf-8") as f:
        json.dump(evidence_docs, f, ensure_ascii=False, indent=2)

    # 3. Save combined NPZ artifact
    np.savez_compressed(
        out_dir / "catalog_dual_stream_vectors.npz",
        concept_embeddings=concept_embeddings,
        concept_metadata=json.dumps(concept_docs, ensure_ascii=False),
        evidence_embeddings=evidence_embeddings,
        evidence_metadata=json.dumps(evidence_docs, ensure_ascii=False),
        model_tag=model_tag,
        embedding_dim=embedding_dim,
    )

    print("\n" + "=" * 88)
    print("🎉 DUAL-STREAM ARTIFACTS SUCCESSFULLY GENERATED!")
    print(f"📦 Concept Index:   {out_dir / 'catalog_concept_faiss.index'} ({len(concept_docs)} vectors)")
    print(f"📦 Evidence Index:  {out_dir / 'catalog_evidence_faiss.index'} ({len(evidence_docs):,} vectors)")
    print(f"📦 NPZ Bundle:      {out_dir / 'catalog_dual_stream_vectors.npz'}")
    print("=" * 88 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build dual-stream FAISS index for Saudi goods classifier.")
    parser.add_argument(
        "--model",
        type=str,
        default="storage/models/intfloat-multilingual-e5-small",
        help="Model choice: 'BAAI/bge-m3', 'storage/models/intfloat-multilingual-e5-small', 'intfloat/multilingual-e5-large', or 'google-gemini'",
    )
    parser.add_argument(
        "--gemini-api-key",
        type=str,
        default="",
        help="Google Gemini API key (if --model is google-gemini)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="storage/semantic",
        help="Output directory for dual-stream artifacts.",
    )
    args = parser.parse_args()

    build_dual_stream_faiss_index(
        model_choice=args.model,
        gemini_api_key=args.gemini_api_key,
        output_dir=args.output_dir,
    )
