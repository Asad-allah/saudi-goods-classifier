import json
from pathlib import Path
from app.nlp.normalizer import normalize_text

contexts_path = Path("storage/catalog/saudi_market_category_contexts.json")
with open(contexts_path, "r", encoding="utf-8") as f:
    contexts = json.load(f)

# -----------------------------------------------------------------------------
# Category 146: الأثاث الجديد (Root: 133 الأثاث) - Furniture, Carpets & Home Furnishings
# -----------------------------------------------------------------------------
furniture_new_ar = [
    # 🧶 السجاد والموكيت والمفروشات الأرضية (Carpets, Rugs, Mats, Flooring)
    "سجاد", "سجاد تركي فاخر", "سجاد ايراني كاشان وقم", "سجاد ممرات طويل رنر", "سجاد صوف كلاسيكي",
    "سجاد حرير بلجيكي", "سجاد مودرن شاج ووبر عالي", "سجاد مساجد رولات محراب اخضر واحمر", "سجاد صلاة اسفنجي وطبي",
    "سجاد صلاة فردي ومطرز", "موكيت ارضيات امريكي وسعودي رولات", "موكيت مكاتب وفنادق مربعات تايلز بلاطات",
    "زل وزوالي كراتين ورولات", "بساط ارضي تراثي ومجالس عربية", "مدات ومفارش ارضية كشتات ورحلات",
    "دعاسات ابواب ومداخل خشنة وناعمة", "لباد موكيت وسجاد عازل فوم سماكة 8 و 10 ملم", "سجاد اطفال ورسومات كرتونية",
    "سجاد حصير وخيزران وبامبو", "سجاد دائري وبيضاوي",

    # 🛋️ الكنب والمجالس والمفروشات المنزلية (Living Room, Sofas, Majlis)
    "كنب مودرن زاوية حرف ال وحرف يو", "كنب كلاسيكي مذهب ومحفور", "اطقم كنب صالات ومجالس رجال ونساء",
    "مجالس عربية ارضية ومساند ظهر ومرتكى وتكايا", "جلسات مغربية وباطرمة سدادر", "كراسي ريلاكس واسترخاء ليزي بوي",
    "بفات وكراسي بوف مفردة", "طاولات شاي وخدمة طقم 5 قطع رخام وزجاج وخشب", "طاولات تلفزيون وشاشات وبوفيهات",
    "مكتبات خشبية وديكورات جدارية وارفف", "ستائر قماشية وتعتيم بلاك اوت وشيفون ودانتيل",

    # 🛏️ غرف النوم والمراتب والمفارش (Bedrooms, Mattresses, Bedding)
    "غرف نوم رئيسية ماستر كينج سايز خشب", "غرف نوم اطفال ومواليد وسراير دورين", "سراير نوم هيدبورد منجد مخمل وجلد",
    "مراتب سرير طبية زنبركية بوكيت وسبرينج", "مراتب فوم ميموري فوم ولاتكس", "مفارش سرير ولحافات فندقية قطن كراتين",
    "مخدات ووسائد طبية وميموري فوم وريش", "واقي مرتبة ضد الماء حامي مراتب", "دواليب ملابس وخزائن دريسنج روم وتسريحات",
    "كمودينات وطاولات سرير جانبية",

    # 🍽️ طاولات الطعام والأثاث المكتبي والخارجي (Dining, Office & Outdoor)
    "طاولات طعام 6 و 8 و 12 كرسي رخام وخشب", "كراسي سفرة وطعام منجدة", "كراسي بار وطاولات مطبخ",
    "اثاث مكتبي مكاتب مدير وموظفين وكراسي دوارة هيدروليك", "طاولات اجتماعات وكونترات استقبال",
    "دواليب ملفات خشبية وحديدية", "جلسات خارجية حدائق والمنيوم وخيزران راتان مقاوم للشمس والمطر",
    "مظلات حدائق ومراجيح وجلسات مسابح", "جزمات وخزائن احذية ومرايات مداخل"
]

