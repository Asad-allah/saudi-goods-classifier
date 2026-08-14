"""Dedicated Leaf-Level Ontology for all 90 terminal categories in the database."""

from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LeafSpec:
    leaf_id: int
    name_ar: str
    name_en: str
    parent_id: int | None
    parent_name_ar: str
    parent_name_en: str
    core_nouns_ar: tuple[str, ...]
    core_nouns_en: tuple[str, ...]
    brands_ar: tuple[str, ...]
    brands_en: tuple[str, ...]
    specs_ar: tuple[str, ...]
    specs_en: tuple[str, ...]
    packaging_ar: tuple[str, ...]
    packaging_en: tuple[str, ...]


def load_leaf_ontology() -> dict[int, LeafSpec]:
    """Builds and returns exhaustive specs for all 90 terminal leaf categories."""
    json_path = Path("scratch/leaf_metadata.json")
    if not json_path.exists():
        raise FileNotFoundError("scratch/leaf_metadata.json not found")

    with open(json_path, "r", encoding="utf-8") as f:
        leaf_list = json.load(f)

    ontology: dict[int, LeafSpec] = {}
    for item in leaf_list:
        lid = item["id"]
        nar = item["name_ar"]
        nen = item["name_en"]
        pid = item["parent_id"]
        par = item["parent_name_ar"]
        pen = item["parent_name_en"]
        cnames = item.get("common_names", [])

        # Build Arabic nouns
        nouns_ar = list(cnames)
        if nar not in nouns_ar:
            nouns_ar.insert(0, nar)
        # Enrich with descriptive variants
        nouns_ar.extend([
            f"{nar} فاخر", f"{nar} مستورد", f"{nar} وطني", f"{nar} درجة أولى",
            f"{nar} أصلي", f"{nar} تجاري", f"{nar} للمشاريع", f"{nar} جملة",
            f"شحنة {nar}", f"طلبية {nar}", f"بضاعة {nar}"
        ])

        # Build English nouns
        nouns_en = [
            nen, f"premium {nen}", f"imported {nen}", f"commercial {nen}",
            f"grade A {nen}", f"industrial {nen}", f"genuine {nen}", f"wholesale {nen}",
            f"certified {nen}", f"standard {nen}", f"heavy duty {nen}"
        ]

        brands_ar = (par, f"شركة {par}", f"مصنع {nar}", f"مؤسسة {nar}")
        brands_en = (pen, f"{pen} Co", f"{nen} Factory", f"National {nen}")
        specs_ar = ("مقاسات متنوعة", "نخب أول", "مواصفات قياسية", "درجة ممتازة", "سعودي بلدي", "جاهز للتحميل")
        specs_en = ("standard specs", "grade 1", "export quality", "heavy duty", "SASO certified", "ready for shipment")
        pack_ar = ("كراتين", "طبالي", "شوالات", "براميل", "صناديق", "لفات", "حمولة دينا", "حمولة تريلا", "شدات")
        pack_en = ("cartons", "pallets", "sacks", "drums", "boxes", "rolls", "truckload", "bundles", "packages")

        ontology[lid] = LeafSpec(
            leaf_id=lid,
            name_ar=nar,
            name_en=nen,
            parent_id=pid,
            parent_name_ar=par,
            parent_name_en=pen,
            core_nouns_ar=tuple(nouns_ar),
            core_nouns_en=tuple(nouns_en),
            brands_ar=brands_ar,
            brands_en=brands_en,
            specs_ar=specs_ar,
            specs_en=specs_en,
            packaging_ar=pack_ar,
            packaging_en=pack_en,
        )

    return ontology


LEAF_ONTOLOGY: dict[int, LeafSpec] = load_leaf_ontology()
