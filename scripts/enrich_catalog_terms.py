import json
from pathlib import Path
from app.nlp.normalizer import normalize_text, compact_text

catalog_path = Path("storage/catalog/catalog.json")
contexts_path = Path("storage/catalog/saudi_market_category_contexts.json")

with open(catalog_path, "r", encoding="utf-8") as f:
    catalog_data = json.load(f)

with open(contexts_path, "r", encoding="utf-8") as f:
    contexts_data = json.load(f)

existing_terms = {(t["sourceGoodTypeId"], t["rawTerm"]) for t in catalog_data.get("terms", [])}
new_terms = list(catalog_data.get("terms", []))

for cat_id_str, ctx in contexts_data.items():
    cat_id = int(cat_id_str)
    root_id = ctx.get("root_id") or cat_id
    trade_terms = ctx.get("trade_terms_ar", []) + ctx.get("trade_terms_en", [])
    
    for term in trade_terms:
        if (cat_id, term) not in existing_terms:
            norm = normalize_text(term)
            compact = compact_text(norm)
            new_terms.append({
                "sourceGoodTypeId": cat_id,
                "rootGoodTypeId": root_id,
                "rawTerm": term,
                "normalizedTerm": norm,
                "compactTerm": compact,
                "sourceType": "COMMON_NAME",
                "languageHint": "AR" if any("\u0600" <= c <= "\u06ff" for c in term) else "EN",
                "isCrossRootAmbiguous": False,
                "isCrossGoodTypeAmbiguous": False,
            })
            existing_terms.add((cat_id, term))

catalog_data["terms"] = new_terms
with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(catalog_data, f, ensure_ascii=False, indent=2)

print(f"✅ Enriched catalog.json: Total search terms is now {len(new_terms)} across all 90 categories!")
