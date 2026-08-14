"""Deep AI-Grade Semantic Dataset Generator for all 90 Leaf Categories.
Generates genuine, coherent, grammatically sound commercial product descriptions,
shipping manifests, and logistics entries without naive character corruption.
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Generator
from app.data_engine.leaf_ontology import LEAF_ONTOLOGY, LeafSpec
from app.data_engine.massive_market_lexicon import LEAF_MARKET_ITEMS


# Real-world logistics prefixes & operational contexts
COMMERCIAL_CONTEXTS_AR: tuple[str, ...] = (
    "توريد مستودع", "طلبية جملة", "شحنة بضائع", "بضاعة مستوردة",
    "إرسالية تجارية", "دفعة جديدة من المصنع", "توصيل للمحلات", "شحنة دينا",
    "حمولة تريلا واصل الموقع", "طلبية مشاريع ومقاولات", "توزيع سوبرماركت وإعاشة",
    "تصفية مستودعات", "بضاعة جاهزة للتحميل", "شحنة سريعة", "طلبية كبرى"
)

COMMERCIAL_CONTEXTS_EN: tuple[str, ...] = (
    "Commercial supply of", "Wholesale consignment of", "Warehouse shipment of",
    "Import cargo containing", "Bulk order of", "Direct factory dispatch:",
    "Distribution delivery of", "Full truckload of", "Container shipment containing",
    "Project procurement of", "Retail inventory batch:", "Commercial freight:"
)

PACK_CONFIGS_AR: tuple[str, ...] = (
    "كرتون 24 حبة", "طبلية 50 كرتون", "طبلية خشبية 40 شد", "أكياس 50 كجم",
    "شوالات خيش 40 كيلو", "براميل 200 لتر", "جوالين سعة 5 لتر", "كرتون شد عائلي",
    "طرد مغلف محكم", "حمولة 5 طن", "حمولة تريلا كاملة", "صناديق خشبية مبطنة",
    "لفة 500 متر", "ربطات 12 حبة", "بوكسات تجارية مغلقة", "شحنة طبالي مشمعة"
)

PACK_CONFIGS_EN: tuple[str, ...] = (
    "carton of 24 units", "pallet of 50 cartons", "shrink-wrapped 40-box pallet",
    "50kg heavy duty bags", "40kg jute sacks", "200L industrial steel drums",
    "5L commercial gallons", "family value master carton", "reinforced shipping crate",
    "5-ton freight load", "full articulated truckload", "protective foam-lined boxes",
    "500m industrial roll", "12-pack master bundle", "sealed commercial boxes", "palletized batch"
)

QUALITY_GRADES_AR: tuple[str, ...] = (
    "نخب أول ممتاز", "مطابق للمواصفات والمقاييس السعودية SASO", "تاريخ جديد وإنتاج حديث",
    "درجة أولى فاخرة", "وكالة أصلي 100%", "جودة تصدير معتمدة", "صالح للاستخدام الفوري",
    "معتمد من هيئة الغذاء والدواء", "تحت الضمان الشامل", "خامات عالية الجودة"
)

QUALITY_GRADES_EN: tuple[str, ...] = (
    "Grade A premium quality", "fully SASO certified standard", "fresh stock new production",
    "first class export grade", "100% genuine OEM certified", "internationally compliant",
    "SFDA registered and approved", "under comprehensive warranty", "heavy duty industrial spec"
)


class AISemanticDatasetGenerator:
    """Generates natural, semantically rich, authentic commercial and logistics records."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)

    def generate_leaf_records(self, spec: LeafSpec, target_count: int) -> list[dict[str, Any]]:
        """Generates authentic semantic records for a leaf category."""
        market_data = LEAF_MARKET_ITEMS.get(spec.leaf_id)
        
        nouns_ar = market_data["nouns_ar"] if market_data else list(spec.core_nouns_ar)
        nouns_en = market_data["nouns_en"] if market_data else list(spec.core_nouns_en)
        brands_ar = market_data["brands_ar"] if market_data else list(spec.brands_ar)
        brands_en = market_data["brands_en"] if market_data else list(spec.brands_en)

        results: set[str] = set()
        records: list[dict[str, Any]] = []
        attempts = 0
        max_attempts = target_count * 35

        while len(results) < target_count and attempts < max_attempts:
            attempts += 1
            lang_mode = self.rng.choices(["ar", "en", "mixed"], weights=[60, 25, 15], k=1)[0]
            template_id = self.rng.randint(1, 6)

            if lang_mode == "ar":
                noun = self.rng.choice(nouns_ar)
                brand = self.rng.choice(brands_ar) if brands_ar else ""
                pack = self.rng.choice(PACK_CONFIGS_AR)
                ctx = self.rng.choice(COMMERCIAL_CONTEXTS_AR)
                grade = self.rng.choice(QUALITY_GRADES_AR)
                qty = self.rng.randint(2, 500)

                if template_id == 1:
                    # e.g. "توريد مستودع 50 كرتون 24 حبة أرز بسمتي هندي الشعلان نخب أول ممتاز"
                    text = f"{ctx} {qty} {pack} {noun} {grade}"
                elif template_id == 2:
                    # e.g. "حليب طازج المراعي كامل الدسم طبلية 50 كرتون معتمد من هيئة الغذاء والدواء"
                    text = f"{noun} {pack} ({grade})"
                elif template_id == 3:
                    # e.g. "طلبية جملة: كفرات هانكوك مقاس 17 للسيارات وكالة أصلي 100% - حمولة تريلا كاملة"
                    text = f"{ctx}: {noun} {grade} - {pack}"
                elif template_id == 4:
                    # e.g. "100 أكياس 50 كجم إسمنت بورتلاندي عادي اليمامة واصل الموقع"
                    text = f"{qty} {pack} من {noun} ({brand})" if brand else f"{qty} {pack} من {noun}"
                elif template_id == 5:
                    noun2 = self.rng.choice(nouns_ar)
                    text = f"{ctx} {noun} مع {noun2} ({pack})"
                else:
                    text = f"شحنة {noun} {brand} {pack} {grade}".strip()

                final_text = " ".join(text.split())

            elif lang_mode == "en":
                noun_en = self.rng.choice(nouns_en)
                brand_en = self.rng.choice(brands_en) if brands_en else ""
                pack_en = self.rng.choice(PACK_CONFIGS_EN)
                ctx_en = self.rng.choice(COMMERCIAL_CONTEXTS_EN)
                grade_en = self.rng.choice(QUALITY_GRADES_EN)
                qty = self.rng.randint(2, 500)

                if template_id == 1:
                    # e.g. "Commercial supply of 50 cartons of 24 units Shalan Indian Basmati Rice (Grade A premium quality)"
                    text = f"{ctx_en} {qty} {pack_en} of {noun_en} - {grade_en}"
                elif template_id == 2:
                    # e.g. "Samsung 65-inch 4K OLED Smart TV sealed commercial boxes [100% genuine OEM certified]"
                    text = f"{noun_en} {pack_en} [{grade_en}]"
                elif template_id == 3:
                    # e.g. "Bulk order of: Michelin Pilot Sport 18-inch High Performance Tires (palletized batch)"
                    text = f"{ctx_en}: {noun_en} ({pack_en})"
                elif template_id == 4:
                    text = f"Consignment of {qty} {pack_en} - {noun_en} ({brand_en})" if brand_en else f"Consignment of {qty} {pack_en} - {noun_en}"
                elif template_id == 5:
                    noun_en2 = self.rng.choice(nouns_en)
                    text = f"{ctx_en} {noun_en} and {noun_en2} ({pack_en})"
                else:
                    text = f"Commercial shipment: {noun_en} {brand_en} {pack_en} {grade_en}".strip()

                final_text = " ".join(text.split())

            else: # Mixed Mode (e.g. "شحنة 100 كرتون iPhone 15 Pro Max وكالة أصلي")
                noun_ar = self.rng.choice(nouns_ar)
                noun_en = self.rng.choice(nouns_en)
                pack_ar = self.rng.choice(PACK_CONFIGS_AR)
                ctx_ar = self.rng.choice(COMMERCIAL_CONTEXTS_AR)
                grade_ar = self.rng.choice(QUALITY_GRADES_AR)
                qty = self.rng.randint(5, 200)

                text = f"{ctx_ar} {qty} {pack_ar} {noun_ar} ({noun_en}) {grade_ar}"
                final_text = " ".join(text.split())

            if len(final_text) >= 10 and final_text not in results:
                results.add(final_text)
                records.append({
                    "text": final_text,
                    "good_type_id": spec.leaf_id,
                    "good_type_name_ar": spec.name_ar,
                    "good_type_name_en": spec.name_en,
                    "parent_root_id": spec.parent_id if spec.parent_id else spec.leaf_id,
                    "parent_root_name_ar": spec.parent_name_ar,
                    "parent_root_name_en": spec.parent_name_en,
                    "language": "AR" if lang_mode == "ar" else ("EN" if lang_mode == "en" else "MIXED"),
                    "source": "deep_semantic_commercial_generator",
                })

        return records[:target_count]
