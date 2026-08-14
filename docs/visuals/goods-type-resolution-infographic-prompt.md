# برومبت إنفوغراف آلية مطابقة نوع البضاعة — منصة دندن

> الهدف: توليد إنفوغراف عربي واضح يشرح مسار الـMVP من إدخال السائق حتى إعادة `goodTypeId` موجود ونهائي، من دون اختراع تصنيف أو إخفاء حالات عدم اليقين.

## البرومبت الجاهز

```text
Use case: infographic-diagram
Asset type: 16:9 landscape technical product infographic for the Dandan shipping platform MVP

Primary request:
Create a precise Arabic right-to-left infographic titled exactly:
"آلية مطابقة وتصنيف نوع البضاعة — منصة دندن"

The infographic must explain the complete decision flow from the driver's input to a safe result. It is a restrained MVP workflow, not an AI marketing poster. Use only the facts and labels supplied below. Do not infer, invent, or add any step, ID, confidence percentage, product category, technology, or claim.

Audience:
Product, backend, mobile, data, and operations teams in Saudi Arabia.

Scene/backdrop:
Clean off-white background. Flat vector-like technical diagram. No photos, no decorative scenery, no 3D effects.

Composition/framing:
- Landscape 16:9.
- Arabic RTL reading direction, starting at the upper right and ending at the lower left.
- One main numbered flow containing six large stages.
- Use short straight arrows only; every arrow must have one unambiguous direction.
- No crossed arrows.
- Add one compact side panel for brand-name handling and one compact footer for safety rules.
- Keep generous whitespace and large readable text.

Visual hierarchy and palette:
- Main title: dark navy.
- Input and preprocessing: blue.
- Deterministic safe match: green.
- Smart candidate retrieval: purple.
- Driver confirmation: amber.
- Human review / abstention: muted red.
- Safety rules: dark gray with small shield icons.
- Use a modern Arabic sans-serif typeface similar to Noto Sans Arabic or IBM Plex Sans Arabic.
- Keep English technical tokens in a clean Latin sans-serif font.

MAIN FLOW — render the following Arabic copy verbatim and in this exact order:

Stage 1 — upper right
Heading: "١. إدخال السائق"
Body:
"اختيار من القائمة"
"أو كتابة اسم البضاعة"
Icon: driver holding a phone.

Stage 2
Heading: "٢. التحقق والتطبيع"
Body:
"حفظ النص الأصلي"
"تطبيع محافظ للمسافات والحروف"
"كشف وجود أكثر من منتج"
Small branch label:
"عدة منتجات ← MULTI_ITEM ← فصل المنتجات"
Icon: keyboard plus filter.

Stage 3
Heading: "٣. المطابقة الحتمية"
Body:
"الاسم الرسمي + الأسماء البديلة المعتمدة"
"تطابق وحيد + فئة نهائية leaf"
Green success output:
"MATCHED ← إرسال goodTypeId الموجود"
Small continuation label:
"لا يوجد تطابق حتمي ← تابع للبحث الذكي"
Icon: exact-match checkmark over a database.

Stage 4
Heading: "٤. البحث الذكي عن مرشحين"
Inside this stage show two parallel compact lanes that merge:
Lane A:
"بحث إملائي وحرفي"
"Character / Fuzzy — أفضل 20"
Lane B:
"بحث دلالي"
"Embedding — أفضل 20"
Merge box:
"RRF: دمج الرتب"
Then:
"تجميع حسب goodTypeId"
"حذف الفئات الأب والاحتفاظ بـ leaf فقط"
Important small note inside this stage:
"Embedding للاسترجاع فقط، وليس قراراً نهائياً"
Icons: magnifying glass for lane A, vector nodes for lane B, merge arrows for RRF.

Stage 5
Heading: "٥. عرض أفضل 3"
Body:
"يعرض التطبيق ثلاثة مرشحين فقط"
Two clear outcomes:
Green outcome:
"اختيار السائق ← MATCHED ← goodTypeId"
Red outcome:
"لا شيء مناسب ← PENDING_REVIEW"
Icon: phone with three radio-button choices.

Stage 6 — lower left
Heading: "٦. مراجعة الإدارة والتعلّم"
Body:
"ربط المصطلح بفئة leaf موجودة"
"اعتماد الاسم كـ alias"
"تحديث فهرس البحث"
"في الطلب التالي يصبح تطابقاً حتمياً"
Icon: administrator approving a tag and refreshing an index.

BRAND HANDLING SIDE PANEL — title and copy must be verbatim:
Title: "معالجة أسماء البراند"
Example line:
"KitKat = Kit Kat = كيتكات = كيت كات"
Rules:
"براند معروف: aliases + المسافات + التعريب + fuzzy"
"براند فقط وملتبس: اسأل «ما نوع المنتج؟»"
"براند غير معروف: لا تخمّن ← PENDING_REVIEW"
"براند + خط منتج: اربط التركيبة بالفئة المناسبة"
Add a small tag icon. Do not draw real product packaging or a trademark logo; use the example only as plain text.

SAFETY FOOTER — title and copy must be verbatim:
Title: "قواعد أمان لا تُتجاوز"
Rules:
"لا يوجد ID مخترع"
"لا تُرسل فئة أب؛ leaf فقط"
"ID 31 ليس Unknown ولا fallback"
"Cosine similarity ليست نسبة ثقة"
"لا Semantic Auto-Match في الـMVP"
"لا Agent ولا إنترنت في مسار السائق"

Final visual emphasis:
The only paths that produce a final `goodTypeId` are:
1) list selection after server validation,
2) a unique approved exact match that is a leaf,
3) explicit driver confirmation of one of the returned leaf candidates,
4) an approved administrative assignment.
All uncertain paths must visibly end in `NEEDS_CONFIRMATION`, `PENDING_REVIEW`, or `MULTI_ITEM`, never in a guessed ID.

Text fidelity constraints:
- Render every quoted string exactly once unless it is explicitly reused as a state label.
- Preserve Arabic spelling, punctuation, capitalization, Latin tokens, arrows, digits, and backticks conceptually; do not translate technical state names.
- Do not add filler copy or placeholder text.
- If the canvas cannot fit the text legibly, increase the canvas or shorten only visual spacing; never paraphrase, omit, or shrink the text to unreadable size.
- Verify every Arabic line character by character before finalizing.
```