furniture_new_en = [
    # 🧶 Carpets, Rugs & Floor Mats
    "carpets", "luxury turkish carpets", "persian rugs", "hallway runner rugs", "classic wool carpets",
    "belgian silk carpets", "modern shaggy rugs", "mosque prayer carpet rolls", "padded orthopedic prayer rugs",
    "individual embroidered prayer mats", "commercial and residential wall to wall moquette rolls", "office carpet tiles squares",
    "floor rugs and mats", "traditional arabic majlis rugs", "picnic and camping floor mats",
    "entryway welcome doormats", "carpet underlay foam padding 8mm 10mm", "kids nursery play rugs",
    "bamboo and jute woven mats", "round and oval area rugs",

    # 🛋️ Sofas & Living Room Sets
    "modern l shaped sectional sofas", "classic carved living room sofas", "upholstered sofa sets and couches",
    "traditional floor majlis seating and armrests", "moroccan salon seating benches", "recliner armchairs lazy boy",
    "ottomans and accent poufs", "nesting coffee tables set marble glass wood", "tv consoles media units and sideboards",
    "bookshelves wall shelves and display units", "curtains draperies blackout and sheer fabrics",

    # 🛏️ Bedrooms & Mattresses
    "master king size bedroom sets", "kids bunk beds and nursery cribs", "upholstered bed frames headboards",
    "orthopedic pocket spring mattresses", "memory foam and latex mattresses", "hotel quality duvet and comforter bedding sets",
    "orthopedic sleeping pillows memory foam down", "waterproof mattress protectors pads", "wardrobes closets and dressing vanities",
    "nightstands and bedside tables",

    # 🍽️ Dining & Office Furniture
    "dining room tables 6 8 12 chairs marble wood", "upholstered dining chairs", "kitchen bar stools",
    "office executive desks ergonomic hydraulic mesh chairs", "conference meeting tables reception desks",
    "wood and metal filing cabinets", "outdoor garden patio rattan furniture weather resistant",
    "garden swings gazebos and pool loungers", "shoe racks cabinets and entryway mirrors"
]

# -----------------------------------------------------------------------------
# Category 145: الأثاث المستعمل (Root: 133 الأثاث) - Used Furniture & Appliances
# -----------------------------------------------------------------------------
furniture_used_ar = [
    "عفش منزل مستعمل بالكامل", "اثاث مستخدم للبيع غرف نوم وكنب", "غرف نوم مستعملة وطني ومستورد",
    "كنب ومجالس مستعملة حراج", "سجاد وموكيت مستعمل نظيف", "طاولات طعام وكراسي مستعملة",
    "مطابخ المنيوم مستعملة فك وتركيب", "مكيفات مستعملة شباك وسبليت حراج", "ثلاجات وغسالات وافران مستعملة",
    "نقل عفش واثاث مع الفك والتركيب والتغليف", "دينا نقل عفش داخل وخارج الرياض وجدة", "كراتين نقل عفش وتغليف اثاث مستخدم"
]

furniture_used_en = [
    "used home furniture full house lot", "second hand furniture for sale", "used master bedroom sets",
    "used sofa sets and arabic majlis", "used clean carpets and rugs", "used dining tables and chairs",
    "used aluminum kitchen cabinets", "used window and split air conditioners", "used refrigerators washing machines ovens",
    "furniture relocation house moving dismantling packing", "truck house moving service", "moving cardboard boxes bubble wrap"
]

# -----------------------------------------------------------------------------
# Category 160: مواد النسيج والخياطة (Root: 160) - Fabrics, Textiles & Sewing
# -----------------------------------------------------------------------------
textiles_ar = [
    "اقمشة ثياب رجالية صوف وخلايا وقطن ياباني وكوري كراتين وطاقات", "اقمشة نسائية حرير وشيفون وتول وجاكار ودانتيل",
    "اقمشة عبايات وطرح كريب وانترنت وصالونا طاقات رولات", "اقمشة تنجيد كنب ومجالس مخمل وجلد وجاكار وشانيل ومقاوم للسوائل",
    "اقمشة ستائر بلاك اوت وشيفون وتطريز", "اقمشة قطن بوبلين ولينن وكتان", "بكرات خيوط خياطة بوليستر وقطن والوان مشكلة درازن",
    "خيوط تطريز وتريكو وصوف كروشيه شلل", "سحابات وزمامات معدنية وبلاستيكية مقاسات رولات", "ازرار قمصان وثياب وبدلات كراتين",
    "كلف واشرطة وتطريزات ودانتيل وخردوات خياطة", "فازلين حشو وقماش تقوية ياقات واساور رولات", "مكائن خياطة صناعية ومنزلية جوكي وسنجر وبراذر",
    "مقصات قماش تفصيل واقلام تباشير خياطة ومتر قياس", "ابر خياطة يد ومكائن ودبابيس مشابك كراتين"
]

