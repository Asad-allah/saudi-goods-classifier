# `good_types` Data Quality Audit — 2026-08-14

## Scope

Source: `sub_db.sql`, table `good_types` only.

- 103 rows
- 37 roots
- 66 direct children
- maximum hierarchy depth: one edge

This audit separates confirmed translation defects from taxonomy decisions that require the catalog owner's approval. The classifier must preserve source values for traceability but must not use unreviewed English text as retrieval or embedding evidence.

## Confirmed English-label mismatches

| ID | Arabic source label | Current `en_name` | Safe English meaning |
|---:|---|---|---|
| 131 | الإلكترونيات | Reinforcing | Electronics |
| 167 | حاويات | Medical Waste | Containers |
| 168 | نفايات طبية | sponges | Medical Waste |
| 169 | الأسفنج | gypsum | Sponge / Foam |
| 170 | جبس | Vegetables and fruits | Gypsum |
| 171 | الخضروات والفواكه | Electrical Appliances | Vegetables and Fruits |
| 175 | منظفات | Refrigerators | Detergents / Cleaning Products |
| 179 | وحدات تبريد | Stoves | Refrigeration Units |
| 184 | صابون | Ovens | Soap |
| 185 | مناديل ورقية | Other unclassified | Paper Tissues |
| 186 | مناديل | containers | Tissues |
| 188 | مكائن صناعية | washing machines | Industrial Machinery |
| 190 | نقل رافعة | Industrial machines | Crane / Lifting Transport |
| 192 | عطور | Air conditioners | Perfumes |

The sequence from IDs 167–192 strongly suggests shifted or copied translations, not isolated model errors.

## Incorrect, corrupted, or incomplete English wording

| ID | Current value | Problem |
|---:|---|---|
| 6 | Mining or Fossilization Materials | `التحجير` means quarrying, not fossilization. |
| 14 | Dry Fast-Moving Consum | Truncated label. |
| 15 | Cold Fast-Moving Consum | Truncated label. |
| 50 | Equipment and tools include saws, hammers, fisher | `fisher` does not translate the Arabic equipment list. |
| 53 | Book and asphalt materials | `Book` is an incorrect translation of backfill materials. |
| 54 | Woods include carpentry wood, doors and succession | `succession` is an incorrect translation of `وخلافه`. |
| 60 | ...air dictations | `dictations` is an incorrect translation of air ducts. |
| 114 | Iron ore - Fe<40? | Contains a corrupted/uncertain symbol. |
| 124 | Cattles | Grammatically incorrect plural; meaning is still recognizable. |
| 165 | New spare | Incomplete; should refer to new spare parts. |

## Search-data conflicts

- There are 61 normalized terms shared by more than one direct `good_types` row. They must be preserved as ambiguous evidence, not deduplicated by root.
- IDs 163 (`مواد تنظيف`) and 175 (`منظفات`) substantially duplicate each other and require a catalog-owner decision: merge, alias, or keep distinct with written definitions.
- IDs 135 (`المواد البلاستيكية`) and 152 (`المطاط واللدائن`) overlap and need boundary definitions.
- IDs 138 and 139 both use Arabic `الزيوت`, under food and petroleum contexts respectively. Context is mandatory; the raw word alone is ambiguous.
- Alias `أجهزة كهربائية` appears in broad electrical/electronic areas and cannot safely distinguish wiring materials, electronics, lamps, or generators by itself.
- ID 159 (`مولدات الكهرباء`) includes solar panels and batteries in `common_names`, making it broader than its Arabic title.
- ID 164 (`المواد الحديدية`) contains `فواكه قشطه`, which is a clearly contaminated food alias and should be quarantined.
- ID 158 (`المواد الزراعية والأسمدة`) contains food/feed-like aliases such as `قمح دقيق` and `نخالة علف`; ownership needs review.
- ID 171 (`الخضروات والفواكه`) contains `تمر`, which also occurs under ID 14. Direct-category ownership is ambiguous without a catalog rule.

## Taxonomy decisions, not automatic corrections

The following may be intentional business choices and must not be silently changed by the classifier:

- `مياه معبأة` (166) is a root instead of a child of food.
- `مولدات الكهرباء` (159) is a root instead of a child of construction/electrical materials.
- `صهاريج الماء` (126), `مواد كيميائية` (136), and `بيوت جاهزة` (140) are roots.
- `كياس زبالة`, `لمبة كهربائية`, `شحاطة بلاستيك`, and `باب خشب` do not yet have an unambiguous approved direct-category rule in the current catalog.

Until the catalog owner approves these boundaries, the correct system behavior is ranked alternatives plus `requiresReview=true`, never a high-confidence guess.

## Requirement conflict found in `Goods Types Flow v2.docx`

The document correctly states that a row with children cannot be returned and that one of its children must be selected. It then instructs the system to use ID 31 (`النقل الخاص لقطاع الاعمال`) whenever classification fails, but immediately gives food examples mapped to 31 and says that result is wrong. These statements contradict each other.

The approved classifier rule is therefore:

- no fallback ID 31;
- no default category;
- unresolved input returns no accepted category and requires review;
- reviewed selection becomes verified feedback for the correct leaf type.
