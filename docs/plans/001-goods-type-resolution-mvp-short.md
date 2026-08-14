# خطة MVP المختصرة: مطابقة أنواع البضائع

> النسخة التفصيلية: [خطة التنفيذ التفصيلية](001-goods-type-resolution-mvp-detailed.md)

## الهدف

تحويل اسم البضاعة الذي يكتبه السائق إلى `good_types.id` موجود ومن فئة نهائية `leaf`، أو طلب تأكيد/مراجعة عند عدم وضوح النتيجة.

القرار المعماري الكامل موثق في [ADR-001](../decisions/ADR-001-hybrid-goods-type-resolution.md).

## الحل المختار

```text
اختيار من القائمة
    -> التحقق من ID وleaf
    -> MATCHED

إدخال حر
    -> تطابق حرفي
    -> بحث إملائي + Semantic Embedding
    -> دمج النتائج
    -> عرض أفضل 3
    -> تأكيد السائق أو مراجعة الإدارة
```

مكونات الـMVP:

- Arabic normalization محافظ.
- Exact matching مع الأسماء والـaliases المعتمدة.
- Character/Fuzzy search للأخطاء الإملائية.
- `multilingual-e5-small` كـembedding baseline قابل للاستبدال.
- Cosine similarity داخل الذاكرة.
- Reciprocal Rank Fusion لدمج البحث الإملائي والدلالي.
- Top-3 confirmation.
- Admin review وإضافة aliases معتمدة.

لا نحتاج في الـMVP إلى Agent أو LangGraph أو Generative LLM أو الإنترنت أو Vector Database أو reranker.

## حالات النتيجة

| الحالة | الاستخدام |
|---|---|
| `MATCHED` | تطابق حتمي أو اختيار مؤكد، ويحتوي ID نهائياً |
| `NEEDS_CONFIRMATION` | عرض أفضل 3 للسائق |
| `PENDING_REVIEW` | لا يوجد مرشح مناسب |
| `MULTI_ITEM` | النص يحتوي أكثر من منتج ويجب فصله |

## خطوات التنفيذ

### 1. تثبيت القواعد

- تحديد سياسة المنتجات المتعددة.
- التأكد إن كان لدى الجهة الرسمية Unknown ID.
- منع استخدام ID 31 كـfallback.
- منع إرسال parent category.

**القبول:** لا يمكن إرسال ID غير موجود أو غير `leaf`.

### 2. تحديث قاعدة البيانات

إنشاء:

- `good_type_aliases` للأسماء البديلة المعتمدة.
- `good_type_resolution_events` لتسجيل كل محاولة ونتيجتها.
- `good_type_resolution_candidates` لحفظ أفضل المرشحين.

إضافة إلى `new_good_types`:

- `normalized_name`
- `resolved_good_type_id`
- `status`
- `occurrence_count`
- بيانات المراجع والتاريخ

**القبول:** تكرار المصطلح يحدث review item موجوداً ولا ينشئ نسخاً متكررة.

### 3. بناء المسار الحتمي

1. حفظ النص الأصلي.
2. تطبيع نسخة مخصصة للبحث.
3. البحث الحرفي في الاسم العربي والإنجليزي والـaliases.
4. إعادة ID فقط عند تطابق وحيد مع `leaf`.

**القبول:** الاسم الملتبس لا يطابق تلقائياً.

### 4. بناء البحث الذكي

1. استرجاع أفضل 20 نتيجة بالبحث الإملائي.
2. حساب embedding واحد لنص السائق.
3. مقارنة الـvector مع category وalias vectors المحسوبة مسبقاً.
4. استرجاع أفضل 20 نتيجة دلالية.
5. دمج القائمتين بـRRF وتجميعهما حسب `good_type_id`.
6. حذف جميع parent categories.
7. إعادة أفضل 3 للسائق.

عند استخدام E5:

```text
query: {driver text}
passage: {category or alias text}
```

النص من كلمة إلى ثلاث كلمات صالح للـembedding، لكنه يستخدم لاسترجاع المرشحين وليس لاتخاذ قرار تلقائي منفرد.

**القبول:** تعطل embedding يعيد lexical candidates أو `PENDING_REVIEW`، ولا يعيد fallback ID.