textiles_en = [
    "mens thobe suiting fabrics wool cotton japanese rolls", "womens dress fabrics silk chiffon tulle lace jacquard",
    "abaya fabrics crepe salonah internet fabric bolts", "furniture upholstery fabrics velvet leather jacquard waterproof",
    "curtain fabrics blackout sheer embroidery drapery", "cotton poplin linen and canvas fabrics", "sewing thread spools polyester cotton colors box",
    "embroidery yarns and knitting crochet wool skeins", "metal and nylon zippers rolls bulk", "clothing shirt and suit buttons bulk",
    "sewing trims ribbons lace borders haberdashery", "interfacing fusible fabric collars cuffs rolls", "industrial sewing machines juki singer brother",
    "tailor fabric shears chalk markers measuring tapes", "hand and machine sewing needles safety pins boxes"
]

# -----------------------------------------------------------------------------
# Category 169: الأسفنج (Root: 169 الأسفنج) - Foam, Sponge & Upholstery Padding
# -----------------------------------------------------------------------------
foam_ar = [
    "اسفنج ضغط عالي 40 و 50 و 60 كراتين وبلوكات", "اسفنج تنجيد كنب ومجالس الواح ورولات", "اسفنج مراتب مضغوط سوبر سوفت",
    "اسفنج ميموري فوم طبي لزج مرن", "اسفنج عازل صوت اهرامات واستوديوهات فوم صوتي", "اسفنج فلتر وبوليريثان",
    "رولات فوم اسفنج سماكات 1 سم و 2 سم و 5 سم و 10 سم", "اسفنج مساند وتكايا كتل مقطعة", "اسفنج تنظيف وغسيل سيارات ومطابخ",
    "اسفنج تغليف وحماية بضائع ضد الصدمات"
]

foam_en = [
    "high density foam blocks density 40 50 60", "furniture upholstery foam sheets and rolls", "compressed super soft mattress foam",
    "medical memory foam visco elastic", "acoustic soundproofing foam pyramid panels", "polyurethane and filter foam",
    "foam sponge rolls thickness 1cm 2cm 5cm 10cm", "pre cut foam cushions and armrests", "cleaning sponges for cars and kitchens",
    "protective packaging foam cushioning"
]

# Apply updates to contexts
def update_cat(cat_id, name_ar, name_en, root_id, root_name_ar, root_name_en, terms_ar, terms_en, desc_ar, desc_en):
    c = contexts.get(str(cat_id), {})
    c["good_type_id"] = int(cat_id)
    c["name_ar"] = name_ar
    c["name_en"] = name_en
    c["root_id"] = root_id
    c["root_name_ar"] = root_name_ar
    c["root_name_en"] = root_name_en
    
    existing_ar = {normalize_text(t) for t in c.get("trade_terms_ar", [])}
    new_ar = [t for t in terms_ar if normalize_text(t) not in existing_ar]
    c["trade_terms_ar"] = list(dict.fromkeys(c.get("trade_terms_ar", []) + new_ar))
    c["trade_terms_en"] = list(dict.fromkeys(terms_en))
    c["market_context_ar"] = desc_ar
    c["market_context_en"] = desc_en
    contexts[str(cat_id)] = c

