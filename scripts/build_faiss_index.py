#!/usr/bin/env python3
"""Builds high-precision FAISS Vector Index artifact for all 90 Saudi Market Categories.
Uses rich contextual passage encoding with intfloat/multilingual-e5-small.
Stores:
1. storage/semantic/catalog_faiss.index (FAISS IndexFlatIP)
2. storage/semantic/catalog_faiss_metadata.json (companion document metadata)
"""

from __future__ import annotations
import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.catalog.importer import load_catalog_artifact


def build_faiss_index(
    catalog_path: str = "storage/catalog/catalog.json",
    contexts_path: str = "storage/catalog/saudi_market_category_contexts.json",
    model_path: str = "storage/models/intfloat-multilingual-e5-small",
    output_index_path: str = "storage/semantic/catalog_faiss.index",
    output_meta_path: str = "storage/semantic/catalog_faiss_metadata.json",
) -> None:
    print("=" * 80)
    print("🚀 BUILDING HIGH-PRECISION FAISS VECTOR INDEX FOR 90 SAUDI MARKET CATEGORIES")
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
            f"passage: تصنيف بضائع {leaf.name_ar} (المجموعة الأساسية: {root.name_ar}). "
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
                f"passage: Category {leaf.name_en} under {root.name_en}. "
                f"{market_en} "
                f"Key trade items: {', '.join(ctx.get('trade_terms_en', []))}."
            )
            documents.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "CATEGORY_DOMAIN_PROFILE_EN",
                "matched_term": leaf.name_en,
                "text": doc_text_en,
            })

        # (b) Contextualized Concept Documents (Never index raw isolated words!)
        # Each trade term is embedded inside a meaningful, domain-grounded sentence
        for term in trade_terms:
            concept_passage = (
                f"passage: شحنة وبضائع {term}، تتبع لتصنيف {leaf.name_ar} ضمن قطاع {root.name_ar} في السوق السعودي."
            )
            documents.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "CONCEPT_PASSAGE",
                "matched_term": term,
                "text": concept_passage,
            })

        # (c) Add contextual terms from catalog.selectable_terms
        catalog_terms = [t.raw_term for t in catalog.selectable_terms if t.source_good_type_id == leaf_id]
        for cterm in list(dict.fromkeys(catalog_terms))[:20]:
            if cterm not in trade_terms:
                concept_passage = (
                    f"passage: منتج {cterm} ضمن تصنيف {leaf.name_ar} - {root.name_ar}."
                )
                documents.append({
                    "root_good_type_id": root_id,
                    "source_good_type_id": leaf_id,
                    "source_type": "CATALOG_TERM_PASSAGE",
                    "matched_term": cterm,
                    "text": concept_passage,
                })

    print(f"📊 Total rich contextual passages to encode: {len(documents):,}")

    print(f"🧠 Loading SentenceTransformer from {model_path}...")
    model = SentenceTransformer(model_path)

    passages = [doc["text"] for doc in documents]
    print(f"⏳ Encoding {len(passages):,} passages in batches of 64...")
    embeddings = model.encode(
        passages,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    embeddings = np.asarray(embeddings, dtype=np.float32)

    dim = embeddings.shape[1]
    print(f"📐 Embedding Dimension: {dim}, Vectors: {embeddings.shape[0]}")

    # Build FAISS IndexFlatIP (Inner Product on L2-normalized vectors == Cosine Similarity)
    print("⚡ Initializing FAISS IndexFlatIP...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"✅ FAISS Index contains {index.ntotal} vectors.")

    out_idx = Path(output_index_path)
    out_idx.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out_idx))

    out_meta = Path(output_meta_path)
    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    # Also maintain compatibility by exporting catalog_vector_index.npz
    npz_path = Path("storage/semantic/catalog_vector_index.npz")
    np.savez_compressed(
        npz_path,
        embeddings=embeddings,
        metadata=np.array([json.dumps(documents, ensure_ascii=False)]),
    )

    print("\n" + "=" * 80)
    print("🎉 FAISS VECTOR INDEX & CONTEXT ARTIFACTS SUCCESSFULLY BUILT!")
    print(f"💾 FAISS Index:    {out_idx} ({out_idx.stat().st_size / (1024*1024):.2f} MB)")
    print(f"📁 Metadata JSON:  {out_meta} ({out_meta.stat().st_size / 1024:.2f} KB)")
    print(f"📦 NPZ Index:      {npz_path} ({npz_path.stat().st_size / (1024*1024):.2f} MB)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    build_faiss_index()
