#!/usr/bin/env python3
"""Builds high-precision FAISS Vector Index artifact for all 90 Saudi Market Categories.
Supports multiple embedding engines:
1. BAAI/bge-m3 (1024-dim, State-of-the-art Open Source, Recommended)
2. intfloat/multilingual-e5-small (384-dim, Ultra-Fast Local)
3. intfloat/multilingual-e5-large (1024-dim)
4. google-gemini (768-dim, Google Gemini Embeddings API text-embedding-004)
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
    key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")
    use_gemini = model_choice.lower() in ("google-gemini", "gemini", "text-embedding-004")

    if use_gemini and key:
        import urllib.request

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
                except Exception as exc:
                    raise RuntimeError(f"Gemini REST embedding API error: {exc}. Ensure your GEMINI_API_KEY is valid.")
                time.sleep(0.05)

            vecs = np.array(all_vecs, dtype=np.float32)
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return vecs / norms

        test_vec = embed_single_or_batch(["test"], is_query=True)
        dim = int(test_vec.shape[1])
        print(f"✅ Connected to Google Gemini Embeddings via REST API (dim: {dim})")
        return embed_single_or_batch, dim, "google-gemini"

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


def build_faiss_index(
    catalog_path: str = "storage/catalog/catalog.json",
    contexts_path: str = "storage/catalog/saudi_market_category_contexts.json",
    model_choice: str = "BAAI/bge-m3",
    gemini_api_key: str = "",
    output_index_path: str = "storage/semantic/catalog_faiss.index",
    output_meta_path: str = "storage/semantic/catalog_faiss_metadata.json",
) -> None:
    print("=" * 80)
    print("🚀 BUILDING HIGH-PRECISION FAISS VECTOR INDEX FOR 90 SAUDI MARKET CATEGORIES")
    print(f"🤖 Selected Engine: {model_choice}")
    print("=" * 80)

    catalog = load_catalog_artifact(catalog_path)
    leaves = [g for g in catalog.good_types.values() if len(g.child_ids) == 0]
    
    with open(contexts_path, "r", encoding="utf-8") as f:
        contexts = json.load(f)

    print(f"📖 Loaded {len(leaves)} leaf categories & {len(contexts)} market contexts.")

    documents: list[dict] = []

    # 1. High-Density Contextual Documents for all 90 categories
    for leaf in leaves:
        leaf_id = leaf.id
        root_id = catalog.root_id_for(leaf_id)
        root = catalog.root(root_id)
        ctx = contexts.get(str(leaf_id), {})

        market_ar = ctx.get("market_context_ar", "")
        market_en = ctx.get("market_context_en", "")
        trade_terms = ctx.get("trade_terms_ar", [])
        brands = ctx.get("key_brands", [])
        containers = ctx.get("allowed_containers", [])

        # (a) Full Category Domain Profile Document
        doc_text_ar = (
            f"تصنيف بضائع {leaf.name_ar} (المجموعة الأساسية: {root.name_ar}). "
            f"{market_ar} "
            f"أبرز السلع والمنتجات: {', '.join(trade_terms[:15])}. "
            f"الماركات والشركات: {', '.join(brands)}. "
            f"طرق التعبئة والشحن: {', '.join(containers)}."
        )
        documents.append({
            "root_good_type_id": root_id,
            "source_good_type_id": leaf_id,
            "source_type": "CATEGORY_DOMAIN_PROFILE",
            "matched_term": leaf.name_ar,
            "text": doc_text_ar,
        })

        if market_en:
            doc_text_en = (
                f"Goods category {leaf.name_en} (Root Category: {root.name_en}). "
                f"{market_en} "
                f"Key products: {', '.join(ctx.get('trade_terms_en', [])[:15])}."
            )
            documents.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "CATEGORY_DOMAIN_PROFILE_EN",
                "matched_term": leaf.name_en or leaf.name_ar,
                "text": doc_text_en,
            })

        # (b) Individual High-Precision Trade Terms (Arabic)
        for term in trade_terms:
            if not term or len(term.strip()) < 2:
                continue
            documents.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "MARKET_TRADE_TERM_AR",
                "matched_term": term,
                "text": f"{term} ضمن بضائع {leaf.name_ar} وتصنيف {root.name_ar}",
            })

        # (c) Individual High-Precision Trade Terms (English)
        for term_en in ctx.get("trade_terms_en", []):
            if not term_en or len(term_en.strip()) < 2:
                continue
            documents.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "MARKET_TRADE_TERM_EN",
                "matched_term": term_en,
                "text": f"{term_en} under {leaf.name_en or leaf.name_ar} and root {root.name_en or root.name_ar}",
            })

    print(f"📊 Total rich contextual passages to encode: {len(documents):,}")

    embed_fn, embedding_dim, model_tag = get_embedding_function(model_choice, gemini_api_key)

    raw_texts = [d["text"] for d in documents]
    embeddings = embed_fn(raw_texts, is_query=False)

    print(f"📐 Embedding Dimension: {embedding_dim}, Vectors: {len(embeddings)}")
    
    # 2. Build FAISS Index (Cosine via IndexFlatIP with normalized vectors)
    import faiss
    print("⚡ Initializing FAISS IndexFlatIP...")
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(embeddings)
    print(f"✅ FAISS Index contains {index.ntotal} vectors.")

    # 3. Save FAISS Index & Metadata
    out_idx = Path(output_index_path)
    out_idx.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out_idx))

    out_meta = Path(output_meta_path)
    metadata_json = []
    for d in documents:
        metadata_json.append({
            "root_good_type_id": d["root_good_type_id"],
            "source_good_type_id": d["source_good_type_id"],
            "source_type": d["source_type"],
            "matched_term": d["matched_term"],
            "text": d["text"],
            "embedding_model": model_tag,
            "embedding_dim": embedding_dim,
        })

    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump(metadata_json, f, ensure_ascii=False, indent=2)

    # 4. Save npz backup
    npz_path = out_idx.parent / "catalog_vector_index.npz"
    np.savez_compressed(
        npz_path,
        embeddings=embeddings,
        metadata_json=json.dumps(metadata_json, ensure_ascii=False),
    )

    print("\n" + "=" * 80)
    print("🎉 FAISS VECTOR INDEX & CONTEXT ARTIFACTS SUCCESSFULLY BUILT!")
    print(f"💾 FAISS Index:    {output_index_path} ({out_idx.stat().st_size / (1024*1024):.2f} MB)")
    print(f"📁 Metadata JSON:  {output_meta_path} ({out_meta.stat().st_size / 1024:.2f} KB)")
    print(f"📦 NPZ Index:      {npz_path} ({npz_path.stat().st_size / (1024*1024):.2f} MB)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build dense FAISS index for Saudi goods classifier.")
    parser.add_argument(
        "--model",
        type=str,
        default="BAAI/bge-m3",
        help="Model choice: 'BAAI/bge-m3', 'storage/models/intfloat-multilingual-e5-small', 'intfloat/multilingual-e5-large', or 'google-gemini'",
    )
    parser.add_argument(
        "--gemini-api-key",
        type=str,
        default="",
        help="Google Gemini API key (if --model is google-gemini)",
    )
    parser.add_argument(
        "--output-index",
        type=str,
        default="storage/semantic/catalog_faiss.index",
        help="Output path for FAISS index file.",
    )
    parser.add_argument(
        "--output-metadata",
        type=str,
        default="storage/semantic/catalog_faiss_metadata.json",
        help="Output path for metadata JSON file.",
    )
    args = parser.parse_args()

    build_faiss_index(
        model_choice=args.model,
        gemini_api_key=args.gemini_api_key,
        output_index_path=args.output_index,
        output_meta_path=args.output_metadata,
    )