update_cat(
    146, "الأثاث الجديد", "New Furniture, Carpets and Furnishings",
    133, "الأثاث", "Furniture",
    furniture_new_ar, furniture_new_en,
    "يشمل تصنيف الأثاث الجديد والمفروشات والسجاد (المجموعة الرئيسية: الأثاث): السجاد بجميع أنواعه (سجاد تركي، إيراني، ممرات، صوف، مساجد، سجاد صلاة، موكيت أرضيات رولات وبلاطات، زل وزوالي، دعاسات، لباد)، الكنب والمجالس الأرضية والمغربية، غرف النوم الماستر والأطفال، المراتب الطبية والزنبركية والمفارش، طاولات الطعام والكراسي، والأثاث المكتبي والحدائق.",
    "Category New Furniture and Furnishings under Furniture includes all new home, office and outdoor furniture as well as floor coverings: carpets (turkish, persian, runners, wool, mosque rolls, prayer rugs, moquette rolls and carpet tiles, area rugs, doormats, underlay), sofa sets, arabic floor majlis, master and kids bedrooms, orthopedic mattresses and bedding, dining tables, and executive office furniture."
)

update_cat(
    145, "الأثاث المستعمل", "Used Furniture",
    133, "الأثاث", "Furniture",
    furniture_used_ar, furniture_used_en,
    "يشمل تصنيف الأثاث المستعمل (المجموعة الرئيسية: الأثاث): غرف النوم المستعملة، الكنب والمجالس المستخدمة، السجاد والموكيت المستعمل، الأجهزة المنزلية المستعملة بحراج، وخدمات فك ونقل وتركيب عفش المنازل.",
    "Category Used Furniture under Furniture includes second-hand household furniture, used sofas and majlis, used carpets, second-hand home appliances, and residential furniture moving and relocation."
)

update_cat(
    160, "مواد النسيج والخياطة", "Textile and Sewing Materials",
    160, "مواد النسيج والخياطة", "Textile and sewing materials",
    textiles_ar, textiles_en,
    "يشمل تصنيف مواد النسيج والخياطة والأقمشة (المجموعة الرئيسية: مواد النسيج والخياطة): أقمشة الثياب الرجالية والنسائية والعبايات طاقات ورولات، أقمشة تنجيد الكنب والستائر، خيوط الخياطة والتطريز، السحابات والأزرار والكلف، ماكينات الخياطة ومستلزمات ومقصات التفصيل.",
    "Category Textile and Sewing Materials encompasses garment fabrics (thobe, abaya, silk, cotton bolts), upholstery and curtain fabrics, sewing and embroidery threads, zippers, buttons, trims, industrial sewing machines, and tailoring supplies."
)

update_cat(
    169, "الأسفنج", "Foam and Sponge Materials",
    169, "الأسفنج", "Sponges and Foam",
    foam_ar, foam_en,
    "يشمل تصنيف الأسفنج ومواد الفوم (المجموعة الرئيسية: الأسفنج): اسفنج الضغط العالي لبلوكات تنجيد الكنب والمجالس، اسفنج المراتب والميموري فوم الطبي، رولات الفوم الإسفنجي، اسفنج عزل الصوت للأستوديوهات، واسفنج حماية وتغليف البضائع.",
    "Category Foam and Sponges includes high-density upholstery foam blocks, compressed mattress foam, memory foam, acoustic soundproofing foam panels, foam rolls, and protective packaging cushioning."
)

with open(contexts_path, "w", encoding="utf-8") as f:
    json.dump(contexts, f, ensure_ascii=False, indent=2)

print("✅ Furniture, Carpets, Textiles, and Foam successfully enriched in contexts!")
print(f"📊 Category 146 (الأثاث والسجاد): {len(contexts['146']['trade_terms_ar'])} AR terms | {len(contexts['146']['trade_terms_en'])} EN terms")
print(f"📊 Category 160 (النسيج والأقمشة): {len(contexts['160']['trade_terms_ar'])} AR terms | {len(contexts['160']['trade_terms_en'])} EN terms")
print(f"📊 Category 169 (الأسفنج والفوم):  {len(contexts['169']['trade_terms_ar'])} AR terms | {len(contexts['169']['trade_terms_en'])} EN terms")