## Negative Instructions

```text
Avoid all of the following:

CONTENT ERRORS
- Do not claim 100% prediction accuracy.
- Do not present cosine similarity, vector similarity, or an LLM self-score as confidence or probability.
- Do not auto-match from semantic similarity in the MVP.
- Do not invent a category, `goodTypeId`, Unknown ID, fallback ID, percentage, threshold, timing, benchmark, or government rule.
- Do not use ID 31 as Unknown or as a fallback.
- Do not return a parent category; only a verified `leaf` may become final.
- Do not imply that an embedding knows every brand or that a brand name always maps to one product type.
- Do not map an unknown brand directly to a product category.
- Do not make web search, an Agent, LangGraph, a generative LLM, or a vector database part of the driver's synchronous MVP path.
- Do not allow internet findings or model output to approve an alias without a human administrator.
- Do not omit the abstention outcomes: `NEEDS_CONFIRMATION`, `PENDING_REVIEW`, and `MULTI_ITEM`.
- Do not show a final `goodTypeId` before server validation and `leaf` validation.

TEXT ERRORS
- No misspelled Arabic, broken Arabic joining, reversed Arabic words, mirrored letters, garbled glyphs, duplicated headings, truncated lines, lorem ipsum, random English, or extra punctuation.
- Do not translate or alter these tokens: `MATCHED`, `NEEDS_CONFIRMATION`, `PENDING_REVIEW`, `MULTI_ITEM`, `RRF`, `Embedding`, `Fuzzy`, `leaf`, `goodTypeId`, `ID 31`, `MVP`.
- Do not replace `KitKat = Kit Kat = كيتكات = كيت كات` with a logo or package image.

LAYOUT ERRORS
- No crossed, looping, bidirectional, disconnected, or ambiguous arrows.
- No hidden stage, missing stage number, repeated stage number, or alternative flow not specified above.
- No dense wall of text, tiny labels, low contrast, excessive icons, decorative charts, fake metrics, dashboards, tables, maps, flags, ministry emblems, or unrelated UI screens.
- No photorealism, 3D, gradients that reduce readability, glassmorphism, neon colors, heavy shadows, crowded cards, comic style, mascots, watermark, signature, stock-photo look, or real trademarks.
- No dramatic AI brain, robot, magic sparkles, or visual claim that AI makes an infallible decision.
```

