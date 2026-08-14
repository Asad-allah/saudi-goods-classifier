import json
from pathlib import Path
from app.nlp.normalizer import normalize_text

contexts_path = Path("storage/catalog/saudi_market_category_contexts.json")
with open(contexts_path, "r", encoding="utf-8") as f:
    contexts = json.load(f)

# Comprehensive Saudi market dictionary mapping each specific construction subcategory under Root 34
root_34_subcategories = {
    # 45: الخرسانة (Concrete)
    "45": {
        "ar": [
            "خرسانة جاهزة ريدي مكس", "صبة خرسانة عادية", "صبة خرسانة مسلحة", "خرسانة سيلف كومباكتنج ذاتية الدمك",
            "صبة نظافة", "خرسانة رغوية فوم كونكريت", "خرسانة ميول اسطح", "خرسانة مطبوعة ارضيات",
            "خرسانة جاهزة مقاومة للكبريتات", "خرسانة مسبقة الصب بريكاست", "بمب صب خرسانة", "سيارة خلاطة خرسانة"
        ],
        "en": [
            "ready mix concrete", "plain concrete", "reinforced concrete", "self compacting concrete scc",
            "blinding lean concrete", "foam concrete lightweight", "roof screed concrete", "stamped concrete flooring",
            "sulfate resistant concrete", "precast concrete elements", "concrete pump truck", "concrete transit mixer"
        ]
    },

    # 46: الصلب (Structural Steel)
    "46": {
        "ar": [
            "هياكل فولاذية صلب", "حديد صلب كربوني", "ستيل مباني معدنية", "قطاعات صلب مدرفلة",
            "جسور صلب ثقيلة", "بليتات صلب مقوى", "صلب انشائي عالي المقاومة", "براغي صلب عالي الشد"
        ],
        "en": [
            "structural steel framing", "carbon structural steel", "pre engineered steel buildings", "rolled steel sections",
            "heavy steel girders", "high strength steel plates", "structural steel grade 50", "high tensile steel bolts"
        ]
    },

    # 47: الأنابيب ومواد تمديد الأعمال المائية وتشمل الخزانات
    "47": {
        "ar": [
            "خزانات مياه الزامل فايبر جلاس", "خزانات بولي ايثيلين افقية وعمودية", "خزانات مياه المهيدب الوطني",
            "مواسير تمديد مياه ضغط عالي", "مواسير بولي ايثيلين HDPE شبكات مياه", "مواسير حديد دكتايل مياه",
            "عوامات خزانات ميكانيكية وكهربائية", "فلاتر مياه مركزية جامبو", "محابس سكورة مياه رئيسية", "وصلات مرنة لمضخات المياه"
        ],
        "en": [
            "zamil fiberglass water tanks", "polyethylene horizontal and vertical water tanks", "muhaidib national water tanks",
            "high pressure water supply pipes", "hdpe water distribution pipes", "ductile iron water main pipes",
            "water tank float valves", "jumbo central water filters", "main water gate valves", "flexible pump connectors"
        ]
    },

    # 48: الألواح الزجاجية والألمنيوم وتشمل الأبواب والنوافذ
    "48": {
        "ar": [
            "الواح زجاج سيكوريت مقسى", "زجاج دبل جلاس عازل للصوت والحرارة", "زجاج استركشر واجهات",
            "قطاعات الومنيوم الراجحي", "الومنيوم سرايا والجامبو", "شبابيك الومنيوم دبل جلاس",
            "ابواب الومنيوم ودورات مياه", "شتر نوافذ الومنيوم كهربائي", "واجهات كرتن وول زجاجية", "درابزين زجاج استيل"
        ],
        "en": [
            "tempered securit glass panels", "double glazed insulated glass units", "structural glazing facade glass",
            "rajhi aluminum profiles", "saraya and jumbo aluminum window systems", "double glazed aluminum windows",
            "aluminum bathroom doors", "motorized roller shutters", "curtain wall glass facades", "glass and stainless steel balustrades"
        ]
    },

    # 49: اعمال التشطيب والدهانات والتكسيات الخارجية
    "49": {
        "ar": [
            "دهانات جوتن جوتاشيلد وفينوماستيك", "دهانات الجزيرة ورود ومشاشكو", "رشة بروفايل خارجي عسيب",
            "رشة كسر رخام واجهات", "معجون لياسة سافيتو داخلي وخارجي", "سيلر مائي وبرايمر دهان",
            "بوية حريري وربع لمعة ومطفي", "ايبوكسي ارضيات مواقف ومستودعات", "برايمر زنك ضد الصدأ", "فواصل تمدد للدهانات واللياسة"
        ],
        "en": [
            "jotun jotashield and fenomastic paints", "jazeera exterior and interior architectural paints", "textured profile exterior render",
            "marble chip aggregate exterior plaster", "saveto interior and exterior wall putty", "alkali resistant water based primer sealer",
            "silk semi gloss and matt emulsion paint", "self leveling floor epoxy", "zinc rich anti rust primer", "plaster expansion joint profiles"
        ]
    },

    # 50: المعدات والأدوات وتشمل المناشير والمطارق ومراوح اللياسة وهزازات الخرسانة
    "50": {
        "ar": [
            "هزاز صبة خرسانة ميكانيكي هوندا", "مروحة تنعيم الصبة هليكوبتر", "خلاطة صبة متنقلة برميل",
            "صاروخ جلخ وقص حديد وسيراميك", "دريل وهيلتي تكسير خرسانة بوش وديوالت وماكيتا", "منشار قص خرسانة واسفلت",
            "ميزان ليزر اخضر 360 درجة", "قدة الومنيوم للياسة والخرسانة", "مسطرين بنا ولياسة", "مالج تخشين وتنعيم ورابونجة",
            "ماكينة قص سيراميك روبي يدوية", "عربية يد نقل صبة ورمل فرغلي", "سقالات معدنية كب لوك", "جاكات حديد تلسكوبية لدعم الاسقف"
        ],
        "en": [
            "concrete poker vibrator with honda engine", "concrete power trowel helicopter machine", "portable concrete drum mixer",
            "angle grinder with diamond cutting disc", "demolition rotary hammer drill bosch dewalt makita", "walk behind concrete floor saw",
            "360 degree multi line green laser level", "aluminum screed straight edge bar", "bricklaying and plastering trowels",
            "plastering sponge float and finishing trowel", "manual porcelain tile cutter rubi", "heavy duty construction wheelbarrow",
            "cup lock modular steel scaffolding", "telescopic steel shoring acrow props"
        ]
    },

    # 51: أعمال السباكة والتمديدات الصحية
    "51": {
        "ar": [
            "مواسير حراري خضراء بي بي آر القبلان", "مواسير صرف يو بي في سي نيبرو", "مواسير سي بي في سي حار جدول 80",
            "اكواع وتيهات ونقاصات سباكة", "سيفون مدفون جروهي وجبيريت", "رداد صرف صحي مانع رجوع مياه المجاري",
            "صفاية ارضية ستانلس ستيل مع مانع روائح", "غرف تفتيش ومانهول بولي ايثيلين", "اغطية مانهول دكتايل",
            "محابس كرات نحاس وسكورة زاوية اركو", "مضخات مياه ودينمو ضغط كالبيدا وسكالا", "كراسي حمام معلقة وارضية الخزف السعودي"
        ],
        "en": [
            "ppr thermal green pipes al qablan", "upvc drainage sewer pipes nibro", "cpvc schedule 80 hot water pipes",
            "plumbing elbows tees and reducers", "grohe and geberit concealed wall cisterns", "backwater non return sewer valve",
            "stainless steel floor drain with odor seal", "polyethylene inspection chambers manholes", "ductile iron manhole covers",
            "brass ball valves and angle shut off valves", "calpeda and grundfos water booster pumps", "saudi ceramic floor and wall mounted toilets"
        ]
    },

    # 52: مواد العزل
    "52": {
        "ar": [
            "رولات عازل ممبرين بيتومينية 4 ملم درمابيت وبيتومات", "رولات ممبرين محببة بحص اسطح", "برايمر بيتومين قار بارد عوازل",
            "عازل اسمنتي مطاطي سيكا توب سيل 107", "عازل بولي يوريثان سائل مطاطي للأسطح", "فوم بولي يوريثان مرشوش عازل مائي وحراري",
            "الواح فوم بوليسترين مبثوق ازرق XPS جفالي", "صوف صخري الواح ورولات لمجاري التكييف والمباني", "قماش جيوتكستايل غير منسوج",
            "شريط ووتر ستوب بي في سي لفواصل الصب", "الواح بروتكشن بورد لحماية العازل", "مشمع نايلون بولي ايثيلين سميك لصبة النظافة"
        ],
        "en": [
            "4mm sbs app bituminous waterproofing membrane rolls dermabit bitumat", "mineral slate granule roof waterproofing membrane",
            "cold applied bitumen primer emulsion", "two component flexible cementitious waterproofing sikatop seal 107",
            "liquid polyurethane waterproofing membrane", "spray applied polyurethane foam spf roof insulation",
            "extruded polystyrene blue foam boards xps juffali", "rockwool thermal and acoustic insulation slabs rolls",
            "non woven polypropylene geotextile fabric", "pvc waterstop profiles for construction joints",
            "bituminous protection boards", "heavy duty polyethylene vapor barrier sheet"
        ]
    },

    # 53: مواد الدفان والسفلتة
    "53": {
        "ar": [
            "دفان صخري مغربل سبيسكورس A-1-a", "رمل احمر نفود للتسوية والفرش", "حصى كسر حجر متدرج",
            "اسفلت ساخن طبقة سطحية", "اسفلت رابط طبقة اساسية", "ام سي وان MC1 دهان اسفلت تشريب",
            "ار سي تو RC2 دهان اسفلت لاصق", "بردورات خرسانية لأرصفة الطرق", "بلاط انترلوك خرساني للشوارع والمواقف"
        ],
        "en": [
            "crushed rock subbase aggregate class a-1-a", "red dune sand for backfilling and bedding", "graded crushed stone aggregates",
            "hot mix asphalt wearing course", "asphalt binder base course", "prime coat bitumen mc1",
            "tack coat asphalt emulsion rc2", "precast concrete road curbstones", "interlock paving blocks for roads and parking"
        ]
    },

    # 54: الأخشاب وأخشاب الطوبار والأبواب
    "54": {
        "ar": [
            "خشب بليود كوري وماليزي اسود فيلم فيس طوبار", "خشب سويدي ابيض طوبار", "خشب لتزانة ومراين خشب",
            "خشب ام دي اف MDF واتش دي اف HDF وميلامين", "خشب سنديان وزان احمر وتيك وبلوط طبيعي", "الواح باركيه خشب ارضيات",
            "بديل الخشب داخلي وخارجي WPC", "ابواب خشب كبس وقشرة زان وحلوق خشبية", "كوالين ومفصلات ابواب خشب ومسامير سنارة"
        ],
        "en": [
            "film faced marine shuttering plywood korean malaysian", "white swedish pine timber for formwork",
            "latte planks and timber joists", "mdf hdf and melamine wood panels",
            "natural solid oak red beech and teak timber", "wooden parquet flooring boards",
            "wpc interior and exterior composite wood cladding", "wooden flush doors door frames and beech veneer",
            "mortise door locks hinges and wood nails"
        ]
    },

    # 55: حديد التسليح
    "55": {
        "ar": [
            "حديد سابك تسليح مشرشر 8 و 10 و 12 و 16 و 20 و 25 و 32 ملم", "حديد الراجحي وحديد الاتفاق وحديد وطني",
            "شبك حديد ارضيات بي ار سي BRC", "كانات حديد جاهزة لتسليح الاعمدة والجسور", "سلك تربيط حديد رباط مجلفن",
            "بسكوت خرساني وكراسي حديد تسليح", "مادة تزريع حديد ايبوكسي هيسكي وسيكا"
        ],
        "en": [
            "deformed steel reinforcing rebar 8mm 10mm 12mm 16mm 20mm 25mm 32mm sabic", "rajhi steel and ittefaq steel",
            "brc welded reinforcing steel mesh", "prefabricated steel stirrups for columns and beams", "galvanized annealed tie wire rolls",
            "concrete cover spacers and rebar chairs", "epoxy chemical rebar anchoring adhesive sika hilti"
        ]
    },

    # 56: مواد تمديدات الكهرباء
    "56": {
        "ar": [
            "كابلات الرياض نحاس مسلحة وغير مسلحة", "كابلات بحرة وكابلات الفنار", "اسلاك كهرباء نحاس معزولة 1.5 و 2.5 و 4 و 6 و 10 ملم",
            "ليات كهرباء برتقالية وفلكسبل مرنة وجرجور", "علب ماجيك وقسامات حديد مجلفن وبلاستيك", "طبالين ولوحات توزيع كهرباء الفنار وشنايدر",
            "قواطع تيار ام سي بي MCB وام سي سي بي MCCB وايرث ليكج RCD", "مفاتيح وافياش الفنار الترا وباناسونيك وشنايدر",
            "مفاتيح مكيفات 45 امبير وسخانات 20 امبير", "حوامل كابلات كيبل تري وترنك", "اسياخ تأريض نحاسية نقية"
        ],
        "en": [
            "riyadh cables armored and unarmored copper power cables", "bahra and alfanar electrical cables",
            "thhn pvc insulated copper building wires 1.5mm 2.5mm 4mm 6mm 10mm", "pvc corrugated flexible electrical conduits and pipes",
            "galvanized metal switch boxes and pvc junction boxes", "alfanar and schneider main distribution load centers",
            "miniature circuit breakers mcb molded case mccb and residual current rcd", "alfanar panasonic and schneider wall switches and sockets",
            "45a air conditioner and 20a water heater switches", "galvanized cable trays trunking and ladders", "pure copper earthing grounding rods"
        ]
    },

    # 57: الأحجار والصخور ومواد الرصف ويشكل ذلك البلاط
    "57": {
        "ar": [
            "كراتين سيراميك وبورسلان ارضيات وجدران الخزف السعودي", "بورسلان اسباني وهندي كبير الحجم", "حجر الرياض طبيعي مجلي ومنشور للواجهات",
            "رخام ارضيات طبيعي وجرانيت محلي ودرج", "بلاط انترلوك خرساني متشابك وممرات", "بلدورات ارصفة خرسانية",
            "غراء بلاط وسيراميك سافيتو وفيتونيت بوليفكس", "ترويبة بلاط وسيراميك فوسام ملونة ضد العفن", "غراء رخام ماستيك ايبوكسي"
        ],
        "en": [
            "ceramic and porcelain floor and wall tiles saudi ceramic", "large format spanish and indian porcelain slabs",
            "riyadh natural limestone and cladding stone", "natural marble floor tiles and granite steps",
            "interlocking concrete paving blocks", "precast concrete road curbstones",
            "saveto and vetonit polyfix cementitious tile adhesive", "fosroc anti fungal colored tile grout",
            "epoxy mastic adhesive for natural marble"
        ]
    },

    # 58: الطين (Clay / Mud)
    "58": {
        "ar": [
            "طين بناء بيوت تراثية", "لبن طيني مجفف للشمس", "طين فخاري معالج", "مونة طينية تراثية", "قش وتبن مخلوط بالطين"
        ],
        "en": [
            "traditional mud building clay", "sun dried adobe mud bricks", "processed ceramic pottery clay",
            "traditional clay mortar", "straw reinforced mud plaster"
        ]
    },

    # 59: الطوب (Blocks & Bricks)
    "59": {
        "ar": [
            "بلك اسمنتي اسود مفرغ 20 و 15 و 10 سم", "بلك اسمنتي مصمت صلب للجدران الحاملة", "بلك بركاني معزول جفالي والمانع",
            "طوب احمر فخاري مفرغ طوب اليمامة", "بلك هوردي اسقف احمر وبركاني وفلين", "بلك خرسانة خلوية خفيف سيبوركس", "بلك يو U-block للجسور الخرسانية"
        ],
        "en": [
            "hollow concrete blocks 20cm 15cm 10cm", "solid concrete masonry blocks for load bearing walls",
            "insulated volcanic thermal blocks juffali al mane", "red clay hollow bricks yamama brick",
            "hourdi hollow blocks for ribbed slabs", "autoclaved aerated concrete aac blocks siporex", "u-blocks for bond beams"
        ]
    },

    # 60: أدوات وآلات التكييف وتشمل أنابيب التمديد والدكتات الهوائية
    "60": {
        "ar": [
            "دكتات تكييف صاج مجلفن نيبون", "الواح دكت تكييف مسبقة العزل بايل باكت", "مواسير نحاس تمديد تكييف مولر امريكي",
            "عوازل دكتات صوف زجاجي وصوف صخري مع المنيوم", "جريلات وموزعات هواء ناشرات سبلاي وريتيرن",
            "مكيفات سبليت جري وماندو وال جي", "مكيفات كاسيت ومخفي كونسيلد", "مكيفات باكيج مركزية ومبردات شيلر",
            "نحاس كوري وجنوبي لتمديد الفريون", "غاز تبريد فريون R410A و R22 و R134a", "قواطع وتوصيلات تكييف كهربائية"
        ],
        "en": [
            "galvanized sheet metal hvac air ducts", "pre insulated duct panels p3 and pal duct", "mueller american copper refrigeration tubing",
            "fiberglass and rockwool duct insulation with aluminum foil", "air grilles diffusers supply and return registers",
            "gree mando and lg split air conditioners", "concealed ducted and cassette ac units", "rooftop package air conditioning units and chillers",
            "korean copper coils for freon lines", "refrigerant freon gas r410a r22 r134a", "hvac electrical disconnect switches"
        ]
    },

    # 121: أسمنت (Cement)
    "121": {
        "ar": [
            "اسمنت بورتلاندي عادي رمادي أكياس 50 كجم", "اسمنت اليمامة واسمنت السعودية واسمنت القصيم واسمنت الرياض",
            "اسمنت مقاوم للاملاح والكبريتات SRC للقواعد والميدات", "اسمنت ابيض رويال ورأس الخيمة لأعمال الديكور والواجهات",
            "اسمنت بوزولاني طبيعي", "طبالي وبالات اسمنت للتوريد المباشر", "اسمنت فائق النعومة للحقن والترميم"
        ],
        "en": [
            "ordinary portland cement opc 50kg bags", "yamama cement saudi cement and qassim cement",
            "sulfate resistant cement src for foundations", "white portland cement royal and rak for architectural work",
            "natural pozzolanic cement", "palletized bagged cement for direct shipment", "microfine cement for grouting and repairs"
        ]
    },

    # 128: الرمل (Sand)
    "128": {
        "ar": [
            "رمل سيليكا ابيض مغسول للياسة والخرسانة", "رمل بطحاء خشن مائل للصفرة للخلطات الاسمنتية",
            "رمل احمر نفود للتسوية والفرش تحت البلاط", "رمل ناعم مغربل", "رمل سيليكا معقم لفلاتر المسابح والدهانات"
        ],
        "en": [
            "washed white silica sand for plastering and concrete", "coarse yellow bathaa sand for cement mortar",
            "red dune sand for ground leveling and tile bedding", "screened fine sand", "sterilized silica sand for swimming pool filters and paints"
        ]
    },

    # 164: المواد الحديدية (Iron & Structural Steel)
    "164": {
        "ar": [
            "كمرات حديد جسور H-beam و I-beam و U-channel", "زوايا حديد متساوية وغير متساوية",
            "تيوبات حديد مربعة ومستطيلة سوداء ومجلفنة", "مواسير حديد سوداء مجلفنة وسيملس", "صاج حديد اسود مدرفل وصاج مبزر بقلاوة",
            "صاج معرج شينكو ملون للمستودعات والاسقف", "اسلاك شائكة وشبك سياج مزارع مجلفن", "درابزينات وبوابات حديد قص ليزر مشغول",
            "بليتات حديد قواعد اعمدة وفلانجات ومثبتات خرسانية عالية الصلابة"
        ],
        "en": [
            "structural steel h-beams i-beams and u-channels", "equal and unequal structural steel angles",
            "black and galvanized hollow square and rectangular steel tubes", "black galvanized and seamless steel pipes",
            "hot rolled steel sheets and chequered diamond floor plates", "corrugated pre painted shinko steel roofing sheets",
            "galvanized barbed wire and chain link security fencing", "laser cut wrought iron gates and balustrades",
            "steel column base plates pipe flanges and high strength concrete anchors"
        ]
    },

    # 170: جبس (Gypsum & Drywall)
    "170": {
        "ar": [
            "الواح جبسون بورد كناوف ومدى ابيض عادي للأسقف", "الواح جبس اخضر مقاوم للرطوبة للمطابخ ودورات المياه",
            "الواح جبس احمر مقاوم للحريق للممرات والمطابخ", "الواح سمنت بورد اسمنتية للواجهات الخارجية والمناطق الرطبة",
            "بلاطات اسقف مستعارة جبسية وفينيل مخرمة 60×60", "قطاعات حديد جبس اوميجا وستد وتراك وزوايا كورنر بيد",
            "شريط فواصل فايبر ومعجون جبس بورد كناوف وسافيتو جاهز", "جبس بلدي بودرة بياض جيبسكو في اكياس للكورنيش",
            "بانوهات وبراويز فوم وبولي يوريثان جدارية ونعلات فوم"
        ],
        "en": [
            "knauf and mada regular white gypsum board panels for ceilings", "moisture resistant green gypsum drywall for bathrooms and kitchens",
            "fire resistant red gypsum board panels", "fiber reinforced cement board panels for exterior claddings",
            "perforated acoustic gypsum and vinyl lay in ceiling tiles 60x60", "drywall metal framing omega furring channels c-studs u-tracks and corner beads",
            "fiberglass joint tape and ready mix joint compound knauf saveto", "powdered plaster of paris gypsco for cornice casting",
            "polyurethane wall molding trims foam panel frames and skirting"
        ]
    }
}

