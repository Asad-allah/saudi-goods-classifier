import json
from pathlib import Path
from app.nlp.normalizer import normalize_text, compact_text

contexts_path = Path("storage/catalog/saudi_market_category_contexts.json")
with open(contexts_path, "r", encoding="utf-8") as f:
    contexts = json.load(f)

# Define carefully separated, non-conflicting terms for each parent/child category
construction_catalog_enrichments = {
    # 🪵 54: الأخشاب وأخشاب الطوبار والأبواب (Root: 34)
    "54": {
        "ar": [
            "خشب بليود كوري", "خشب بليود ماليزي", "خشب بليود اسود فيلم فيس", "بليود طوبار صبة",
            "الواح بليود 18 ملم", "خشب سويدي طوبار", "خشب لاتيه", "خشب ام دي اف MDF",
            "خشب اتش دي اف HDF", "خشب ميلامين", "خشب كونتر", "خشب سنديان طبيعي",
            "خشب زان احمر", "خشب تيك وبلوط", "خشب قشرة طبيعية", "عوارض خشبية",
            "مراين خشب طوبار", "مربوع خشب 4 في 4", "لوح خشب لاتزانة", "الواح موسكي",
            "باركيه خشب ارضيات", "بديل الخشب داخلي", "بديل الخشب خارجي WPC", "ابواب خشب سويدي",
            "ابواب كبس شامي", "ابواب خشب قشرة زان", "حلوق خشبية", "كوالين ومفصلات ابواب خشب",
            "مسامير خشب وسنارة", "الواح خشب مضغوط صاج", "خشب سويدي مجفف", "خشب سنديان امريكي"
        ],
        "en": [
            "film faced plywood", "marine plywood", "shuttering plywood", "18mm plywood sheets",
            "white wood timber", "swedish timber", "mdf boards", "hdf panels",
            "melamine faced boards", "blockboard panels", "solid oak wood", "red beech wood",
            "teak timber", "natural wood veneer", "wooden joists and beams", "shuttering battens",
            "wooden studs 4x4", "latzana wood boards", "wooden parquet flooring", "wpc wall cladding",
            "wooden flush doors", "wooden door frames", "wood fasteners and screws", "particle boards",
            "kiln dried swedish wood", "american red oak timber"
        ]
    },

    # 🧱 55: حديد التسليح (Rebar, Stirrups, BRC Mesh, Tie Wire) (Root: 34)
    "55": {
        "ar": [
            "حديد سابك تسليح", "حديد الراجحي", "حديد الاتفاق", "حديد وطني", "حديد اليمامة",
            "حديد تسليح 8 ملم", "حديد تسليح 10 ملم", "حديد تسليح 12 ملم", "حديد تسليح 14 ملم",
            "حديد تسليح 16 ملم", "حديد تسليح 18 ملم", "حديد تسليح 20 ملم", "حديد تسليح 25 ملم",
            "حديد تسليح 32 ملم", "ربطة حديد تسليح", "طن حديد سابك", "تريلا حديد تسليح",
            "شبك حديد ارضيات", "شبك بي ار سي BRC", "شبك صبة ارضية", "كانات حديد جاهزة",
            "كانات تسليح اعمدة", "سلك تربيط حديد", "سلك رباط مجلفن", "مكنة ثني حديد",
            "مقص حديد تسليح", "طعاجه حديد", "بسكوت خرساني للحديد", "كراسي حديد تسليح",
            "مادة تزريع حديد ايبوكسي", "غراء تزريع اسياخ هيسكي", "صلب كربوني للخرسانة", "اسياخ حديد مبروم"
        ],
        "en": [
            "debar steel bars", "deformed steel bars", "sabic rebar", "rajhi steel",
            "al ittefaq steel", "rebar bundles", "8mm rebar", "10mm rebar", "12mm rebar",
            "16mm rebar", "20mm rebar", "25mm rebar", "32mm rebar", "brc welded mesh",
            "concrete reinforcing mesh", "preformed steel stirrups", "tie wire rolls",
            "galvanized binding wire", "rebar cutters", "bar benders", "rebar spacers",
            "epoxy rebar anchoring adhesive", "chemical anchor studs", "carbon steel rebar"
        ]
    },

    # 🔌 56: مواد تمديدات الكهرباء الإنشائية (Root: 34)
    "56": {
        "ar": [
            "كابلات الرياض نحاس", "كابلات بحرة", "كابلات الفنار", "كابلات مسلحة دفان",
            "كيابل الومنيوم جهد منخفض", "اسلاك كهرباء معزولة 2.5 ملم", "اسلاك كهرباء 4 ملم",
            "اسلاك كهرباء 6 ملم", "اسلاك 10 ملم و 16 ملم", "ليات كهرباء برتقالي حمراء",
            "ليات فلكسبل مرنة", "ليات جرجور كهرباء", "جلب مواسير كهرباء", "علب ماجيك بوش",
            "قسامات كهرباء بلاستيك", "طبالين كهرباء الفنار", "لوحات توزيع رئيسية",
            "قواطع شنايدر الكتريك", "قواطع ام سي بي MCB", "قواطع ام سي سي بي MCCB",
            "قواطع ايرث ليكج RCD", "مفاتيح وافياش الفنار الترا", "افياش باناسونيك وليجراند",
            "مفتاح مكيف 45 امبير", "مفتاح سخان 20 امبير", "ترامل نحاسية", "مواسير ترنك حوامل كابلات",
            "كيبل تري حديد مجلفن", "قضيض نحاس ارضي للتأريض", "مانعات صواعق كهربائية"
        ],
        "en": [
            "riyadh cables", "bahra electric cables", "alfanar electrical cables",
            "armored underground cables", "low voltage aluminum cables", "insulated copper wire 2.5mm",
            "electric building wires 4mm", "electric wires 6mm", "pvc electrical conduits",
            "flexible corrugated conduits", "electrical junction boxes", "flush mounting boxes",
            "alfanar distribution boards", "main electrical panels", "schneider electric circuit breakers",
            "miniature circuit breakers mcb", "molded case circuit breakers mccb",
            "residual current devices rcd", "alfanar electrical switches and sockets",
            "panasonic wall switches", "45a air conditioner switches", "20a water heater switches",
            "cable trays and trunking", "perforated galvanized cable ladders", "earthing copper rods",
            "lightning protection rods"
        ]
    },

    # 🧱 57: مواد البناء والأحجار والخرسانة والبلك ومواد الرصف والدهانات (Root: 34)
    "57": {
        "ar": [
            "اسمنت بورتلاندي عادي", "اسمنت اليمامة", "اسمنت السعودية", "اسمنت نجران",
            "اسمنت مقاوم للاملاح كبريتات", "اسمنت ابيض رويال", "شيكارة اسمنت 50 كجم",
            "بالة اسمنت طبالي", "خرسانة جاهزة ريدي مكس", "صبة خرسانة نظافة",
            "صبة خرسانة اعمدة واسقف", "خرسانة رغوية فوم كونكريت", "بلك بركاني معزول جفالي",
            "بلك اسمنتي مصمت", "بلك اسمنتي مفرغ 20 سم", "بلك اسمنتي 15 سم و 10 سم",
            "بلك سيبوركس خفيف معزول", "طوب احمر فخاري مفرغ", "طوب احمر اليمامة",
            "بلك هوردي اسقف", "حجر الرياض طبيعي", "حجر طبيعي مجلي ومنشور", "رخام ارضيات وجدران",
            "جرانيت محلي وورود", "درج رخام وترابيع", "كراتين سيراميك وبورسلان",
            "بورسلان هندي واسباني", "مغاسل رخام وبورسلان", "انترلوك ارضيات وتشبيك",
            "بلدورة خرسانية ارصفة", "غراء بلاط وسيراميك سافيتو", "غراء فيتونيت بوليفكس",
            "غراء سيكا سيرام", "روبة ترويبة فوسام", "معجون وشبك لياسة جدران",
            "زوايا فايبر وزوايا لياسة", "صوف صخري عازل براميل", "عازل بيتومين مطاطي قار",
            "رولات عازل دراي شيلد", "فوم عازل بولي يوريثان", "الواح جبسون بورد كناوف",
            "الواح جبس مدى اخضر مقاوم للرطوبة", "الواح جبس احمر مقاوم للحريق", "شاسيهات وصاج جبس بورد",
            "دهانات جوتن براميل", "دهانات الجزيرة", "بويه ربع لمعة ومطفي", "سيلر وبرايمر دهانات",
            "معجون دهان داخلي وخارجي", "بروفايل واجهات خارجية"
        ],
        "en": [
            "ordinary portland cement opc", "yamama cement", "saudi cement",
            "sulfate resistant cement src", "white portland cement", "50kg cement bags",
            "ready mix concrete", "foam concrete lightweight", "volcanic insulated blocks",
            "solid concrete blocks", "hollow concrete blocks 20cm", "aac autoclaved aerated concrete siporex",
            "red clay bricks", "hourdi hollow ceiling blocks", "riyadh natural limestone",
            "polished natural marble", "saudi granite slabs", "ceramic and porcelain floor tiles",
            "interlock paving stones", "concrete curbstones", "saveto tile adhesive",
            "vetonite polyfix tile glue", "sika tile mortar", "fosroc tile grout",
            "wall plastering mesh and wire", "fiber corner beads", "rockwool thermal insulation",
            "elastomeric bitumen waterproofing", "bituminous membrane rolls", "polyurethane spray foam",
            "knauf gypsum board panels", "mada moisture resistant green drywall", "fire rated red gypsum panels",
            "metal drywall framing studs", "jotun architectural paints", "jazeera paints",
            "acrylic wall primers", "wall putty compound", "exterior profile texture paint"
        ]
    },

    # 🚰 125: الصرف الصحي والسباكة الإنشائية (Root: 125)
    "125": {
        "ar": [
            "مواسير نيبرو للصرف الصحي uPVC", "مواسير القبلان خضراء PPR", "مواسير حراري تغذية",
            "مواسير تصريف 4 بوصة", "مواسير تصريف 6 بوصة و 8 بوصة", "اكواع وتيهات وموزعات سباكة",
            "جلب ورادياتير تقليل", "غراء مواسير حار تانجيت", "محابس دفن كروم", "محابس كرات نحاس إيطالي",
            "رداد صرف صحي مانع رجوع", "صفاية ارضية ستانلس ستيل", "غرف تفتيش ومانهول بولي ايثيلين",
            "اغطية مانهول دكتايل C250 و D400", "خزانات مياه فايبر جلاس الزامل",
            "خزانات بولي ايثيلين افقي وعمودي", "عوامات خزانات كهربائية وميكانيكية",
            "مضخات مياه ودينمو ضغط كالبيدا", "سيفونات مدفونة جروهي وجبيريت",
            "خلاطات مياه ومغاسل وشطافات", "شاورات وبانيوهات وجاكوزي"
        ],
        "en": [
            "upvc drainage pipes nibro", "ppr green pipes al qablan", "thermal water supply pipes",
            "4 inch sewer pipes", "6 inch drainage pipes", "upvc elbows tees and fittings",
            "tangit pipe cement glue", "concealed brass ball valves", "non-return sewage valves",
            "stainless steel floor drains", "polyethylene inspection chambers manholes",
            "ductile iron manhole covers", "zamil fiberglass water storage tanks",
            "polyethylene horizontal water tanks", "water tank float switches",
            "calpeda water booster pumps", "grohe concealed cisterns", "geberit toilet frames",
            "bathroom mixers faucets and bidets", "shower trays and enclosures"
        ]
    },

    # 🏠 140: البيوت الجاهزة والبركسات والكرفانات (Root: 140)
    "140": {
        "ar": [
            "بركسات موقع ومكاتب مهندسين", "كرفانات غرف ساندوتش بانل", "غرف جاهزة متنقلة بركس",
            "مجالس خارجية جاهزة", "مستودعات وهناجر حديدية جاهزة", "مظلات مواقف سيارات وسواتر",
            "الواح ساندوتش بانل معزولة صوف صخري", "الواح ساندوتش بانل بولي يوريثان",
            "شينكو معزول فوم", "قواعد كرفانات شاصي حديد", "دورات مياه متنقلة فيبر جلاس جاهزة",
            "اكشاك حراسة امنية معزولة", "مكاتب مشاريع متحركة"
        ],
        "en": [
            "portable site cabins", "sandwich panel porta-cabins", "prefabricated modular accommodation",
            "prefabricated site offices", "steel prefab warehouses and hangars", "car parking sheds and fences",
            "rockwool insulated sandwich panels", "polyurethane sandwich panels", "insulated foam corrugated sheets",
            "heavy duty cabin chassis", "portable fiberglass toilet cabins", "security guard booths",
            "mobile project office containers"
        ]
    },

    # 🔩 164: المواد والقطاعات والمنتجات الحديدية والمعدنية (Root: 34)
    "164": {
        "ar": [
            "كمرات حديد جسور H-beam", "كمرات حديد I-beam", "كمرات مجرى U-channel",
            "زوايا حديد متساوية وغير متساوية", "تيوبات حديد مربعة ومستطيلة", "تيوب حديد مجلفن وسياه",
            "مواسير حديد سوداء مجلفنة", "صاج حديد اسود مدرفل", "صاج حديد مجلفن ومبزر",
            "شبك بقلاوة حديد ممدد", "صاج معرج شينكو ملون", "اسلاك شائكة وشبك سياج مزارع",
            "درابزينات حديد مشغول ليزر", "بوابات حديد قص ليزر", "مفصلات ابواب حديد ثقيلة",
            "فلانجات حديد ومواسير ضغط", "براغي وصواميل تسليح عالية الصلابة", "رصاص ومثبتات حديد خرسانية",
            "بليتات حديد قواعد اعمدة", "شبك حماية ومناخل حديد"
        ],
        "en": [
            "structural steel h-beams", "structural steel i-beams", "steel u-channels",
            "equal and unequal steel angles", "square and rectangular hollow sections",
            "galvanized steel tubes", "black and galvanized steel pipes", "hot rolled steel sheets",
            "chequered steel floor plates", "expanded metal mesh", "corrugated metal sheeting zinc",
            "barbed wire and chainlink fencing", "wrought iron and laser cut railings",
            "laser cut steel gates", "heavy duty steel hinges", "steel pipe flanges",
            "high tensile structural bolts and nuts", "concrete anchor expansion bolts",
            "steel base plates", "protective wire mesh screens"
        ]
    }
}