## فحص إلزامي بعد التوليد

لا يمكن لمولّد صور ضمان صحة النص العربي بنسبة 100%. تُعتمد الصورة فقط إذا نجحت في هذا الفحص:

- المراحل الست موجودة ومرتبة من اليمين إلى اليسار.
- مسار المطابقة الحتمية يسبق البحث الذكي.
- البحث الإملائي والـEmbedding مساران متوازيان يندمجان عبر `RRF`.
- `Embedding` يسترجع مرشحين ولا يتخذ القرار النهائي.
- لا يظهر `goodTypeId` نهائي إلا بعد تحقق حتمي أو تأكيد بشري.
- حالات `MULTI_ITEM` و`PENDING_REVIEW` ظاهرة ولا تنتهي بـID.
- مثال `KitKat` مكتوب بأشكاله الأربعة بلا أخطاء.
- جملة `ID 31 ليس Unknown ولا fallback` موجودة حرفياً.
- لا يوجد أي نص أو رقم أو سهم إضافي غير مذكور في البرومبت.
- كل سطر عربي مطابق حرفياً للنص المرجعي أعلاه.

إذا أخفق أي بند، صحّح البند وحده في جولة تحرير واحدة، مع تثبيت بقية التصميم بلا تغيير.

## امتداد مستقل للإنفوغراف: ما بعد الـMVP

لا تضع هذا الامتداد داخل المسار الأساسي إذا تسبب في ازدحام الصورة. الأفضل عرضه كشريط ثانٍ بعنوان **«التطوير بعد إثبات الـMVP»**:

```text
Add a separate lower roadmap strip titled exactly:
"التطوير بعد إثبات الـMVP"

Show this left-to-right technical sequence as a separate roadmap, not as part of the current MVP runtime:

"١. جمع القرارات المراجعة"
"قرارات الإدارة = بيانات ذهبية"
"اختيارات السائق = بيانات مساعدة"

→

"٢. بناء Gold Dataset"
"Train / Validation / Test بلا تسرب"
"قياس Top-3 Recall وPrecision وCoverage وP95"

→

"٣. تحسين فهم البراند والمنتج"
"Brand + Product Line + Aliases"
"استخراج البراند ونوع المنتج والحجم عند الحاجة"

→

"٤. إضافة Reranker"
"إعادة ترتيب أفضل 5–10 مرشحين"
"تدريبه على أمثلة دندن وHard Negatives"

→

"٥. معايرة pCorrect"
"ليست Cosine Similarity"
"تعتمد على اتفاق المحركات والفرق بين المرشحين ودرجة الـReranker"

→

"٦. Shadow Mode"
"قياس القرار الآلي دون تطبيقه على الشحنات"
"مراجعة الأخطاء حسب البراند واللهجة وطول النص"

→

"٧. Auto-Match تدريجي"
"يُفعّل فقط بعد إثبات Precision ≥ 95% على بيانات حقيقية"
"Feature Flag + إطلاق محدود + Rollback"

→

"٨. تحسين السرعة والكلفة"
"Cache + Embeddings محسوبة مسبقاً"
"اختيار Local أو API بالـBenchmark"
"Vector DB فقط إذا أثبت الحجم الحاجة"

Optional separate admin-only box:
"Agent إداري اختياري"
"يبحث عن البراندات غير المعروفة ويقترح فقط"
"لا يعتمد alias ولا يرسل goodTypeId دون موافقة بشرية"

Post-MVP runtime insertion:
Place `Reranker` after `RRF` and before the decision policy. Place the calibrated `pCorrect` decision after the reranker:
"pCorrect ≥ T_auto المعايرة ← MATCHED"
"أقل من العتبة ← عرض أفضل 3"
"لا دليل كافٍ ← PENDING_REVIEW"

Avoid:
- Do not enable automatic matching merely because cosine similarity is high.
- Do not train first on raw unreviewed driver choices as if they were ground truth.
- Do not add a generative LLM to every driver request.
- Do not add a Vector Database merely because embeddings exist.
- Do not make the Agent part of the driver hot path.
- Do not promise that Precision ≥ 95% will be reached; it must be measured and proven.
```
