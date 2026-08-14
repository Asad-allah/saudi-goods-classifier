#!/usr/bin/env python3
"""Offline Vector Index Builder for Semantic Goods Search.
Encodes rich category documents from saudi_market_category_contexts.json and catalog.json into
a fast, portable vector index artifact.
"""

from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from typing import Any
import numpy as np
from sentence_transformers import SentenceTransformer

from app.catalog.importer import load_catalog_artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Build external vector index artifact.")
    parser.add_argument(
        "--catalog-path",
        type=str,
        default="storage/catalog/catalog.json",
        help="Path to catalog.json artifact",
    )
    parser.add_argument(
        "--contexts-path",
        type=str,
        default="storage/catalog/saudi_market_category_contexts.json",
        help="Path to saudi_market_category_contexts.json artifact",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="storage/models/intfloat-multilingual-e5-small",
        help="Path to local SentenceTransformer model",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="storage/semantic/catalog_vector_index.npz",
        help="Output path for compiled vector index",
    )
    args = parser.parse_args()

    print("=" * 75)
    print("🚀 BUILDING EXTERNAL VECTOR INDEX ARTIFACT (OPTION 2)")
    print("=" * 75)
    print(f"📖 Catalog:     {args.catalog_path}")
    print(f"🌍 Contexts:    {args.contexts_path}")
    print(f"🧠 Model:       {args.model_path}")
    print(f"💾 Output:      {args.output_path}")
    print("=" * 75 + "\n")

    catalog = load_catalog_artifact(args.catalog_path)
    print(f"✅ Loaded catalog: {len(catalog.good_types)} good types, {len(catalog.selectable_terms)} terms")

    contexts_file = Path(args.contexts_path)
    contexts_data: dict[str, dict] = {}
    if contexts_file.exists():
        with open(contexts_file, "r", encoding="utf-8") as f:
            contexts_data = json.load(f)
        print(f"✅ Loaded {len(contexts_data)} enriched Saudi market domain contexts.")

    model = SentenceTransformer(args.model_path)
    is_e5 = "e5" in str(args.model_path).lower()

    # Construct comprehensive semantic passages
    passages: list[str] = []
    metadata: list[dict[str, Any]] = []

    # 1. Base catalog terms
    for term in catalog.selectable_terms:
        root = catalog.root(term.root_good_type_id)
        good_type = catalog.good_type(term.source_good_type_id)
        text = f"passage: {term.raw_term}. نوع البضاعة: {good_type.name_ar} ({good_type.name_en}). المجموعة الرئيسية: {root.name_ar} ({root.name_en})."
        passages.append(text if is_e5 else text.replace("passage: ", ""))
        metadata.append({
            "root_good_type_id": term.root_good_type_id,
            "source_good_type_id": term.source_good_type_id,
            "source_type": term.source_type,
            "matched_term": term.raw_term,
            "is_cross_root_ambiguous": term.is_cross_root_ambiguous,
            "is_cross_good_type_ambiguous": term.is_cross_good_type_ambiguous,
            "text": text,
        })

    # 2. Rich Category Contexts and Trade Terms from saudi_market_category_contexts.json
    for key, cdata in contexts_data.items():
        leaf_id = int(cdata["good_type_id"])
        root_id = int(cdata["root_id"])
        name_ar = cdata["name_ar"]
        name_en = cdata["name_en"]
        root_name_ar = cdata["root_name_ar"]
        root_name_en = cdata["root_name_en"]
        market_ctx_ar = cdata["market_context_ar"]
        market_ctx_en = cdata["market_context_en"]
        trade_terms_ar = cdata.get("trade_terms_ar", [])
        trade_terms_en = cdata.get("trade_terms_en", [])
        key_brands = cdata.get("key_brands", [])

        # Build full domain context narrative passage
        full_ctx_text = (
            f"passage: {name_ar} ({name_en}). "
            f"المجموعة الرئيسية: {root_name_ar} ({root_name_en}). "
            f"{market_ctx_ar} {market_ctx_en}"
        )
        passages.append(full_ctx_text if is_e5 else full_ctx_text.replace("passage: ", ""))
        metadata.append({
            "root_good_type_id": root_id,
            "source_good_type_id": leaf_id,
            "source_type": "SAUDI_MARKET_DOMAIN_CONTEXT",
            "matched_term": name_ar,
            "is_cross_root_ambiguous": False,
            "is_cross_good_type_ambiguous": False,
            "text": full_ctx_text,
        })

        # Add individual trade terms & slang as focused passages
        for term in trade_terms_ar:
            term_text = f"passage: {term}. تصنيف: {name_ar} - {root_name_ar}."
            passages.append(term_text if is_e5 else term_text.replace("passage: ", ""))
            metadata.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "MARKET_TRADE_TERM_AR",
                "matched_term": term,
                "is_cross_root_ambiguous": False,
                "is_cross_good_type_ambiguous": False,
                "text": term_text,
            })

        for term in trade_terms_en:
            term_text = f"passage: {term}. Category: {name_en} ({root_name_en})."
            passages.append(term_text if is_e5 else term_text.replace("passage: ", ""))
            metadata.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "MARKET_TRADE_TERM_EN",
                "matched_term": term,
                "is_cross_root_ambiguous": False,
                "is_cross_good_type_ambiguous": False,
                "text": term_text,
            })

        for brand in key_brands:
            brand_text = f"passage: {brand}. ماركة تجارية لتصنيف: {name_ar} ({root_name_ar})."
            passages.append(brand_text if is_e5 else brand_text.replace("passage: ", ""))
            metadata.append({
                "root_good_type_id": root_id,
                "source_good_type_id": leaf_id,
                "source_type": "MARKET_BRAND",
                "matched_term": brand,
                "is_cross_root_ambiguous": False,
                "is_cross_good_type_ambiguous": False,
                "text": brand_text,
            })

    print(f"📊 Encoding {len(passages):,} rich semantic passages across all 90 leaves...")
    start_time = time.perf_counter()
    raw_embeddings = model.encode(passages, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
    
    # Normalize vectors for cosine similarity
    norms = np.linalg.norm(raw_embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized_embeddings = (raw_embeddings / norms).astype(np.float32)

    elapsed = time.perf_counter() - start_time
    print(f"⏱️ Encoding finished in {elapsed:.2f}s (Shape: {normalized_embeddings.shape})")

    # Export index artifact
    out_file = Path(args.output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    metadata_json_str = json.dumps(metadata, ensure_ascii=False)
    np.savez_compressed(
        out_file,
        embeddings=normalized_embeddings,
        metadata=np.array([metadata_json_str]),
    )
    
    file_size_mb = out_file.stat().st_size / (1024 * 1024)
    print("\n" + "=" * 75)
    print("🎉 UPDATED VECTOR INDEX ARTIFACT SUCCESSFULLY COMPILED!")
    print("=" * 75)
    print(f"📁 File:      {out_file}")
    print(f"📦 Size:      {file_size_mb:.2f} MB")
    print(f"🔢 Vectors:   {len(normalized_embeddings):,} vectors (Dimension: {normalized_embeddings.shape[1]})")
    print("=" * 75 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