# Apply strictly with complete deduplication
total_added_ar = 0
total_added_en = 0

for cat_id, data in construction_catalog_enrichments.items():
    if cat_id not in contexts:
        continue
    c = contexts[cat_id]
    
    # Existing normalized
    existing_ar = {normalize_text(t) for t in c.get("trade_terms_ar", [])}
    existing_en = {t.lower().strip() for t in c.get("trade_terms_en", [])}
    
    new_ar = [t for t in data["ar"] if normalize_text(t) not in existing_ar]
    new_en = [t for t in data["en"] if t.lower().strip() not in existing_en]
    
    c["trade_terms_ar"] = list(dict.fromkeys(c.get("trade_terms_ar", []) + new_ar))
    c["trade_terms_en"] = list(dict.fromkeys(c.get("trade_terms_en", []) + new_en))
    
    total_added_ar += len(new_ar)
    total_added_en += len(new_en)
    print(f"Cat {cat_id} ({c.get('name_ar')}): +{len(new_ar)} AR, +{len(new_en)} EN terms (Total: {len(c['trade_terms_ar'])} AR, {len(c['trade_terms_en'])} EN)")

with open(contexts_path, "w", encoding="utf-8") as f:
    json.dump(contexts, f, ensure_ascii=False, indent=2)

print(f"\n🎉 Successfully enriched construction contexts: Added {total_added_ar} pristine Arabic and {total_added_en} English terms with zero duplication!")
