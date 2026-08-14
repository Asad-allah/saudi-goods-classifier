"""High-Performance Multi-Strategy Bilingual (Arabic/English) Dataset Generator."""

from __future__ import annotations
import random
from app.data_engine.ontology import ROOT_ONTOLOGY, CategorySpec
from app.data_engine.vocabularies import (
    PACKAGING_CONTAINERS_AR,
    PACKAGING_CONTAINERS_EN,
    QUANTITY_PREFIXES_AR,
    QUANTITY_PREFIXES_EN,
    PREFIXES_AR,
    PREFIXES_EN,
    MODIFIERS_AR,
    MODIFIERS_EN,
    apply_realistic_noise,
)
from app.data_engine.disambiguator import DisambiguationEngine


class LogisticsDatasetGenerator:
    """Generates massive, diverse, zero-conflict bilingual logistics examples for all 37 roots."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)
        self.disambiguator = DisambiguationEngine()

    def generate_category_samples(
        self,
        root_id: int,
        target_count: int = 27030,
    ) -> list[str]:
        """Generates target_count unique, validated, and disambiguated examples for root_id."""
        spec = ROOT_ONTOLOGY.get(root_id)
        if not spec:
            raise ValueError(f"Unknown root_id: {root_id}")

        results: set[str] = set()
        attempts = 0
        max_attempts = target_count * 25

        while len(results) < target_count and attempts < max_attempts:
            attempts += 1
            sample = self._generate_archetype_sample(spec)
            
            # Disambiguate and check boundaries
            is_valid, anchored_sample = self.disambiguator.validate_and_anchor(sample, root_id)
            if not is_valid or len(anchored_sample.strip()) < 4:
                continue

            # Apply realistic noise to a subset of Arabic text
            final_text = apply_realistic_noise(anchored_sample, noise_probability=0.18)
            results.add(final_text.strip())

        return sorted(results)[:target_count]

    def _generate_archetype_sample(self, spec: CategorySpec) -> str:
        """Picks a language mode and generation archetype based on distribution weights."""
        lang_mode = self.rng.choices(["ar", "en", "mixed"], weights=[60, 25, 15], k=1)[0]
        
        archetype = self.rng.choices(
            [
                "logistics_packaging",
                "brand_focused",
                "dialect_driver",
                "spec_model",
                "cohesive_compound",
                "bare_with_modifier",
            ],
            weights=[30, 22, 20, 13, 8, 7],
            k=1,
        )[0]

        if lang_mode == "ar":
            noun = self.rng.choice(spec.core_nouns)
            brand = self.rng.choice(spec.brands) if spec.brands else ""
            packaging = self.rng.choice(spec.packaging_types) if spec.packaging_types else self.rng.choice(PACKAGING_CONTAINERS_AR)
            spec_model = self.rng.choice(spec.specs_and_models) if spec.specs_and_models else ""
            quantity = self.rng.choice(QUANTITY_PREFIXES_AR)
            prefix = self.rng.choice(PREFIXES_AR)
            modifier = self.rng.choice(MODIFIERS_AR)

            if archetype == "logistics_packaging":
                parts = [quantity, packaging, noun]
                if brand and self.rng.random() > 0.4:
                    parts.append(brand)
                return " ".join(p for p in parts if p)

            elif archetype == "brand_focused":
                parts = [noun, brand]
                if spec_model and self.rng.random() > 0.3:
                    parts.append(spec_model)
                if self.rng.random() > 0.5:
                    parts.append(modifier)
                return " ".join(p for p in parts if p)

            elif archetype == "dialect_driver":
                parts = [prefix, noun]
                if brand and self.rng.random() > 0.5:
                    parts.append(brand)
                if self.rng.random() > 0.4:
                    parts.append(modifier)
                return " ".join(p for p in parts if p)

            elif archetype == "spec_model":
                parts = [noun, spec_model]
                if brand and self.rng.random() > 0.4:
                    parts.append(brand)
                return " ".join(p for p in parts if p)

            elif archetype == "cohesive_compound":
                noun2 = self.rng.choice(spec.core_nouns)
                while noun2 == noun and len(spec.core_nouns) > 1:
                    noun2 = self.rng.choice(spec.core_nouns)
                parts = [quantity, noun, "و", noun2]
                if self.rng.random() > 0.5:
                    parts.append(packaging)
                return " ".join(p for p in parts if p)

            else:
                parts = [noun, modifier]
                return " ".join(p for p in parts if p)

        elif lang_mode == "en":
            noun_en = self.rng.choice(spec.core_nouns_en) if spec.core_nouns_en else spec.name_en
            brand_en = self.rng.choice(spec.brands_en) if spec.brands_en else ""
            packaging_en = self.rng.choice(spec.packaging_types_en) if spec.packaging_types_en else self.rng.choice(PACKAGING_CONTAINERS_EN)
            spec_model_en = self.rng.choice(spec.specs_and_models_en) if spec.specs_and_models_en else ""
            quantity_en = self.rng.choice(QUANTITY_PREFIXES_EN)
            prefix_en = self.rng.choice(PREFIXES_EN)
            modifier_en = self.rng.choice(MODIFIERS_EN)

            if archetype == "logistics_packaging":
                parts = [quantity_en, packaging_en, "of", noun_en]
                if brand_en and self.rng.random() > 0.4:
                    parts.append(f"({brand_en})")
                return " ".join(p for p in parts if p)

            elif archetype == "brand_focused":
                parts = [brand_en, noun_en]
                if spec_model_en and self.rng.random() > 0.3:
                    parts.append(spec_model_en)
                if self.rng.random() > 0.5:
                    parts.append(modifier_en)
                return " ".join(p for p in parts if p)

            elif archetype == "dialect_driver":
                parts = [prefix_en, noun_en]
                if brand_en and self.rng.random() > 0.5:
                    parts.append(brand_en)
                if self.rng.random() > 0.4:
                    parts.append(modifier_en)
                return " ".join(p for p in parts if p)

            elif archetype == "spec_model":
                parts = [noun_en, spec_model_en]
                if brand_en and self.rng.random() > 0.4:
                    parts.append(brand_en)
                return " ".join(p for p in parts if p)

            elif archetype == "cohesive_compound":
                noun_en2 = self.rng.choice(spec.core_nouns_en) if spec.core_nouns_en else spec.name_en
                while noun_en2 == noun_en and len(spec.core_nouns_en) > 1:
                    noun_en2 = self.rng.choice(spec.core_nouns_en)
                parts = [quantity_en, noun_en, "and", noun_en2]
                if self.rng.random() > 0.5:
                    parts.append(f"({packaging_en})")
                return " ".join(p for p in parts if p)

            else:
                parts = [noun_en, modifier_en]
                return " ".join(p for p in parts if p)

        else: # Mixed Mode (e.g. "شحنة 10 كراتين iPhone 15 Pro Max", "طبلية زيت Castrol 5W-30")
            noun_ar = self.rng.choice(spec.core_nouns)
            brand_en = self.rng.choice(spec.brands_en) if spec.brands_en else ""
            spec_model_en = self.rng.choice(spec.specs_and_models_en) if spec.specs_and_models_en else ""
            packaging_ar = self.rng.choice(spec.packaging_types) if spec.packaging_types else self.rng.choice(PACKAGING_CONTAINERS_AR)
            quantity_ar = self.rng.choice(QUANTITY_PREFIXES_AR)
            prefix_ar = self.rng.choice(PREFIXES_AR)

            parts = [prefix_ar, quantity_ar, packaging_ar, noun_ar]
            if brand_en:
                parts.append(brand_en)
            if spec_model_en and self.rng.random() > 0.4:
                parts.append(spec_model_en)
            return " ".join(p for p in parts if p)