### 5. بناء API

```text
POST /api/v1/good-type-resolutions
POST /api/v1/good-type-resolutions/{id}/confirmation
POST /api/v1/good-type-resolutions/{id}/rejection
```

مثال النتيجة:

```json
{
  "status": "NEEDS_CONFIRMATION",
  "resolutionId": "uuid",
  "candidates": [
    { "goodTypeId": 122, "arName": "...", "enName": "..." }
  ]
}
```

**القبول:** الخادم يتحقق أن ID المؤكد موجود ضمن المرشحين وما زال `leaf`.

### 6. واجهة السائق والإدارة

السائق:

- يرى أفضل 3 نتائج.
- يختار نتيجة أو "لا شيء مناسب".
- يفصل الإدخال إذا كان يحتوي عدة منتجات.

الإدارة:

- تراجع `PENDING_REVIEW`.
- تربط المصطلح بـleaf موجود.
- تضيفه كـalias معتمد.
- تحدث فهرس البحث.

**القبول:** alias المعتمد يصبح تطابقاً حرفياً في الطلب التالي.

### 7. الاختبار والقياس

الاختبارات المطلوبة:

- Unit: التطبيع، exact match، leaf guard، RRF.
- Integration: البحث الهجين، timeout، confirmation، review.
- E2E: إدخال السائق حتى إرسال ID.
- Security: الصلاحيات، validation، rate limit، وعدم تسريب البيانات.

المقاييس:

- `Top-3 Recall`
- `Precision`
- `Coverage`
- P50/P95 latency
- تكلفة كل 1000 طلب
- نسبة رفض السائق للمرشحين
- حجم وعمر قائمة المراجعة

**الأهداف الأولية:**

- `Top-3 Recall >= 95%` على بيانات مراجعة.
- exact/lexical `P95 <= 50 ms`.
- المسار الكامل `P95 <= 500 ms` عند استخدام API embedding.

لا يتم تفعيل semantic auto-match إلا بعد إثبات `Precision >= 95%` على test set حقيقية وغير متسربة.

### 8. الإطلاق

1. تشغيل exact matching فقط.
2. تشغيل semantic Top-3 بوضع تجريبي.
3. إطلاق محدود للسائقين.
4. مراقبة الجودة والسرعة والتكلفة.
5. التوسع التدريجي.

Feature flags:

- `lexicalEnabled`
- `semanticSuggestionsEnabled`
- `semanticAutoMatchEnabled=false`
- `embeddingProvider`

الرجوع الآمن: تعطيل semantic search والعودة إلى exact + lexical + admin review.

## المهام المختصرة

| # | المهمة | الاعتماد |
|---|---|---|
| 1 | اعتماد قواعد unknown وmulti-item وleaf | لا يوجد |
| 2 | Migrations وbackfill للـaliases | 1 |
| 3 | Normalizer وExact Matcher | 2 |
| 4 | Lexical Retriever | 3 |
| 5 | Embedding Provider وفهرس الذاكرة | 2 |
| 6 | Semantic Retriever وRRF | 4 و5 |
| 7 | Resolver API وحالات النتيجة | 3 و6 |
| 8 | Top-3 في تطبيق السائق | 7 |
| 9 | Review Queue وإضافة alias | 7 |
| 10 | تحديث الفهرس والتكامل الخارجي | 8 و9 |
| 11 | الاختبارات والمراقبة والإطلاق التدريجي | 10 |

تقدير أولي لفريق صغير: **3 إلى 4 أسابيع** بعد توفر مستودعات الـbackend والـmobile.

## Definition of Done

- [ ] لا يعاد إلا ID موجود و`leaf`.
- [ ] لا يستخدم ID 31 كـfallback.
- [ ] exact match يعمل من دون AI.
- [ ] البحث الهجين يعرض Top-3.
- [ ] السائق يستطيع التأكيد أو الرفض.
- [ ] الإدارة تستطيع اعتماد alias.
- [ ] تعطل provider لا ينتج ID خاطئاً.
- [ ] semantic auto-match معطل في الـMVP.
- [ ] الاختبارات والمقاييس وخطة الرجوع جاهزة.