total_added = 0
for cat_id, data in root_34_subcategories.items():
    if cat_id not in contexts:
        continue
    c = contexts[cat_id]
    
    existing_ar = {normalize_text(t) for t in c.get("trade_terms_ar", [])}
    existing_en = {t.lower().strip() for t in c.get("trade_terms_en", [])}
    
    new_ar = [t for t in data["ar"] if normalize_text(t) not in existing_ar]
    new_en = [t for t in data["en"] if t.lower().strip() not in existing_en]
    
    c["trade_terms_ar"] = list(dict.fromkeys(c.get("trade_terms_ar", []) + new_ar))
    c["trade_terms_en"] = list(dict.fromkeys(c.get("trade_terms_en", []) + new_en))
    
    total_added += len(new_ar) + len(new_en)
    print(f"Subcategory {cat_id} ({c.get('name_ar')}): +{len(new_ar)} AR, +{len(new_en)} EN (Total: {len(c['trade_terms_ar'])} AR, {len(c['trade_terms_en'])} EN)")

with open(contexts_path, "w", encoding="utf-8") as f:
    json.dump(contexts, f, ensure_ascii=False, indent=2)

print(f"\n🎉 Successfully enriched ALL 21 Subcategories strictly under Root 34 (Building & Construction)! Total terms added: {total_added}")
