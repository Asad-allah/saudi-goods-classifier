"""Exhaustive bilingual (Arabic/English) ontology for the 37 Saudi logistics root categories."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CategorySpec:
    root_id: int
    name_ar: str
    name_en: str
    domains: tuple[str, ...]
    core_nouns: tuple[str, ...]
    core_nouns_en: tuple[str, ...]
    brands: tuple[str, ...]
    brands_en: tuple[str, ...]
    specs_and_models: tuple[str, ...]
    specs_and_models_en: tuple[str, ...]
    packaging_types: tuple[str, ...]
    packaging_types_en: tuple[str, ...]
    strict_inclusions: tuple[str, ...]
    strict_exclusions: tuple[str, ...]
    disambiguation_anchors: tuple[str, ...]


ROOT_ONTOLOGY: dict[int, CategorySpec] = {
    4: CategorySpec(
        root_id=4,
        name_ar="زراعية",
        name_en="Agricultural",
        domains=("زراعة", "مشاتل", "بيوت محمية", "مزارع", "أسمدة", "ري"),
        core_nouns=(
            "بذور قمح", "بذور طماطم", "شتلات زيتون", "شتلات نخل", "أسمدة يوريا",
            "سماد داب", "تربة بتموس", "بيوت محمية", "شبكات تنقيط", "رشاشات زراعية",
            "أسمدة سائلة", "مبيدات فطرية زراعية", "مبيدات حشرية للمزارع", "مواسير ري زراعي",
            "محابس تنقيط", "فسائل نخل خلاص", "بذور برسيم", "محسنات تربة", "أغطية بيوت بلاستيكية",
            "لي ري زراعي", "مضخات غطاس زراعي", "أسمدة بوتاسيوم", "سماد عضوي معالج",
            "بذور خيار هجين", "شتلات حمضيات", "مغذيات نباتية", "شباك تظليل زراعية"
        ),
        core_nouns_en=(
            "wheat seeds", "tomato seeds", "olive saplings", "palm date seedlings", "urea fertilizer",
            "DAP fertilizer", "peat moss soil", "greenhouse structures", "drip irrigation network", "agricultural sprinklers",
            "liquid fertilizer", "agricultural fungicides", "farm insecticides", "irrigation pipes",
            "drip valves", "Khalas palm shoots", "alfalfa seeds", "soil conditioners", "greenhouse plastic film",
            "irrigation drip hose", "submersible agricultural pump", "potassium fertilizer", "treated organic manure",
            "hybrid cucumber seeds", "citrus saplings", "plant nutrients", "agricultural shade nets"
        ),
        brands=("سابك زراعي", "أراسكو أسمدة", "المهيدب الزراعية", "استرا الزراعية", "سافكو"),
        brands_en=("SABIC Agri-Nutrients", "ARASCO Fertilizer", "Al-Muhaidib Agriculture", "Astra Agricultural", "SAFCO"),
        specs_and_models=("NPK 20-20-20", "يوريا 46%", "لفات 400 متر", "قطر 16 ملم", "حمولة 50 كيس", "ضغط 4 بار"),
        specs_and_models_en=("NPK 20-20-20", "Urea 46% N", "400m rolls", "16mm diameter", "50kg bag load", "4 bar pressure rating"),
        packaging_types=("أكياس 50 كجم", "لفات ليات", "طبالي أسمدة", "شتلات بصناديق", "جوالين 20 لتر"),
        packaging_types_en=("50kg bags", "hose rolls", "fertilizer pallets", "seedling crates", "20L jerrycans"),
        strict_inclusions=("أسمدة", "بذور", "شتلات", "مستلزمات ري مزارع"),
        strict_exclusions=("أعلاف حيوانات", "مواد غذائية", "معدات حفر ثقيلة"),
        disambiguation_anchors=("زراعي", "مزارع", "شتلات", "بذور", "أسمدة", "محميات", "agri", "farm", "fertilizer", "seedling"),
    ),
    5: CategorySpec(
        root_id=5,
        name_ar="صناعية",
        name_en="Industrial",
        domains=("مصانع", "ورش", "خطوط إنتاج", "معدات هيدروليك", "صمامات ومحابس"),
        core_nouns=(
            "صمامات صناعية", "محابس بخار", "تروس حديد", "سيور ناقلة للمصانع",
            "روافع هيدروليكية", "مكائن خراطة", "اسطوانات نيوماتيك", "مضخات هيدروليك صناعية",
            "محركات كهربائية ثلاثية الطور", "قواطع ليزر صناعية", "مكائن لحام صناعي",
            "لوحات تحكم PLC", "بكرات سيور مصانع", "جيربوكس صناعي", "فلاتر هيدروليك ثقيلة",
            "رولمان بلي صناعي", "خراطيم ضغط عالي صناعية", "مكابس هيدروليكية",
            "خطوط تعبئة وتغليف", "روبوتات تجميع صناعية", "مضخات تفريغ فاكيوم"
        ),
        core_nouns_en=(
            "industrial valves", "steam gate valves", "steel spur gears", "factory conveyor belts",
            "hydraulic lift cylinders", "lathe machines", "pneumatic air cylinders", "industrial hydraulic pumps",
            "three-phase electric motors", "industrial laser cutters", "heavy duty welding machines",
            "PLC control panels", "conveyor pulleys", "industrial gearboxes", "heavy hydraulic filters",
            "industrial ball bearings", "high pressure industrial hoses", "hydraulic press machines",
            "filling and packaging lines", "industrial assembly robots", "vacuum pumps"
        ),
        brands=("شنايدر", "سيمنز", "ABB", "بوش ريكسروث", "دانفوس", "باركر"),
        brands_en=("Schneider Electric", "Siemens", "ABB Industrial", "Bosch Rexroth", "Danfoss", "Parker Hannifin"),
        specs_and_models=("3 Phase 380V", "10 Bar", "50 HP", "PLC S7-1200", "ضغط 200 بار", "1400 RPM"),
        specs_and_models_en=("3-Phase 380V", "10 Bar rating", "50 HP motor", "PLC S7-1200", "200 Bar pressure", "1400 RPM"),
        packaging_types=("صناديق خشبية", "طبالي معدات", "قواعد حديد", "حمولة ونش"),
        packaging_types_en=("wooden crates", "equipment pallets", "steel skid mounts", "crane rigging bundles"),
        strict_inclusions=("مكائن مصانع", "قطع هيدروليك", "محركات مصانع", "صمامات صناعية"),
        strict_exclusions=("أجهزة منزلية", "قطع غيار سيارات", "إلكترونيات استهلاكية"),
        disambiguation_anchors=("صناعي", "مصنع", "خط إنتاج", "هيدروليك", "ثلاثي الطور", "industrial", "factory", "hydraulic", "pneumatic"),
    ),
    6: CategorySpec(
        root_id=6,
        name_ar="مواد أعمال التعدين أو التحجير",
        name_en="Mining or Fossilization Materials",
        domains=("كسارات", "محاجر", "مناجم", "صخور وركام"),
        core_nouns=(
            "صخور جرانيت خام", "كتل رخام خام", "رمل سيليكا", "حجر جيري للكسارات",
            "جبس صخري خام", "بحص مقاسات", "دفان محاجر", "صلبوخ", "ركام خرساني",
            "بودرة حجر جيري", "أحجار بازلت", "خام فوسفات", "رمل أبيض مغسول", "خام بوكسيت"
        ),
        core_nouns_en=(
            "raw granite blocks", "raw marble quarry blocks", "silica sand", "limestone quarry rock",
            "raw rock gypsum", "graded aggregate crushed stone", "quarry backfill gravel", "sub-base gravel", "concrete aggregate",
            "limestone powder", "basalt quarry stones", "phosphate ore", "washed white silica sand", "bauxite ore"
        ),
        brands=("معادن", "محاجر الرياض", "كسارات اليمامة", "جرانيت نجران"),
        brands_en=("Maaden Mining", "Riyadh Quarries", "Yamama Crushers", "Najran Granite Quarries"),
        specs_and_models=("مقاس 3/4", "مقاس 3/8", "رمل زيرو", "كتل 5 طن", "حمولة قلاب 24 متر"),
        specs_and_models_en=("3/4 inch aggregate", "3/8 inch chip", "zero silica sand", "5 ton quarry blocks", "24 m3 tipper load"),
        packaging_types=("حمولة قلاب", "تريلا صخور", "شحنة تيدر", "أكياس جامبو 1 طن"),
        packaging_types_en=("tipper truckload", "flatbed rock haul", "semi-trailer bulk load", "1-ton jumbo bulk bags"),
        strict_inclusions=("صخور خام", "رمل سيليكا", "حجر جيري", "بحص ودفان"),
        strict_exclusions=("بلاط وسيراميك جاهز", "إسمنت معبأ", "تحف رخام"),
        disambiguation_anchors=("خام", "كسارات", "محاجر", "صخور", "قلاب", "سيليكا", "quarry", "mining", "raw stone", "aggregate", "silica"),
    ),
    10: CategorySpec(
        root_id=10,
        name_ar="منتجات بترولية",
        name_en="Petroleum Products",
        domains=("مشتقات نفطية", "محروقات", "إسفلت", "زيوت أساس"),
        core_nouns=(
            "ديزل", "بنزين 91", "بنزين 95", "كيروسين", "زيت بترولي أساس",
            "إسفلت سائل", "بيتومين عازل", "فحم بترولي", "شحم بترولي ثقيل",
            "نافثا", "وقود طائرات كيروسين", "مازوت وقود أفران", "زيوت هيدروليك بترولية خام"
        ),
        core_nouns_en=(
            "diesel fuel", "gasoline 91 octane", "gasoline 95 octane", "kerosene", "petroleum base oil",
            "liquid asphalt", "bitumen waterproofing grade", "petroleum coke", "heavy petroleum grease",
            "naphtha", "jet A1 kerosene fuel", "heavy fuel oil mazut", "raw petroleum hydraulic fluid"
        ),
        brands=("أرامكو السعودية", "بترومين", "لوبريف", "ساسرف", "سامرف"),
        brands_en=("Saudi Aramco", "Petromin", "Luberef", "SASREF", "SAMREF"),
        specs_and_models=("Euro 5", "درجة 60/70", "براميل 208 لتر", "صهريج 32 ألف لتر"),
        specs_and_models_en=("Euro 5 standard", "grade 60/70 bitumen", "208L steel drums", "32,000L road tanker load"),
        packaging_types=("صهريج تريلا", "براميل حديد 200 لتر", "خزانات IBC", "شحنة وايت محروقات"),
        packaging_types_en=("road tanker truckload", "200L steel drums", "IBC containers", "fuel tanker supply"),
        strict_inclusions=("مشتقات بترولية", "ديزل وبنزين", "إسفلت وبيتومين", "زيوت أساس"),
        strict_exclusions=("زيوت طعام", "بلاستيك مصنع", "منظفات كيميائية"),
        disambiguation_anchors=("بترولي", "أرامكو", "ديزل", "بنزين", "إسفلت", "بيتومين", "محروقات", "petroleum", "diesel", "gasoline", "fuel tanker"),
    ),
    11: CategorySpec(
        root_id=11,
        name_ar="حيوانات حية",
        name_en="LIVE ANIMALS",
        domains=("مواشي", "إبل", "أغنام", "خيول", "طيور ودواجن"),
        core_nouns=(
            "أغنام حري", "خراف نعيمي", "ماعز عارضي", "حيران وجمال", "نوق إبل",
            "أبقار هولشتاين", "خيول عربية أصيلة", "دواجن وصيصان حية", "صقور صيد",
            "تيوس بيشية", "عجول تسمين", "خراف سواكني حية", "طليان نجدي"
        ),
        core_nouns_en=(
            "live Harri sheep", "live Nuaimi sheep", "Aradi goats", "live camels and calves", "she-camels",
            "Holstein dairy cows", "purebred Arabian horses", "live chicks and poultry", "hunting falcons",
            "live Bishi billy goats", "fattening cattle calves", "live Sawakni sheep", "Najdi live lambs"
        ),
        brands=("مزارع الوطنية للمواشي", "إبل الصياهد", "مرابط الخيل العربية", "دواجن الأخوين"),
        brands_en=("Al-Watania Livestock", "Sayahid Camels", "Arabian Stud Stables", "Al-Akhawain Poultry"),
        specs_and_models=("أعمار 6 أشهر", "حمولة دينا 40 رأس", "تريلا طابقين مواشي", "رؤوس حية"),
        specs_and_models_en=("6 months age", "40 head truckload", "double deck livestock trailer", "live head count"),
        packaging_types=("دينا شبك مواشي", "تريلا مواشي مجهزة", "أقفاص طيور مجهزة", "عربة خيل مقفلة"),
        packaging_types_en=("ventilated livestock truck", "double-deck sheep trailer", "ventilated bird crates", "enclosed horse trailer"),
        strict_inclusions=("مواشي حية", "إبل وخيول حية", "دواجن وطيور حية"),
        strict_exclusions=("لحوم مجمدة ومذبوحة", "أعلاف", "أدوية بيطرية"),
        disambiguation_anchors=("حي", "رؤوس", "حري", "نعيمي", "إبل", "حيران", "طليان", "نوق", "live animal", "sheep", "camel", "livestock"),
    ),
    12: CategorySpec(
        root_id=12,
        name_ar="مواد غذائية",
        name_en="Food Items",
        domains=("سوبرماركت", "مواد تموينية", "مشروبات", "معلبات", "مجمدات", "بقوليات", "تمور"),
        core_nouns=(
            "أرز بسمتي", "سكر أبيض ناعم", "زيت دوار الشمس طعام", "زيت زيتون بكر",
            "حليب بودرة مجفف", "معلبات تونة خفيفة", "معجون طماطم صلصة", "مكرونة وشعيرية",
            "تمور سكري مفتل", "تمر خلاص الأحساء", "دجاج مجمد كراتين", "شوكولاتة وبسكويت",
            "شيبس وبطاطس مقرمشة", "شاي أسود كبوس", "قهوة عربي وهيل", "جبنة كاسات ومثلثات",
            "دقيق فاخر ومخبوزات", "لحوم مفرومة مجمدة", "خضار وفواكه طازجة", "عسل نحل طبيعي",
            "شوربة شعيرية", "معلبات فول مدمس", "مايونيز وكاتشب", "حبوب كورن فليكس"
        ),
        core_nouns_en=(
            "basmati rice", "refined white sugar", "sunflower cooking oil", "extra virgin olive oil",
            "instant milk powder", "canned light tuna", "tomato paste sauce", "pasta and vermicelli",
            "Sukkari dates", "Khalas Al-Ahsa dates", "frozen chicken cartons", "chocolates and biscuits",
            "potato chips crisps", "black tea leaves", "Arabic coffee and cardamom", "cream cheese jars",
            "baking flour", "frozen minced meat", "fresh fruits and vegetables", "natural bee honey",
            "noodle soup packs", "canned fava beans", "mayonnaise and ketchup", "breakfast corn flakes"
        ),
        brands=(
            "المراعي", "نادك", "الربيع", "عافية", "أبو كاس", "الشعلان",
            "نيدو", "لونا", "قودي", "بيتي كروكر", "ساديا", "الوطنية دواجن",
            "باجة", "العلالي", "حلواني", "نوتيلا", "كيت كات", "ليبتون"
        ),
        brands_en=(
            "Almarai", "Nadec", "Al Rabie", "Afia", "Abu Kass", "Al Shalan",
            "Nido", "Luna", "Goody", "Betty Crocker", "Sadia", "Al-Watania Poultry",
            "Baja", "Al Alali", "Halwani", "Nutella", "KitKat", "Lipton"
        ),
        specs_and_models=("كيس 40 كجم", "كرتون 24 حبة", "علب 400 جرام", "شد 12 حبة", "جالون 5 لتر"),
        specs_and_models_en=("40kg sack", "24-pack carton", "400g cans", "12-pack bundle", "5L cooking gallon"),
        packaging_types=("كراتين مواد غذائية", "طبالي تموين", "أكياس خيش أرز", "شحنة ثلاجة مبردة"),
        packaging_types_en=("food grocery cartons", "wholesale grocery pallets", "jute rice sacks", "reefer refrigerated truckload"),
        strict_inclusions=("أطعمة", "مشروبات معلبة وعصائر", "تموين", "مجمدات ومأكولات"),
        strict_exclusions=("مياه معبأة مستقلة", "مواشي حية", "أعلاف حيوانات", "منظفات منزلية"),
        disambiguation_anchors=("طعام", "غذائي", "تموين", "أرز", "تونة", "سكر", "حليب", "بسكوت", "شوكولاته", "food", "grocery", "rice", "cooking oil", "dates"),
    ),
    13: CategorySpec(
        root_id=13,
        name_ar="نقل المركبات",
        name_en="Vehicle Transportation",
        domains=("سيارات", "سطحات", "شاحنات", "تشليح", "نقل معارض وموانئ"),
        core_nouns=(
            "سيارة تويوتا كامري", "هيونداي سوناتا جديدة", "جيب لاندكروزر",
            "شاحنة ايسوزو دينا", "سيارة مصدومة للتشليح", "سيارات معارض جديدة",
            "فورد تورس", "نيسان باترول", "لكزس صالون", "سيارة عطلانة نقل سطحة",
            "باص تويوتا هايس", "هايلوكس غمارة وغمارتين", "سيارة كهربائية تسلا", "شاحنة مرسيدس اكتروس"
        ),
        core_nouns_en=(
            "Toyota Camry sedan", "Hyundai Sonata brand new", "Toyota Land Cruiser SUV",
            "Isuzu Dyna light truck", "accident damaged car for scrap", "showroom brand new cars",
            "Ford Taurus", "Nissan Patrol SUV", "Lexus luxury sedan", "broken car for flatbed recovery",
            "Toyota Hiace van", "Hilux single and double cabin", "Tesla electric vehicle", "Mercedes Actros heavy truck"
        ),
        brands=("تويوتا", "هيونداي", "نيسان", "فورد", "مرسيدس", "ايسوزو", "كيا", "لكزس", "جيلي", "ام جي"),
        brands_en=("Toyota", "Hyundai", "Nissan", "Ford", "Mercedes-Benz", "Isuzu", "Kia", "Lexus", "Geely", "MG"),
        specs_and_models=("موديل 2024", "موديل 2023", "محرك 2.5", "مصدومة بدون لوحات", "بطاقة جمركية"),
        specs_and_models_en=("2024 model year", "2023 model", "2.5L engine", "accident salvage non-runner", "customs clearance papers"),
        packaging_types=("سطحة هيدروليك فردية", "لوبد نقل معدات", "تريلا حاملة سيارات 8 حبات"),
        packaging_types_en=("hydraulic flatbed recovery", "lowbed equipment carrier", "8-car double deck car carrier"),
        strict_inclusions=("مركبات وسيارات كاملة منقولة"),
        strict_exclusions=("قطع غيار مفردة", "إطارات وبطاريات سيارات منفصلة", "دراجات نارية"),
        disambiguation_anchors=("سيارة", "مركبة", "سطحة", "معارض", "تشليح سيارة", "مصدومة نقل", "vehicle", "car carrier", "recovery flatbed", "salvage car"),
    ),
    34: CategorySpec(
        root_id=34,
        name_ar="مواد البناء و التشييد",
        name_en="Building And Construction Items",
        domains=("مقاولات", "إسمنت", "حديد تسليح", "بلك وطوب", "تشطيبات", "سباكة وكهرباء إنشائية"),
        core_nouns=(
            "حديد تسليح سابك", "إسمنت بورتلاندي معبأ", "بلك بركاني معزول", "طوب أحمر مفرغ",
            "سيراميك وبورسلان أرضيات", "دهانات وبويات داخلية", "مواسير سباكة كلاس 5",
            "أسلاك كهرباء مباني", "ألواح جبس بورد", "خشب بليود للبناء", "رخام تشطيب أرضيات",
            "عوازل فوم أسطح", "شبك حديد أرضيات", "غراء بلاط وسيراميك", "أبواب وشبابيك ألمنيوم",
            "خلاطات ومغاسل تشطيب", "قواطع جبسية", "صوف صخري عازل"
        ),
        core_nouns_en=(
            "SABIC rebar steel", "bagged Portland cement", "insulated volcanic blocks", "hollow red clay bricks",
            "floor porcelain and ceramic tiles", "interior emulsion paints", "Class 5 plumbing pipes",
            "building electrical wires", "gypsum board panels", "film faced plywood", "finished floor marble",
            "roof PU foam insulation", "steel welded mesh", "tile and ceramic adhesive glue", "aluminum doors and windows",
            "sanitary mixers and basins", "drywall gypsum partitions", "rockwool thermal insulation"
        ),
        brands=("سابك حديد", "إسمنت اليمامة", "دهانات الجزيرة", "جوتن بويات", "الفنار كابلات", "الخزف السعودي", "نيبرو سباكة"),
        brands_en=("SABIC Steel", "Yamama Cement", "Jazeera Paints", "Jotun Paints", "Alfanar Cables", "Saudi Ceramics", "Nepro Pipes"),
        specs_and_models=("حديد 16 ملم", "حديد 14 ملم", "أكياس 50 كجم", "بلك 20*40", "مواسير 4 بوصة", "سلك 4 ملم"),
        specs_and_models_en=("16mm rebar", "14mm rebar", "50kg cement bags", "20x40cm hollow blocks", "4 inch pipes", "4mm2 wire roll"),
        packaging_types=("طبالي إسمنت وبلك", "ربطات حديد تسليح", "كراتين سيراميك", "براميل بويه", "حمولة تريلا تيدر"),
        packaging_types_en=("cement and block pallets", "rebar steel bundles", "ceramic tile cartons", "paint drums 18L", "flatbed trailer load"),
        strict_inclusions=("مواد إنشائية", "حديد تسليح", "إسمنت", "طوب وبلك", "دهانات تشطيب"),
        strict_exclusions=("أثاث منزلي", "صخور خام من الكسارة", "بيوت جاهزة بركسات"),
        disambiguation_anchors=("بناء", "إنشائي", "تسليح", "إسمنت", "بلك", "طوب", "دهان", "سيراميك", "جبس بورد", "construction", "rebar", "cement", "building materials"),
    ),
    125: CategorySpec(
        root_id=125,
        name_ar="الصرف الصحي",
        name_en="Sanitation",
        domains=("شبكات صرف", "مياه عادمة", "غرف تفتيش", "مضخات غاطسة مجاري"),
        core_nouns=(
            "أنابيب صرف صحي سميكة", "غرف تفتيش صرف خرسانية", "أغطية مانهول دكتايل",
            "مضخات مجاري غاطسة ثقيلة", "مواسير صرف برتقالية uPVC", "مصائد دهون للصرف",
            "محابس رداد صرف صحي", "خزانات تحليل صرف بيارات", "شنابر ومناهل صرف صحي"
        ),
        core_nouns_en=(
            "heavy sewage pipes", "precast concrete manhole chambers", "ductile iron manhole covers",
            "submersible sewage sump pumps", "orange uPVC drainage pipes", "drainage grease traps",
            "sewage check valves", "septic treatment tanks", "sanitation manhole frame rings"
        ),
        brands=("الوطنية للأنابيب", "نيبرو صرف", "مضخات كروندفوس مجاري", "سعودي مانهول"),
        brands_en=("National Pipes Co", "Nepro Sanitation", "Grundfos Sewage Pumps", "Saudi Manhole"),
        specs_and_models=("قطر 6 بوصة", "قطر 8 بوصة كلاس 4", "مانهول ضغط 40 طن", "مضخة 5 حصان غاطس"),
        specs_and_models_en=("6 inch drainage diameter", "8 inch Class 4 pipe", "D400 40-ton manhole cover", "5 HP submersible pump"),
        packaging_types=("ربطات أنابيب صرف", "طبالي أغطية دكتايل", "صناديق مضخات غاطسة"),
        packaging_types_en=("sewer pipe bundles", "ductile cover pallets", "sump pump wood crates"),
        strict_inclusions=("مستلزمات وشبكات الصرف الصحي والمجاري"),
        strict_exclusions=("مياه شرب معبأة", "صهاريج ماء نظيف", "منظفات ومطهرات عادية"),
        disambiguation_anchors=("صرف صحي", "مجاري", "مانهول", "مياه عادمة", "غرفة تفتيش", "sanitation", "sewage", "drainage", "manhole cover"),
    ),
    126: CategorySpec(
        root_id=126,
        name_ar="صهاريج الماء",
        name_en="Water Tanks",
        domains=("خزانات مياه", "صهاريج نقل ماء", "وايتات ماء"),
        core_nouns=(
            "خزانات مياه فايبر جلاس", "خزانات ماء بولي إيثيلين أفقية", "خزان مياه علوي عمودي",
            "صهريج وايت ماء حديد مجلفن", "خزانات مياه أرضية معزولة", "تانكي ماء للسيارة",
            "خزان مياه 5000 لتر الزامل", "صهريج تريلا لنقل المياه الصالحة للشرب"
        ),
        core_nouns_en=(
            "fiberglass water tanks", "horizontal polyethylene water storage tanks", "vertical rooftop water tanks",
            "galvanized steel water tanker bodies", "insulated underground water cisterns", "vehicle auxiliary water tank",
            "5000 liter water tank Zamil", "potable drinking water road tanker"
        ),
        brands=("الزامل للخزانات", "المهيدب للخزانات", "خزانات الوطني", "فايبر بولي"),
        brands_en=("Al Zamil Water Tanks", "Al Muhaidib Tanks", "Al Watani Poly Tanks", "Fiber Poly Tech"),
        specs_and_models=("سعة 5000 لتر", "سعة 2000 لتر 4 طبقات", "سعة 10000 لتر", "عمودي أبيض"),
        specs_and_models_en=("5000L capacity", "2000L 4-layer tank", "10000L large cistern", "vertical insulated white"),
        packaging_types=("حمولة دينا خزانات", "تريلا صهريج", "خزانات محملة بقواعد"),
        packaging_types_en=("water tank flatbed haul", "water tanker trailer", "skid mounted water storage unit"),
        strict_inclusions=("خزانات وصهاريج المياه بمختلف أحجامها"),
        strict_exclusions=("مياه معبأة كراتين وقوارير", "صهاريج غاز وبترول", "أنابيب صرف"),
        disambiguation_anchors=("خزان ماء", "صهريج ماء", "تانكي مويا", "وايت ماء", "فايبر جلاس ماء", "water tank", "water tanker", "potable water cistern"),
    ),
    127: CategorySpec(
        root_id=127,
        name_ar="صهاريج الغاز",
        name_en="Gas Tanks",
        domains=("غاز البترول المسال", "خزانات غاز مركزية", "اسطوانات غاز صناعي"),
        core_nouns=(
            "خزان غاز مركزي للمنازل", "صهريج نقل غاز مسال LPG", "اسطوانات غاز صناعي أكسجين واستيلين",
            "خزانات غاز بضغط عالي", "اسطوانات غاز طبخ حديد", "صهريج غاز تريلا مصمت",
            "صمامات ومنظمات خزانات الغاز المركزية"
        ),
        core_nouns_en=(
            "central LPG home gas tank", "bulk LPG liquefied petroleum tanker", "industrial gas cylinders oxygen acetylene",
            "high pressure gas storage pressure vessels", "cooking gas domestic steel cylinders", "bulk gas transport road trailer",
            "central gas tank pressure regulators and valves"
        ),
        brands=("شركة الغاز والتصنيع الأهلية غازكو", "GASCO", "خزانات فالكون غاز"),
        brands_en=("National Gas and Industrialization Co GASCO", "GASCO", "Falcon Gas Tanks"),
        specs_and_models=("سعة 1000 لتر مدفون", "سعة 2000 لتر فوق الأرض", "ضغط 25 بار"),
        specs_and_models_en=("1000L underground LPG tank", "2000L above-ground gas tank", "25 bar working pressure"),
        packaging_types=("تريلا صهريج غاز", "طبالي اسطوانات غاز برباط أمان", "قواعد تثبيت خزان"),
        packaging_types_en=("LPG tanker truck", "secured cylinder gas pallet", "skid base gas tank mount"),
        strict_inclusions=("صهاريج وخزانات الغاز واسطواناته"),
        strict_exclusions=("صهاريج ماء", "وقود وبنزين", "مكيفات هواء"),
        disambiguation_anchors=("صهريج غاز", "خزان غاز", "غازكو", "غاز مركزي", "اسطوانات غاز", "gas tank", "LPG tanker", "gas cylinder", "central gas"),
    ),
    129: CategorySpec(
        root_id=129,
        name_ar="قطع غيار",
        name_en="Spares",
        domains=("قطع غيار سيارات", "إطارات وكفرات", "بطاريات مركبات", "زيوت محركات", "ميكانيكا وكهرباء سيارات"),
        core_nouns=(
            "فحمات وأقمشة فرامل", "بواجي وشمعات احتراق", "مساعدات ومقصات أمامية",
            "رديتر ماء سيارة", "دينمو شحن وسلف", "سيور ماكينة ومراوح",
            "كفرات هانكوك مقاس 17", "إطارات ميشلان مقاس 18", "بطاريات سيارات هانكوك 70 أمبير",
            "زيت محرك بترومين 10w40", "زيت قير أوتوماتيك تويوتا", "فلاتر زيت وسيفون وكالة",
            "كمبروسر مكيف سيارة", "مساعدات هيدروليك جيب", "عكوس ومساعدات دركسون",
            "طرمبة بنزين ومضخة وقود", "أذرعة دركسون وجلود مقصات", "كويلات إشعال بواجي"
        ),
        core_nouns_en=(
            "ceramic brake pads and shoes", "spark plugs set", "front shock absorbers and control arms",
            "car engine cooling radiator", "charging alternator and starter motor", "engine serpentine fan belts",
            "Hankook tires 17 inch", "Michelin tires 18 inch", "Hankook 70AH automotive car battery",
            "Petromin 10W40 engine motor oil", "Toyota automatic transmission fluid ATF", "OEM engine oil filter cartridge",
            "car AC compressor pump", "hydraulic shock struts SUV", "drive shafts and steering CV joints",
            "fuel pump assembly", "tie rod ends and suspension bushings", "ignition coils"
        ),
        brands=("بترومين زيوت", "هانكوك إطارات", "تويوتا قطع غيار", "موبار", "اي سي ديلكو", "ميشلان", "بريدجستون", "بوش سيارات", "كاسترول"),
        brands_en=("Petromin Oil", "Hankook Tires", "Toyota Genuine Parts", "Mopar", "ACDelco", "Michelin", "Bridgestone", "Bosch Automotive", "Castrol"),
        specs_and_models=("مقاس 265/65R17", "زيت 5W-30 تخليقي", "بطارية 12V 80AH", "طقم فحمات سيراميك"),
        specs_and_models_en=("265/65R17 tire size", "5W-30 full synthetic oil", "12V 80AH battery", "ceramic brake pads kit"),
        packaging_types=("كراتين قطع غيار", "طبالي بطاريات برباط", "شد إطارات وكفرات", "كراتين جلود وسيفونات"),
        packaging_types_en=("auto parts cartons", "battery strapped pallets", "tire wrapped bundles", "boxed filter kits"),
        strict_inclusions=("قطع غيار مركبات", "إطارات وبطاريات سيارات", "زيوت وفلاتر محركات"),
        strict_exclusions=("سيارات كاملة منقولة", "أجهزة كهربائية منزلية", "زيوت طعام"),
        disambiguation_anchors=("قطع غيار", "فحمات", "كفرات", "بطارية سيارة", "زيت محرك", "بواجي", "رديتر", "spare parts", "brake pads", "tires", "car battery", "engine oil"),
    ),
    131: CategorySpec(
        root_id=131,
        name_ar="الإلكترونيات",
        name_en="Reinforcing",
        domains=("أجهزة ذكية", "شاشات وتلفزيونات", "كمبيوتر ولابتوب", "اتصالات وشواحن", "كاميرات"),
        core_nouns=(
            "شاشات تلفزيون سمارت 65 بوصة", "جوالات آيفون وسامسونج", "أجهزة لابتوب ديل واتش بي",
            "أجهزة آيباد وتابلت", "راوترات وشبكات 5G فايبر", "كاميرات مراقبة هيكفيجن NVR",
            "شواحن متنقلة وباور بانك", "سماعات بلوتوث ولاسلكية", "ساعات ذكية أبل وسمارت",
            "رسيفرات وشاشات عرض بروجكتر", "بلايستيشن واكس بوكس ألعاب", "كيابل شحن ومحولات Type-C",
            "ماوس وكيبورد ميكانيكي", "هارديسك خارجي SSD", "طابعات ليزر مكتبية"
        ),
        core_nouns_en=(
            "65 inch 4K Smart TV", "iPhone and Samsung smartphones", "Dell and HP laptops",
            "iPad and Android tablets", "5G fiber wireless routers", "Hikvision CCTV security cameras NVR",
            "power bank portable chargers", "wireless Bluetooth headphones earbuds", "Apple Watch and smartwatches",
            "digital satellite receivers and projectors", "PlayStation and Xbox gaming consoles", "Type-C charging cables and adapters",
            "mechanical keyboards and mice", "external SSD hard drives", "desktop laser printers"
        ),
        brands=("سامسونج", "أبل", "ال جي شاشات", "سوني", "هواوي", "ديل", "اتش بي", "أنكر", "هيكفيجن", "شاومي"),
        brands_en=("Samsung", "Apple", "LG Electronics", "Sony", "Huawei", "Dell", "HP", "Anker", "Hikvision", "Xiaomi"),
        specs_and_models=("4K OLED 65 inch", "iPhone 15 Pro", "Core i7 16GB", "شاحن سريع 65W"),
        specs_and_models_en=("4K OLED 65 inch display", "iPhone 15 Pro Max", "Intel Core i7 16GB RAM", "65W GaN fast charger"),
        packaging_types=("كراتين إلكترونيات", "طبالي شاشات بحماية فوم", "بوكسات أجهزة ذكية مقفلة"),
        packaging_types_en=("retail electronics cartons", "foam-cushioned TV pallets", "sealed device master boxes"),
        strict_inclusions=("أجهزة استهلاكية ذكية", "تلفزيونات وشاشات", "حواسيب واتصالات"),
        strict_exclusions=("أجهزة تبريد ومكيفات منزلية", "مولدات كهرباء ضخمة", "لوحات صناعية PLC"),
        disambiguation_anchors=("إلكترونيات", "شاشة تلفزيون", "جوال", "لابتوب", "سمارت", "كاميرات مراقبة", "راوتر", "electronics", "smart tv", "laptop", "smartphone", "cctv"),
    ),
    133: CategorySpec(
        root_id=133,
        name_ar="الأثاث",
        name_en="Furniture",
        domains=("عفش منزلي", "مفروشات", "أثاث مكتبي", "مجالس وغرف نوم", "طاولات ومطابخ"),
        core_nouns=(
            "غرف نوم خشب كينج وسنجل", "أطقم كنب مجالس أمريكي ومغربي", "طاولات طعام مع كراسي",
            "دواليب ملابس خشبية 6 أبواب", "مكاتب وكراسي دوارة جلد", "مراتب سرير طبية سبرينج",
            "طاولات شاي وخدمة", "خزائن أحذية ومداخل", "مطابخ ألمنيوم وخشب مركبة",
            "ستائر وسجاد موكيت مجالس", "جلسات خارجية حدائق", "مكتبات أرفف كتب خشبية",
            "سرير أطفال دورين", "بوفيه غرفة طعام", "كنب زاوية ركنية L"
        ),
        core_nouns_en=(
            "king and single wooden bedroom sets", "American and Moroccan living room sofa sets", "dining tables with chairs",
            "6-door wooden wardrobe closets", "executive leather office desks and swivel chairs", "orthopedic spring bed mattresses",
            "coffee and tea side tables", "shoe storage cabinets and entryway consoles", "modular aluminum and wood kitchen cabinets",
            "window curtains and living room carpets rugs", "outdoor garden patio seating sets", "wooden bookshelf racks",
            "bunk beds for kids", "dining room buffet credenza", "L-shaped sectional corner sofas"
        ),
        brands=("ايكيا", "هوم سنتر", "ميداس", "العامر للأثاث", "سليب هاي مراتب", "مطلبي للأثاث"),
        brands_en=("IKEA", "Home Centre", "Midas Furniture", "Al Amer Furniture", "Sleep High Mattresses", "Al Motlaq"),
        specs_and_models=("مقاس 200*200 سم", "كنب 7 أشخاص L-Shape", "طاولة 8 كراسي رخام"),
        specs_and_models_en=("200x200cm king size", "7-seater L-shaped sofa", "8-seater marble dining table set"),
        packaging_types=("عفش مغلف بلاستيك فقاعات", "كراتين أثاث مسطحة", "أطقم كنب ملفوفة بنايلون", "حمولة دينا عفش"),
        packaging_types_en=("bubble-wrapped furniture load", "flat-pack furniture boxes", "shrink-wrapped sofa bundles", "furniture moving truckload"),
        strict_inclusions=("أثاث منزلي ومكتبي", "مراتب ومفروشات", "مجالس وطاولات"),
        strict_exclusions=("مواد بناء خام وخشب بليود", "أجهزة كهربائية وإلكترونيات"),
        disambiguation_anchors=("أثاث", "عفش", "كنب", "غرفة نوم", "طاولة طعام", "دولاب", "مرتبة سرير", "مجلس", "furniture", "sofa", "bedroom set", "dining table", "mattress"),
    ),
    136: CategorySpec(
        root_id=136,
        name_ar="المواد الكيميائية",
        name_en="Chemicals materials",
        domains=("كيماويات صناعية", "مذيبات", "أحماض وقواعد", "بوليمرات ومواد معالجة"),
        core_nouns=(
            "هيدروكسيد الصوديوم صودا كاوية", "حمض الهيدروكلوريك تينر كيميائي", "كحول إيثيلي نقي 99%",
            "مذيبات عضوية كيميائية", "بوليمرات خام ومثبتات", "مادة راتنجات إيبوكسي",
            "أمونيا سائلة وأحماض كبريتية", "كلور سائل ومطهرات كيميائية مركزة", "صمغ كيميائي وبوليمر",
            "مبيدات آفات كيميائية مركزة", "بودرة سيليكا كيميائية", "مواد معالجة مياه كيميائية"
        ),
        core_nouns_en=(
            "sodium hydroxide caustic soda flakes", "hydrochloric acid chemical thinner", "pure 99% ethyl alcohol ethanol",
            "industrial organic chemical solvents", "raw polymer resins and stabilizers", "liquid epoxy resin and hardener",
            "liquid ammonia and sulfuric acid", "concentrated liquid chlorine sanitizer", "chemical adhesives and bonding polymer",
            "concentrated technical grade pesticides", "chemical grade precipitated silica", "water treatment chemicals flocculants"
        ),
        brands=("سابك للبتروكيماويات", "الشركة السعودية للكيماويات", "باسف BASF", "داو كيميكال"),
        brands_en=("SABIC Petrochemicals", "Saudi Chemical Co", "BASF", "Dow Chemical"),
        specs_and_models=("نقاء 99.5%", "أكياس رقائق 25 كجم", "براميل بلاستيك HDPE أزرق", "IBC 1000L"),
        specs_and_models_en=("99.5% purity grade", "25kg flake bags", "blue HDPE chemical drums", "1000L IBC chemical tote"),
        packaging_types=("براميل كيميائية زرقاء", "خزانات IBC بمحبس أمان", "أكياس رقائق كيميائية"),
        packaging_types_en=("blue chemical barrels", "IBC totes with safety valves", "25kg chemical sacks"),
        strict_inclusions=("مواد كيميائية خام ومركزة", "أحماض ومذيبات", "بتروكيماويات أولية"),
        strict_exclusions=("منظفات تجارية جاهزة للاستخدام", "أدوية ومستحضرات بشرية"),
        disambiguation_anchors=("كيميائي", "أحماض", "صودا كاوية", "مذيبات", "إيبوكسي", "بوليمر", "chemical", "caustic soda", "acid", "solvent", "epoxy resin"),
    ),
    140: CategorySpec(
        root_id=140,
        name_ar="البيوت الجاهزة",
        name_en="Prefabricated Houses",
        domains=("بركسات", "كرفانات", "ساندوتش بانل", "غرف جاهزة ومتحركة", "كبائن حراسة"),
        core_nouns=(
            "بركسات سكن عمال", "كرفانات متنقلة سحب وشاحنات", "غرف ساندوتش بانل معزولة",
            "كبائن حراسة فيبر جلاس جاهزة", "مكاتب موقع متنقلة جاهزة", "دورات مياه جاهزة بركسات",
            "شاليهات وملاحق حديد جاهزة للتركيب", "غرف حارس مجهزة بمكيف وشباك"
        ),
        core_nouns_en=(
            "prefabricated labor camp porta cabins", "mobile caravan trailers", "insulated sandwich panel portable cabins",
            "fiberglass security guard booths", "portable mobile site offices", "prefabricated modular toilet blocks",
            "prefabricated modular chalets and outhouses", "furnished security guard room with AC"
        ),
        brands=("الزامل للحديد والمباني الجاهزة", "الرشيد للمباني الجاهزة", "الراجحي كرفانات"),
        brands_en=("Zamil Prefab Buildings", "Al-Rasheed Prefab Porta Cabins", "Al-Rajhi Caravans"),
        specs_and_models=("مقاس 3*6 متر", "مقاس 3.75*12 متر", "ساندوتش بانل 5 سم", "شاسيه حديد ثقيل"),
        specs_and_models_en=("3x6m dimensions", "3.75x12m heavy porta cabin", "50mm insulated sandwich panel", "heavy duty steel chassis"),
        packaging_types=("حمولة لوبد مفردة", "تريلا تيدر منخفض", "سحب كرفان"),
        packaging_types_en=("lowbed heavy haul", "flatbed trailer cabin haul", "towable caravan transport"),
        strict_inclusions=("غرف ومباني وكرفانات وكبائن جاهزة منقولة بالكامل"),
        strict_exclusions=("مواد بناء مفرقة كالإسمنت والبلك", "خزانات مياه فقط"),
        disambiguation_anchors=("بركس", "كرفان", "بيوت جاهزة", "ساندوتش بانل", "كابينة حراسة", "غرفة جاهزة", "porta cabin", "prefab house", "sandwich panel cabin", "caravan"),
    ),
    141: CategorySpec(
        root_id=141,
        name_ar="النفايات",
        name_en="Waste material",
        domains=("نفايات بلدية", "مخلفات هدم ونظافة", "نفايات صلبة وتدوير"),
        core_nouns=(
            "نفايات صلبة مجمعة", "نفايات بلدية كبس", "نفايات هدم مباني وردم",
            "نفايات كرتون وبلاستيك للتدوير", "حاويات نفايات تجارية ممتلئة",
            "نفايات صناعية غير خطرة", "نفايات حدائق وأشجار مقلمة", "نفايات أوراق مكاتب للإتلاف"
        ),
        core_nouns_en=(
            "compacted municipal solid waste", "compressed municipal trash", "demolition rubble and debris waste",
            "waste cardboard and plastic for recycling", "full commercial waste dumpster containers",
            "non-hazardous industrial waste debris", "green garden pruning foliage waste", "confidential office document shredding waste"
        ),
        brands=("شركة إدامة للتدوير", "سرك للاستثمار البيئي SIRC", "بلدية النظافة"),
        brands_en=("Edama Recycling", "Saudi Investment Recycling Co SIRC", "Municipality Cleanliness"),
        specs_and_models=("حمولة ضاغطة نفايات", "حاوية 20 ياردة", "حاوية 12 ياردة"),
        specs_and_models_en=("garbage compactor truckload", "20-yard skip container", "12-yard roll-off bin"),
        packaging_types=("سيارة ضاغطة نفايات", "حاوية نفايات مسحوبة", "أكياس نفايات كبرى جامبو"),
        packaging_types_en=("waste compactor vehicle", "roll-off waste skip container", "heavy jumbo waste trash bags"),
        strict_inclusions=("نفايات بلدية وتجارية وردم غير معالج"),
        strict_exclusions=("سكراب معادن ذو قيمة عالية للبيع", "أجهزة سليمة"),
        disambiguation_anchors=("نفايات", "ردم نفايات", "ضاغطة نفايات", "تدوير نفايات", "حاوية نظافة", "waste material", "trash", "rubble waste", "garbage compactor"),
    ),
    147: CategorySpec(
        root_id=147,
        name_ar="الملابس والأحذية",
        name_en="Clothes and Shoes",
        domains=("ملابس جاهزة", "أثواب", "عبايات", "أحذية وشرابات", "ملابس أطفال ورياضة"),
        core_nouns=(
            "أثواب رجالية جاهزة", "عبايات وطرح نسائية مطرزة", "أشمغة وغتر حمراء وبيضاء",
            "أحذية رياضية وجلدية", "صنادل وشباشب رجالية ونسائية", "فساتين وبلايز نسائية",
            "تيشرتات وبناطيل جينز", "ملابس أطفال ومواليد قطنية", "بجامات وملابس نوم",
            "أطقم رياضية وبدل تدريب", "شرابات وأوشحة وقفازات صوف", "ملابس موحدة يونيفورم عمال"
        ),
        core_nouns_en=(
            "ready-to-wear men thobes", "embroidered women abayas and scarves", "red and white Shemagh headscarves",
            "athletic sports shoes and leather shoes", "men and women sandals slippers", "women dresses and blouses",
            "cotton t-shirts and denim jeans", "baby and children cotton clothing", "pajamas and nightwear sets",
            "sports tracksuits and athletic apparel", "socks, scarves and winter wool gloves", "commercial worker uniforms"
        ),
        brands=("الدفة أثواب", "الأصيل ثياب", "شماغ البسام", "شماغ جيفنشي", "نايكي أحذية", "أديداس", "سكتشرز", "رد تاغ", "سنتربوينت"),
        brands_en=("Al Daffah Thobes", "Al Aseel Thobes", "Al Bassam Shemagh", "Givenchy Shemagh", "Nike Footwear", "Adidas", "Skechers", "Red Tag", "Centrepoint"),
        specs_and_models=("مقاسات 52 إلى 62", "مقاسات أحذية 40-45", "قطن 100%", "كرتون 50 ثوب"),
        specs_and_models_en=("thobe sizes 52 to 62", "shoe sizes EU 40-45", "100% combed cotton", "carton of 50 thobes"),
        packaging_types=("كراتين ملابس معلقة ومطبقة", "شوالات ملابس بالات", "بوكسات أحذية مجمعة"),
        packaging_types_en=("hanger and folded apparel cartons", "compressed apparel bales", "master shoe boxes"),
        strict_inclusions=("ملابس وأزياء جاهزة", "أحذية وصنادل", "أشمغة وعبايات"),
        strict_exclusions=("أقمشة خام ورولات خياطة", "أثاث ومفروشات منزلية"),
        disambiguation_anchors=("ملابس", "ثياب", "أثواب", "أحذية", "عبايات", "أشمغة", "فساتين", "تيشرتات", "clothes", "apparel", "thobe", "shoes", "abaya", "shemagh"),
    ),
    148: CategorySpec(
        root_id=148,
        name_ar="الفحم والحطب",
        name_en="Charcoal and Firewood",
        domains=("حطب تدفئة وطبخ", "فحم شواء", "فحم شيشة ونباتي"),
        core_nouns=(
            "حطب سمر مستورد ناشف", "حطب قرض للتدفئة", "حطب أرطى مجفف",
            "فحم نباتي للشواء كراتين", "فحم وادي حلفا سوداني", "فحم مضغوط قوالب سداسي",
            "فحم شيشة كوكو طبيعي", "حطب زيتون للطبخ والمطاعم", "أكياس فحم شواء سريع الاشتعال",
            "حطب مقطع ومشذب بالربطة"
        ),
        core_nouns_en=(
            "dried Samar firewood logs", "Qarad firewood for heating", "dry Arta firewood bundles",
            "natural barbecue lump charcoal", "Wadi Halfa natural charcoal", "hexagonal extruded briquette charcoal",
            "natural coconut shell hookah charcoal", "olive wood logs for cooking", "quick-light barbecue charcoal bags",
            "split seasoned firewood bundles"
        ),
        brands=("فحم الشعلة", "فحم كوكو نارا", "حطب السمر الأفريقي المستورد", "فحم الشرقية"),
        brands_en=("Al-Shoala Charcoal", "Coco Nara Hookah Charcoal", "African Samar Firewood", "Al Sharqiya Briquettes"),
        specs_and_models=("خياش 10 كجم", "أكياس 5 كجم", "ربطات حطب 15 كجم", "خالي من الدخان والشرار"),
        specs_and_models_en=("10kg burlap sacks", "5kg retail bags", "15kg firewood bundles", "smokeless and sparkless grade"),
        packaging_types=("خياش حطب مربوطة", "كراتين فحم مضغوط", "طبالي شوالات فحم", "حمولة دينا حطب"),
        packaging_types_en=("tied firewood jute sacks", "boxed charcoal briquette cartons", "charcoal sack pallets", "firewood truckload"),
        strict_inclusions=("حطب الوقود والشواء", "فحم نباتي ومضغوط"),
        strict_exclusions=("فحم بترولي وصناعي للمصانع", "أثاث وأخشاب بناء"),
        disambiguation_anchors=("حطب", "فحم", "سمر", "شواء", "شيشة فحم", "قرض", "وادي حلفا", "firewood", "charcoal", "bbq briquette", "samar firewood"),
    ),
    149: CategorySpec(
        root_id=149,
        name_ar="الأدوية",
        name_en="Medicines",
        domains=("صيدليات", "مستحضرات علاجية بشرية", "أدوية مبردة ومحاقن"),
        core_nouns=(
            "مسكنات بنادول وفيفادول", "مضادات حيوية كبسولات وشراب", "أدوية ضغط وسكر وأنسولين",
            "فيتامينات ومكملات غذائية صيدلانية", "محاليل وريدية ومغذيات جلوكوز",
            "مراهم وكريمات علاجية", "قطرات عيون وأذن طبية", "بخاخات ربو وحساسية",
            "لقاحات وتحصينات بشرية مبردة", "كبسولات أوميبرازول للمعدة"
        ),
        core_nouns_en=(
            "Panadol and Fevadol analgesics", "antibiotic capsules and oral suspension", "hypertension, diabetes and insulin medications",
            "pharmaceutical multivitamins and dietary supplements", "intravenous IV glucose infusion solutions",
            "topical therapeutic medical ointments", "sterile eye and ear drops", "asthma and allergy inhalers",
            "cold chain human vaccines", "omeprazole gastro-resistant capsules"
        ),
        brands=("سبيماكو الدوائية SPIMACO", "فايزر", "نوفارتس", "جلاكسو سميث كلاين GSK", "جمجوم فارما", "تبوك الدوائية"),
        brands_en=("SPIMACO", "Pfizer", "Novartis", "GlaxoSmithKline GSK", "Jamjoom Pharma", "Tabuk Pharmaceuticals"),
        specs_and_models=("علب 500 مجم", "حفظ في حرارة 2-8 مئوية", "أمبولات 5 مل", "كراتين مبردة ثلاجة"),
        specs_and_models_en=("500mg tablets box", "store at 2-8 C cold chain", "5ml sterile ampoules", "temperature-monitored refrigerated boxes"),
        packaging_types=("كراتين أدوية مبردة", "طبالي صيدليات مقفلة", "صناديق حفظ حراري إيس بوكس"),
        packaging_types_en=("cold-chain pharmaceutical shippers", "sealed pharmacy pallets", "insulated ice box containers"),
        strict_inclusions=("أدوية علاجية ومستحضرات بشرية صيدلانية"),
        strict_exclusions=("أدوية بيطرية للحيوانات", "مستلزمات وأجهزة طبية كمامات وأسرة", "عطور ومكياج"),
        disambiguation_anchors=("أدوية", "علاج صيدلية", "بنادول", "أنسولين", "كبسولات علاج", "مضاد حيوي", "medicine", "pharmaceutical", "panadol", "antibiotic", "insulin"),
    ),
    153: CategorySpec(
        root_id=153,
        name_ar="الأدوية البيطرية",
        name_en="Veterinary medicines",
        domains=("عيادات بيطرية", "علاجات مواشي وإبل", "لقاحات بيطرية"),
        core_nouns=(
            "مضادات حيوية بيطرية للحقن أوكسي تتراسيكلين", "فيتامينات ومعادن مواشي وإبل هـ سيلينيوم",
            "تحاميل وبخاخات جروح بيطرية أزرق", "لقاحات طاعون وجدري الأغنام", "علاجات ديدان وطفيليات بيطرية إيفوميك",
            "مقويات ومكملات غذائية للخيل والهجن", "مطهرات ومبيدات حشرات الحظائر البيطرية"
        ),
        core_nouns_en=(
            "injectable oxytetracycline veterinary antibiotics", "vitamin E and selenium for camels and livestock",
            "veterinary blue antiseptic wound spray", "sheep pox and pestes des petits ruminants vaccines", "Ivomec antiparasitic dewormer for cattle and camels",
            "performance tonics and supplements for racing camels and horses", "veterinary barn insecticides and disinfectants"
        ),
        brands=("أفيكو للأدوية البيطرية", "فايتوفارم بيطري", "سيفا سانتي بيطري", "شركة الرياض للبيطرة"),
        brands_en=("AVICO Vet", "Phytopharm Veterinary", "Ceva Sante Animale", "Riyadh Pharma Vet"),
        specs_and_models=("قوارير 100 مل للحقن", "جوالين 5 لتر شراب مواشي", "حقن تحت الجلد إيفوميك سوبر"),
        specs_and_models_en=("100ml injectable vial", "5L livestock drench gallon", "subcutaneous Ivomec Super injection"),
        packaging_types=("كراتين قوارير بيطرية", "صناديق لقاحات مبردة لمزارع المواشي", "جوالين محاليل بيطرية"),
        packaging_types_en=("boxed veterinary vials", "insulated livestock vaccine cold packs", "5L solution jerrycans"),
        strict_inclusions=("أدوية ولقاحات ومكملات علاج الحيوانات والمواشي"),
        strict_exclusions=("أدوية بشرية", "أعلاف ومواشي حية"),
        disambiguation_anchors=("بيطري", "مواشي علاج", "إبل علاج", "إيفوميك", "حقن أغنام", "أدوية بيطرية", "veterinary", "animal medicine", "ivomec", "livestock vaccine"),
    ),
    154: CategorySpec(
        root_id=154,
        name_ar="الدراجات الهوائية",
        name_en="Bicycles",
        domains=("سياكل", "دراجات جبلية وسباق", "إكسسوارات وقطع سياكل"),
        core_nouns=(
            "دراجات هوائية جبلية للكبار مقاس 26 و 29", "سياكل أطفال مقاس 12 و 16 كفرات جانبية",
            "دراجات طريق وهجين رود بايك", "خوذ وقفازات حماية للدراجين",
            "قطع غيار سياكل كفرات وجنازير وبدالات", "دراجات هوائية رياضية ترينكس وتريك",
            "حوامل سياكل للسيارات ومنافيخ كفرات هوائية"
        ),
        core_nouns_en=(
            "adult mountain bikes 26 and 29 inch", "kids bicycles with training wheels 12 and 16 inch",
            "road racing and hybrid commuter bicycles", "cycling safety helmets and protective gloves",
            "bicycle spare parts tires, chains and pedals", "Trinx and Trek sports bicycles",
            "car rear bicycle racks and floor tire pumps"
        ),
        brands=("تريك Trek", "جاينت Giant", "ترينكس Trinx", "كوماكس", "فونيكس سياكل"),
        brands_en=("Trek Bicycles", "Giant Bicycles", "Trinx Bikes", "Co-Max Bikes", "Phoenix Bicycles"),
        specs_and_models=("مقاس 27.5 بوصة ألمنيوم", "سرعات شيمانو 21 سرعة", "كرتون دراجة مفككة جديدة"),
        specs_and_models_en=("27.5 inch aluminum frame", "Shimano 21-speed gear system", "85% assembled new bike box"),
        packaging_types=("كراتين دراجات هوائية من المصنع", "طبالي سياكل كراتين", "سياكل مجمعة مربوطة"),
        packaging_types_en=("factory bicycle shipping cartons", "palletized bicycle boxes", "assembled strapped bicycles"),
        strict_inclusions=("دراجات هوائية وسياكل وإكسسواراتها المباشرة"),
        strict_exclusions=("دراجات نارية ودبابات محركات", "ألعاب أطفال بلاستيكية صغيرة"),
        disambiguation_anchors=("سيكل", "دراجة هوائية", "سياكل", "رود بايك", "ماونتن بايك", "bicycle", "bike", "mountain bike", "cycling"),
    ),
    155: CategorySpec(
        root_id=155,
        name_ar="الدراجات النارية",
        name_en="Motorbikes",
        domains=("دبابات", "دراجات نارية توصيل", "سكوترات كهربائية", "دبابات بر كواد"),
        core_nouns=(
            "دراجات نارية توصيل طلبات مطاعم", "دبابات أربع كفرات صحراوية كواد",
            "دبابات ريس وسرعة سوزوكي وهوندا", "سكوترات كهربائية ذكية للكبار",
            "دبابات بر وسفاري ياماها رابتر", "دراجات نارية كروزر وهارلي",
            "قطع غيار دبابات وجنازير وخوذ دبابات ريس"
        ),
        core_nouns_en=(
            "food delivery courier motorcycles", "all-terrain 4x4 quad ATVs",
            "Suzuki and Honda sport racing superbikes", "adult electric smart scooters",
            "Yamaha Raptor sand dune quad bikes", "Harley-Davidson cruiser motorbikes",
            "motorcycle spare drive chains and full-face racing helmets"
        ),
        brands=("سوزوكي دبابات", "هوندا دراجات نارية", "ياماها", "هارلي ديفيدسون", "كوازاكي", "سيم SYM"),
        brands_en=("Suzuki Motorcycles", "Honda Motorbikes", "Yamaha Powersports", "Harley-Davidson", "Kawasaki", "SYM Scooters"),
        specs_and_models=("سعة 150 سي سي", "سعة 700 سي سي رابتر", "سكوتر 48 فولت 500 واط"),
        specs_and_models_en=("150cc delivery engine", "700cc Raptor engine", "48V 500W electric scooter"),
        packaging_types=("صناديق خشبية للدبابات", "دبابات مربوطة على سطحة أو دينا", "كراتين سكوترات كهربائية"),
        packaging_types_en=("steel-framed motorbike wooden crates", "tied down motorcycles on flatbed", "e-scooter master boxes"),
        strict_inclusions=("دبابات ودراجات نارية وسكوترات بمحرك"),
        strict_exclusions=("دراجات هوائية سياكل بدون محرك", "سيارات وشاحنات"),
        disambiguation_anchors=("دباب", "دراجة نارية", "سكوتر كهربائي", "سوزوكي دباب", "كواد", "رابتر", "motorbike", "motorcycle", "quad bike", "electric scooter", "atv"),
    ),
    156: CategorySpec(
        root_id=156,
        name_ar="المستلزمات الطبية و مستلزمات المستشفيات",
        name_en="Medical supplies and hospital supplies",
        domains=("تجهيزات طبية", "مستهلكات مستشفيات", "أجهزة قياس صحية", "أسرة وكراسي طبية"),
        core_nouns=(
            "كمامات طبية وقائية جراحية كراتين", "قفازات لاتكس ونيتريل فحص معقمة",
            "شاش وشاش معقم ولاصق جروح طبي", "كراسي متحركة للمرضى وكبار السن",
            "أسرة مستشفيات كهربائية وهيدروليكية", "أجهزة قياس السكر والضغط والحرارة عن بعد",
            "سرنجات وحقن طبية ومشارط معقمة", "أنابيب قساطر طبية وأكياس جمع البول",
            "أجهزة تنفس وأسطوانات أكسجين للمرضى", "معقمات أيدي وأسطح جراحية للمستشفيات"
        ),
        core_nouns_en=(
            "surgical 3-ply medical face masks", "sterile nitrile and latex examination gloves",
            "sterile medical gauze and surgical tape", "patient and elderly wheelchairs",
            "electric adjustable hospital ICU beds", "digital blood pressure monitors and glucometers",
            "sterile disposable hypodermic syringes and scalpels", "medical urinary catheters and drainage bags",
            "oxygen concentrators and medical oxygen therapy cylinders", "hospital grade surgical surface disinfectants"
        ),
        brands=("أومرون Omron", "3M ميديكال", "بيدرايت كراسي", "شركة الصناعات الطبية ميديكا", "بي براون B. Braun"),
        brands_en=("Omron Healthcare", "3M Health Care", "Pedrite Wheelchairs", "Saudi Medical Medica", "B. Braun Medical"),
        specs_and_models=("كرتون 50 علبة كمامات", "كراسي كفرات مقاس 18 بوصة", "سرنجات 5 مل معقمة"),
        specs_and_models_en=("carton of 50 boxes 2500 masks", "18 inch width wheelchair", "5ml sterile luer lock syringes"),
        packaging_types=("كراتين مستلزمات طبية", "طبالي شاش وقفازات", "صناديق كراسي وأسرة طبية"),
        packaging_types_en=("medical supply master cartons", "glove and gauze pallets", "heavy hospital bed crates"),
        strict_inclusions=("مستهلكات وأجهزة ومعدات المستشفيات والعيادات"),
        strict_exclusions=("أدوية علاجية كبسولات وشراب", "منظفات منزلية عادية"),
        disambiguation_anchors=("طبي", "مستلزمات مستشفيات", "كمامات طبية", "كرسي متحرك", "قفازات لاتكس", "شاش معقم", "medical supplies", "hospital equipment", "face masks", "wheelchair", "sterile gloves"),
    ),
    157: CategorySpec(
        root_id=157,
        name_ar="الكتب",
        name_en="Books",
        domains=("مطبوعات", "مصاحف", "مناهج وكتب مدرسية", "روايات ومراجع"),
        core_nouns=(
            "مصاحف شريفة طباعة مجمع الملك فهد", "كتب ومناهج دراسية وزارة التعليم",
            "روايات وكتب أدبية وثقافية", "مراجع وكتب جامعية وأكاديمية",
            "كتب وقصص أطفال مصورة تعليمية", "مجلات وكتالوجات مطبوعة ومجلدات",
            "معاجم وقواميس وكتب فقهية وتاريخية", "دفاتر وكراسات مدرسية كراتين"
        ),
        core_nouns_en=(
            "Holy Quran Medina printing press edition", "Ministry of Education school curriculum textbooks",
            "fiction novels and literary cultural books", "university academic reference textbooks",
            "illustrated children educational storybooks", "printed magazines and bound reference catalogues",
            "Arabic dictionaries and Islamic jurisprudence history encyclopedias", "ruled school notebooks cartons"
        ),
        brands=("مكتبة جرير كتب", "مكتبة العبيكان", "مجمع الملك فهد لطباعة المصحف", "دار الشروق", "مكتبة الرشد"),
        brands_en=("Jarir Bookstore", "Obeikan Bookshop", "King Fahd Quran Printing Complex", "Dar El Shorouk", "Al Rushd Library"),
        specs_and_models=("كراتين 30 مصحف", "كراتين 50 كتاب مدرسي", "مجلدات فاخرة ورق شاموا"),
        specs_and_models_en=("carton of 30 Quran copies", "carton of 50 school textbooks", "hardcover chamois paper editions"),
        packaging_types=("كراتين كتب محكمة الرباط", "طبالي كراتين مناهج ومصاحف", "رزم كتب مغلفة بنايلون حراري"),
        packaging_types_en=("strapped book master cartons", "curriculum and Quran pallets", "shrink-wrapped book bundles"),
        strict_inclusions=("كتب ومصاحف ومطبوعات ورقية ومناهج"),
        strict_exclusions=("كرتون فارغ ومخلفات ورق للتدوير", "أجهزة إلكترونية لوحية كيندل"),
        disambiguation_anchors=("كتب", "مصحف", "مصاحف", "منهاج مدرسي", "رواية", "مطبوعات كتب", "مجلدات", "books", "quran", "textbook", "novel", "printed publications"),
    ),
    159: CategorySpec(
        root_id=159,
        name_ar="مولدات الكهرباء",
        name_en="Electricity Generators",
        domains=("طاقة ومولدات", "ماطور ديزل", "مولدات كاتم صوت", "محولات طاقة"),
        core_nouns=(
            "مولدات كهرباء ديزل كاتمة للصوت", "ماطور كهرباء بنزين صغير للرحلات والمخيمات",
            "مولدات طاقة كمنز وبيركنز صناعية للمشاريع", "محولات وموزعات جهد كهربائي للمولدات",
            "مولدات كهربائية قدرة 100 كيلو واط إلى 500 KVA", "لوحات نقل التيار الأوتوماتيكي ATS للمولدات",
            "دينمو توليد طاقة كهروميكانيكية احتياطية"
        ),
        core_nouns_en=(
            "soundproof silent diesel power generators", "portable gasoline power generator for camping",
            "Cummins and Perkins heavy industrial diesel generators", "generator voltage transformers and distribution panels",
            "100 kW to 500 KVA prime power generator sets", "automatic transfer switch ATS panels for generators",
            "backup industrial electrical alternator dynamos"
        ),
        brands=("كمنز Cummins", "بيركنز Perkins", "كاتربيلر CAT مولدات", "هوندا مواطير", "ميكالتي Denyo"),
        brands_en=("Cummins Power", "Perkins Engines", "Caterpillar CAT Generators", "Honda Generators", "Denyo Silent Generators"),
        specs_and_models=("قدرة 50 KVA", "قدرة 100 KVA كمنز", "ماطور 5 كيلو واط كاتم", "3 فاز 380V"),
        specs_and_models_en=("50 KVA prime power", "100 KVA Cummins silent canopy", "5 kW quiet portable generator", "3-phase 380V output"),
        packaging_types=("قواعد حديدية محملة بونش", "مولدات مجهزة على عجلات سحب", "شحنة لوبد مولدات ثقيلة"),
        packaging_types_en=("heavy skid-mounted canopy", "trailer-mounted mobile generator", "lowbed heavy generator haul"),
        strict_inclusions=("مولدات ومواطير الطاقة الكهربائية وملحقاتها المباشرة"),
        strict_exclusions=("أجهزة كهربائية وإلكترونيات استهلاكية", "بطاريات صغيرة جافة"),
        disambiguation_anchors=("مولد كهرباء", "ماطور كهرباء", "ديزل كمنز", "KVA", "بيركنز توليد", "generator", "diesel generator", "power generator", "silent genset"),
    ),
    160: CategorySpec(
        root_id=160,
        name_ar="مواد النسيج والخياطة",
        name_en="Textile and sewing materials",
        domains=("أقمشة خام", "رولات قماش", "مستلزمات خياطة", "خيوط وسحابات"),
        core_nouns=(
            "رولات طاقات أقمشة رجالية ونسائية", "طاقات قماش قطن وياباني وكوري",
            "بكرات خيوط خياطة كراتين ألوان متنوعة", "سحابات وأزرار وكلف خياطة للمشاغل",
            "ماكينات خياطة وتطريز صناعية جوكي وسنجر", "حشوات أكتاف وياقات تفصيل ثياب",
            "أقمشة تفصيل ستائر ومفروشات طاقات", "مطاط ومقصات خياطة احترافية كراتين"
        ),
        core_nouns_en=(
            "textile fabric bolts for thobes and dresses", "Japanese and Korean cotton fabric bolts",
            "assorted sewing thread spool cartons", "zippers, buttons and tailor notions",
            "Juki and Singer industrial sewing and embroidery machines", "shoulder pads and collar interlinings for tailoring",
            "upholstery and curtain drapery fabric rolls", "elastic bands and tailor shears cartons"
        ),
        brands=("أقمشة الجديعي", "أقمشة ريتشي", "ماكينات جوكي Juki", "سنجر Singer", "خيوط الكوتش"),
        brands_en=("Al-Jedaie Fabrics", "Richy Fabrics", "Juki Industrial Sewing", "Singer Sewing", "Coats Thread"),
        specs_and_models=("طاقة قماش 25 ياردة", "كرتون 100 بكرة خيط", "ماكينة درزة خياطة 220V"),
        specs_and_models_en=("25 yard fabric bolt", "carton of 100 thread spools", "220V industrial lockstitch machine"),
        packaging_types=("طاقات أقمشة ملفوفة برول بلاستيك", "كراتين خيوط وسحابات", "طبالي رولات أقمشة"),
        packaging_types_en=("plastic-wrapped fabric bolts", "tailoring notions master cartons", "textile fabric pallets"),
        strict_inclusions=("أقمشة خام وطاقات ومستلزمات خياطة ومشاغل"),
        strict_exclusions=("ملابس وأثواب جاهزة ومخيطة", "سجاد وموكيت مفروشات كاملة"),
        disambiguation_anchors=("طاقة قماش", "رول قماش", "خيوط خياطة", "مكينة خياطة", "أقمشة تفصيل", "سحابات وكلف", "textile", "fabric bolt", "sewing machine", "sewing thread"),
    ),
    161: CategorySpec(
        root_id=161,
        name_ar="منتجات التبغ",
        name_en="Tobacco Products",
        domains=("سجائر", "معسل وشيشة", "فيب وتبغ إلكتروني"),
        core_nouns=(
            "كراتين سجائر باكيتات متنوعة مارلبورو ودافيدوف", "معسل تفاحتين ونكهات فاخر وشيشة",
            "أجهزة شيشة إلكترونية وسحبات فيب جاهزة", "نكهات سائل فيب إلكتروني سولت نيكوتين",
            "تبغ سجائر للف وفلاتر وأوراق لف كراتين", "شيش ونراجيل زجاجية وخراطيم شيشة",
            "معسل عنب وتوت كراتين علب صفيح"
        ),
        core_nouns_en=(
            "Marlboro and Davidoff cigarette cartons", "Al Fakher double apple shisha molasses",
            "disposable electronic vape pod devices", "nicotine salt vape e-liquid bottles",
            "rolling tobacco pouches, filters and rolling papers", "traditional glass waterpipes and shisha hoses",
            "grape and berry flavored molasses tins"
        ),
        brands=("مارلبورو Marlboro", "الفاخر معسل Al Fakher", "دافيدوف", "مزاج فيب Mazaj", "نكهات نكست"),
        brands_en=("Marlboro", "Al Fakher Tobacco", "Davidoff", "Mazaj Vape", "Nasty Juice"),
        specs_and_models=("كرتون 50 كروز سجائر", "جردل معسل 1 كجم", "سحبة 5000 موشة 50 مجم"),
        specs_and_models_en=("master case of 50 cartons", "1kg shisha molasses tub", "5000 puffs 50mg disposable pod"),
        packaging_types=("كراتين كروزات سجائر", "كراتين معسل محكمة الإغلاق", "بوكسات نكهات وسحبات"),
        packaging_types_en=("cigarette master cases", "sealed shisha tubs master carton", "retail vape display boxes"),
        strict_inclusions=("سجائر ومعسل وفيب وتبغ وملحقاتها"),
        strict_exclusions=("فحم شواء وحطب", "مواد غذائية وحلويات عادية"),
        disambiguation_anchors=("سجائر", "دخان", "معسل", "فيب", "سحبة إلكترونية", "الفاخر معسل", "tobacco", "cigarettes", "shisha", "vape", "molasses"),
    ),
    162: CategorySpec(
        root_id=162,
        name_ar="مخلفات",
        name_en="Remnants",
        domains=("سكراب", "خردة معادن", "بقايا تصنيع وهياكل تالفة"),
        core_nouns=(
            "سكراب حديد تسليح وهياكل معدنية مقصوصة", "سكراب نحاس أسلاك ومواسير تالفة",
            "خردة ألمنيوم وشبابيك قديمة مجمعة للوزن", "سكراب شاحنات وسيارات تالفة كبس",
            "بقايا خشب طبالي مكسرة للتدوير", "خردة محركات ومكائن تالفة قديمة",
            "سكراب بطاريات سيارات تالفة رصاص", "قصاصات صاج حديد وبقايا ورش ومصانع"
        ),
        core_nouns_en=(
            "cut rebar steel and structural scrap metal", "scrap copper wire and damaged copper piping",
            "scrap aluminum frames and profiles for recycling", "crushed vehicle bodies and truck scrap",
            "broken wooden pallet scrap for recycling", "discarded non-working engine core scrap",
            "spent lead-acid automotive battery scrap", "industrial sheet metal punchings and offcuts"
        ),
        brands=("حراج السكراب", "مكابس الحديد الخردة", "شركة تدوير المعادن"),
        brands_en=("Scrap Yard Auction", "Metal Hydraulic Balers", "Saudi Metal Recycling Co"),
        specs_and_models=("حمولة تريلا سكراب 25 طن", "ربطات حديد خردة مكبوس", "وزن ميزان بيسكول"),
        specs_and_models_en=("25-ton scrap trailer haul", "compacted hydraulic metal bales", "weighbridge certified weight"),
        packaging_types=("تريلا جوانب مرتفعة سكراب", "صناديق حديدية للحديد الخردة", "حمولة قلاب خردة"),
        packaging_types_en=("high-side scrap trailer load", "scrap metal steel bins", "open tipper scrap transport"),
        strict_inclusions=("خردة معادن وسكراب ومخلفات صناعية ذات قيمة للتدوير"),
        strict_exclusions=("نفايات بلدية وعضوية وردم", "قطع غيار صالحة للاستخدام"),
        disambiguation_anchors=("سكراب", "خردة", "سكراب حديد", "نحاس سكراب", "حديد كبس خردة", "scrap", "scrap metal", "copper scrap", "steel scrap", "metal recycling"),
    ),
    163: CategorySpec(
        root_id=163,
        name_ar="مواد تنظيف",
        name_en="Cleaning materials",
        domains=("منظفات ومساحيق", "مطهرات", "مستلزمات نظافة منزلية وتجارية"),
        core_nouns=(
            "مسحوق غسيل ملابس كراتين تايد وإريال", "كلوركس مبيض ومطهر أسطح جالونات",
            "صابون غسيل صحون سائل فيري كراتين", "مطهر أرضيات ديتول وجينتو برائحة الصنوبر",
            "منظف حمامات فلاش ومزيل ترسبات كلسية", "ملمع زجاج ومرايا بخاخات",
            "مناديل ورقية رولات ومربعات كراتين فاين ونورس", "أكياس نفايات وسفر طعام رولات بلاستيك",
            "مماسح ومقشات وإسفنج جلي صحون كراتين"
        ),
        core_nouns_en=(
            "Tide and Ariel laundry detergent powder cartons", "Clorox liquid bleach and surface disinfectant gallons",
            "Fairy liquid dishwashing soap cartons", "Dettol and Gento pine scented floor cleaner",
            "Flash toilet bowl cleaner and limescale remover", "spray glass and mirror window cleaner",
            "Fine and Noor facial tissues and paper towel cartons", "plastic garbage trash bags and table cover rolls",
            "floor mops, brooms and dishwashing scouring sponges"
        ),
        brands=("تايد Tide", "إريال Ariel", "كلوركس Clorox", "فيري Fairy", "ديتول Dettol", "داك DAC", "فاين مناديل", "جينتو"),
        brands_en=("Tide Detergent", "Ariel Laundry", "Clorox Bleach", "Fairy Dishwashing", "Dettol Antiseptic", "DAC Disinfectant", "Fine Tissues", "Gento Clean"),
        specs_and_models=("كيس 10 كجم مسحوق", "كرتون 12 جالون 3.78 لتر", "شد مناديل 10 علب"),
        specs_and_models_en=("10kg detergent bag", "carton of 12x 3.78L gallons", "10-box tissue bundle pack"),
        packaging_types=("كراتين منظفات", "طبالي مساحيق غسيل", "شدات رولات مناديل وسفر"),
        packaging_types_en=("cleaning supply master cartons", "laundry powder wrapped pallets", "paper towel tissue bundles"),
        strict_inclusions=("مساحيق غسيل ومطهرات ومناديل ومستلزمات نظافة"),
        strict_exclusions=("مواد كيميائية أولية صناعية صودا كاوية خام", "عطور وبخور شخصي"),
        disambiguation_anchors=("تنظيف", "مسحوق غسيل", "صابون", "كلوركس", "فيري", "مطهر أسطح", "مناديل رول", "cleaning materials", "detergent", "bleach", "tissues", "disinfectant"),
    ),
    166: CategorySpec(
        root_id=166,
        name_ar="مياه معبأة",
        name_en="Bottled water",
        domains=("مياه شرب", "قوارير مياه", "كراتين مويا", "جوالين 5 جالون"),
        core_nouns=(
            "كراتين مياه شرب هنا 330 مل و 200 مل", "كراتين مياه صفا مكة 40 حبة",
            "كراتين مياه نوفا قوارير 550 مل و 1.5 لتر", "مياه نقى وأروى كراتين كاسات ومغلفة",
            "جوالين مياه 5 جالون مخصصة للبرادات", "كراتين مياه بيرين قوارير زجاجية وبلاستيك",
            "طبالي مياه شرب موزعة للمساجد والمنازل", "كراتين مياه هدا والعين قطرات نقية"
        ),
        core_nouns_en=(
            "Hana bottled drinking water cartons 330ml and 200ml", "Safa Makkah drinking water cartons 40-pack",
            "Nova bottled mineral water 550ml and 1.5L cartons", "Naqi and Arwa drinking water cup packs",
            "5-gallon bottled water dispenser bottles", "Berain premium glass and plastic bottled water cartons",
            "drinking water pallets for mosques and homes", "Hada and Al Ain pure drinking water cartons"
        ),
        brands=("مياه هنا", "مياه نوفا", "مياه صفا", "مياه بيرين Berain", "مياه نقى", "مياه أروى", "مياه تانيا"),
        brands_en=("Hana Water", "Nova Water", "Safa Water", "Berain Water", "Naqi Water", "Arwa Water", "Tania Water"),
        specs_and_models=("كرتون 40 قارورة 330 مل", "كرتون 48 كاس 250 مل", "جالون 18.9 لتر"),
        specs_and_models_en=("carton of 40x 330ml bottles", "carton of 48x 250ml cups", "5-gallon 18.9L cooler bottle"),
        packaging_types=("طبالي كراتين مياه شرب", "شحنة دينا مياه معبأة", "تريلا كاملة طبالي مويا"),
        packaging_types_en=("bottled water carton pallets", "water distribution truckload", "full semi-trailer water pallets"),
        strict_inclusions=("مياه شرب معبأة بقوارير أو كاسات أو جوالين جاهزة"),
        strict_exclusions=("وايتات صهاريج مياه غير معبأة", "عصائر ومشروبات غازية تموينية"),
        disambiguation_anchors=("مياه معبأة", "كراتين مياه", "مويا", "مياه هنا", "مياه نوفا", "مياه صفا", "مياه بيرين", "bottled water", "drinking water", "mineral water cartons", "water pallet"),
    ),
    167: CategorySpec(
        root_id=167,
        name_ar="حاويات",
        name_en="Medical Waste",
        domains=("كونتينرات", "حاويات شحن بحري", "خزانات وسائط IBC", "حاويات تفريغ"),
        core_nouns=(
            "حاوية شحن بحري 20 قدم جافة ونظيفة", "حاوية شحن 40 قدم هاي كيوب HC",
            "خزانات وسائط IBC سعة 1000 لتر بقفص حديدي", "حاويات تفريغ حديدية لمخلفات الهدم والبناء",
            "براميل شحن حديد سعة 200 لتر مغلقة بغطاء", "حاويات تخزين بضائع معزولة مقاومة للحرارة",
            "هياكل حاويات شحن معدلة كمستودعات متنقلة"
        ),
        core_nouns_en=(
            "20ft standard dry cargo shipping container", "40ft High Cube ISO shipping container",
            "1000L IBC intermediate bulk container with steel cage", "steel roll-off waste skip containers",
            "200L tight-head steel shipping drums", "insulated temperature-resistant cargo storage containers",
            "modified shipping container mobile storage units"
        ),
        brands=("ميرسك Maersk", "MSC كونتينرات", "حاويات شوتر للمخلفات", "تانك IBC جريف"),
        brands_en=("Maersk Container", "MSC Container Lines", "Schuetz Waste Skips", "Greif IBC Totes"),
        specs_and_models=("طول 20 قدم", "طول 40 قدم High Cube", "سعة 1000 لتر قفص حديد مجلفن"),
        specs_and_models_en=("20ft standard length", "40ft High Cube 9ft6in", "1000L galvanized cage IBC tote"),
        packaging_types=("شحنة تريلا تيدر حاوية", "رفع ونش كرين للحاوية", "طبالي خزانات IBC فارغة"),
        packaging_types_en=("container chassis trailer haul", "mobile crane container lift", "empty IBC tote pallet load"),
        strict_inclusions=("حاويات وكونتينرات الشحن والتخزين الفارغة وبراميل IBC"),
        strict_exclusions=("البضائع الموجودة داخل الحاويات", "كبائن وبيوت جاهزة للسكن"),
        disambiguation_anchors=("حاوية", "كونتينر", "حاوية 20 قدم", "حاوية 40 قدم", "خزان IBC", "حاويات شحن", "container", "shipping container", "20ft container", "40ft container", "ibc tote"),
    ),
    169: CategorySpec(
        root_id=169,
        name_ar="الأسفنج",
        name_en="gypsum",
        domains=("إسفنج أثاث", "فوم وعوازل مرنة", "رولات إسفنج", "حشوات إسفنجية"),
        core_nouns=(
            "رولات إسفنج ضغط عالي لتنجيد الكنب", "ألواح إسفنج مضغوط مقاسات لتصنيع المراتب",
            "بلوكات إسفنج خام كثافة 30 و 40", "حشوات إسفنجية مقطعة للوسائد والمجالس",
            "إسفنج عازل للصوت هرمي للاستوديوهات", "رولات فوم إسفنجي تغليف أثاث وبضائع",
            "إسفنج طبي مرن لتصنيع الكراسي والمقاعد"
        ),
        core_nouns_en=(
            "high density upholstery foam rolls for sofas", "compressed foam sheets for mattress manufacturing",
            "raw polyurethane foam blocks density 30 and 40", "shredded foam cushion filling for majlis",
            "acoustic soundproofing pyramid foam panels", "polyethylene protective foam rolls for packaging",
            "medical grade flexible foam for seating cushions"
        ),
        brands=("مصنع الراجحي للإسفنج", "إسفنج سليب هاي", "إسفنج اليمامة", "مصنع الشرقية للفوم"),
        brands_en=("Al Rajhi Foam Factory", "Sleep High Sponge", "Yamama Polyurethane Foam", "Eastern Foam Co"),
        specs_and_models=("كثافة دنسيتي 30", "كثافة دنسيتي 40 سوبر", "ألواح سماكة 10 سم مقاس 2*1 متر"),
        specs_and_models_en=("density 30 kg/m3", "super high density 40 kg/m3", "10cm thickness 2x1m sheets"),
        packaging_types=("رولات إسفنج مكبوسة بلاستيك", "بلوكات إسفنج كبيرة على دينا", "طبالي ألواح فوم إسفنجي"),
        packaging_types_en=("compressed plastic wrapped foam rolls", "large foam blocks open truckload", "foam sheet pallets"),
        strict_inclusions=("إسفنج ورولات وألواح فوم خام لتنجيد وصناعة الأثاث"),
        strict_exclusions=("كنب وأثاث جاهز مكتمل", "عوازل بولي يوريثان ومواد بناء خرسانية"),
        disambiguation_anchors=("إسفنج", "رول إسفنج", "ألواح إسفنج", "إسفنج مضغوط", "تنجيد إسفنج", "بلوك إسفنج", "sponge", "foam", "upholstery foam", "foam rolls", "pu foam block"),
    ),
    175: CategorySpec(
        root_id=175,
        name_ar="منظفات",
        name_en="Refrigerators",
        domains=("منظفات متخصصة", "صابون سائل تجاري", "أقراص جلايات ومزيلات شحوم"),
        core_nouns=(
            "صابون غسيل أيدي سائل جلونات تجارية", "أقراص غسالات صحون فنش وفيري كراتين",
            "شامبو عبايات وملابس داكنة برسيل جالونات", "مزيلات شحوم ودهون الأفران والمطابخ فورنيت",
            "منظفات أرضيات وسيراميك مركزة للمجمعات", "معطرات ومنعمات أقمشة داوني ولينور",
            "شامبو غسيل سيارات رغوة كثيفة براميل"
        ),
        core_nouns_en=(
            "commercial liquid hand wash soap gallons", "Finish and Fairy automatic dishwasher tablet cartons",
            "Persil abaya and dark clothes shampoo gallons", "Fornet heavy duty kitchen oven degreaser cleaner",
            "concentrated commercial tile and floor cleaner", "Downy and Comfort concentrated fabric softeners",
            "high foaming car wash auto shampoo drums"
        ),
        brands=("برسيل Persil", "فنش Finish", "داوني Downy", "كومفورت", "لوركس للسيارات", "فورنيت"),
        brands_en=("Persil", "Finish Dishwasher", "Downy Softener", "Comfort", "Lurex Auto Care", "Fornet Degreaser"),
        specs_and_models=("جالون 5 لتر معطر", "كرتون 100 قرص جلاية", "برميل 20 لتر صابون سائل"),
        specs_and_models_en=("5L scented gallon", "carton of 100 all-in-one dishwasher tablets", "20L commercial soap drum"),
        packaging_types=("كراتين جالونات منظفات", "طبالي عبوات بلاستيكية كراتين", "جوالين 20 لتر منظفات"),
        packaging_types_en=("gallon cleaner master cartons", "bottled chemical pallets", "20L chemical jerrycans"),
        strict_inclusions=("مستحضرات صابون سائل متخصصة وشامبو أقمشة وأقراص جلايات"),
        strict_exclusions=("أجهزة غسالات أو ثلاجات كهربائية", "مواد بترولية خام"),
        disambiguation_anchors=("منظفات سائلة", "شامبو عبايات", "أقراص غسالة صحون", "منعم أقمشة داوني", "مزيل دهون", "detergents", "liquid soap", "dishwasher tablets", "degreaser", "fabric softener"),
    ),
    179: CategorySpec(
        root_id=179,
        name_ar="وحدات تبريد",
        name_en="Stoves",
        domains=("مكيفات", "غرف تبريد", "ثلاجات ومجمدات تجارية", "كمبروسرات تكييف"),
        core_nouns=(
            "مكيفات سبليت جدارية 18 و 24 وحدة كراتين", "مكيفات شباك كراتين طاقة وكفاءة",
            "مكيفات صحراوية قش وكرتون للحدائق والمخيمات", "ثلاجات عرض سوبرماركت باب زجاجي ومجمدات",
            "وحدات تبريد غرف تخزين ومستودعات فريزر وتبريد", "كمبروسرات تكييف وتبريد صناعي كراتين",
            "مكيفات دولابي مركزي 5 طن كراتين جديدة"
        ),
        core_nouns_en=(
            "18000 and 24000 BTU wall split air conditioners", "energy efficient window air conditioning units",
            "portable desert evaporative air coolers for outdoors", "commercial supermarket glass door display refrigerators freezers",
            "cold room refrigeration condensing units and evaporators", "commercial HVAC refrigeration compressor units",
            "5-ton standing floor cabinet central air conditioners"
        ),
        brands=("جري Gree", "ماندو Mando", "ميديا Midea", "ال جي تكييف LG", "كارير Carrier", "أوجنرال", "الزامل مكيفات"),
        brands_en=("Gree AC", "Mando Plus AC", "Midea HVAC", "LG Air Conditioning", "Carrier HVAC", "O General", "Zamil Air Conditioners"),
        specs_and_models=("قدرة 18000 وحدة", "قدرة 24000 BTU موفر", "غاز R410A صديق للبيئة", "دولابي 5 طن"),
        specs_and_models_en=("18000 BTU capacity", "24000 BTU inverter", "R410A eco refrigerant gas", "5-ton floor standing"),
        packaging_types=("كراتين مكيفات وحدات داخلية وخارجية", "طبالي مكيفات سبليت", "ثلاجات عرض محملة واقفة"),
        packaging_types_en=("indoor and outdoor AC unit cartons", "split AC palletized cartons", "upright display chiller truckload"),
        strict_inclusions=("مكيفات هواء ووحدات تبريد وثلاجات عرض تجارية وكمبروسرات تكييف"),
        strict_exclusions=("ثلاجات شحن كمركبات نقل", "مواد غذائية مبردة"),
        disambiguation_anchors=("مكيف", "سبليت", "وحدات تبريد", "مكيف شباك", "كمبروسر مكيف", "ثلاجة عرض", "air conditioner", "split ac", "cooling unit", "chiller display", "hvac compressor"),
    ),
    192: CategorySpec(
        root_id=192,
        name_ar="عطور",
        name_en="Air conditioners",
        domains=("عطور شرقية وغربية", "بخور ودهن عود", "مستحضرات تجميل وعناية"),
        core_nouns=(
            "عطور فرنسية نسائية ورجالية كراتين وبوكسات", "دهن عود كمبودي وتول مخلط ملكي",
            "بخور وعود موروكي وكلمنتان فاخر أكياس وبوكسات", "مستحضرات تجميل ومكياج وأرواج كراتين",
            "لوشنات وكريمات ترطيب وعناية بالبشرة والجسم", "مباخر كهربائية وخشبية فاخرة بوكسات هدايا",
            "زيوت عطرية مركزة ومعطرات مفارش وغرف"
        ),
        core_nouns_en=(
            "boxed French men and women luxury perfumes", "Cambodian Dehn Al Oud and royal perfume oils",
            "luxury Maroki and Kalimantan agarwood incense bukhoor", "cosmetics makeup kits, foundations and lipsticks",
            "moisturizing body lotions and skincare creams", "luxury electric and wooden incense burners mubkhara",
            "concentrated fragrance diffuser oils and room linen sprays"
        ),
        brands=("عبدالصمد القرشي", "العربية للعود", "الماجد للعود", "إبراهيم القرشي", "شانيل", "ديور", "درعه للعطور", "هدى بيوتي"),
        brands_en=("Abdul Samad Al Qurashi", "Arabian Oud", "Al Majed Oud", "Ibrahim Al Qurashi", "Chanel Perfumes", "Dior Fragrances", "Deraah", "Huda Beauty"),
        specs_and_models=("تولة دهن عود", "عطر 100 مل Eau de Parfum", "أوقية عود مروكي", "طقم هدايا عطور"),
        specs_and_models_en=("tola concentrated perfume oil", "100ml Eau de Parfum spray", "ounce premium agarwood chips", "luxury perfume gift set"),
        packaging_types=("بوكسات عطور هدايا مغلفة", "كراتين مستحضرات تجميل وعطور محكمة", "طبالي كراتين عناية وعطور"),
        packaging_types_en=("gift-wrapped perfume presentation boxes", "sealed cosmetics and fragrance master cartons", "fragrance and beauty pallets"),
        strict_inclusions=("عطور وبخور ومستحضرات تجميل وعناية شخصية فاخرة"),
        strict_exclusions=("مكيفات هواء", "منظفات ومعقمات أرضيات كيميائية"),
        disambiguation_anchors=("عطور", "بخور", "دهن عود", "مكياج", "عطر فرنسي", "مبخرة", "لوشن عناية", "perfume", "fragrance", "oud", "incense", "cosmetics", "skincare"),
    ),
    193: CategorySpec(
        root_id=193,
        name_ar="معدات السلامة والأمن",
        name_en="Safety  Firefighting Equipment",
        domains=("إطفاء حريق", "معدات وقاية شخصية PPE", "كاميرات وأجهزة إنذار", "أمن صناعي"),
        core_nouns=(
            "طفايات حريق بودرة جافة ورغوة وثاني أكسيد الكربون كراتين", "خراطيم ومحابس مكافحة الحريق كراتين ولفات",
            "كواشف دخان وحرارة ولوحات إنذار حريق", "أحذية سلامة صناعية سفتي شوز كراتين",
            "خوذ حماية بلاستيكية ونظارات واقية للمشاريع", "سترات فسفورية عاكسة للضوء كراتين يونيفورم",
            "صناديق وخزائن إطفاء حريق ستانلس معلقة", "أحزمة أمان للعمل على المرتفعات وشباك حماية"
        ),
        core_nouns_en=(
            "dry chemical powder, foam and CO2 fire extinguishers", "firefighting hoses and landing valves",
            "smoke and heat detectors and fire alarm control panels", "steel toe industrial safety work boots",
            "protective hard hats and project safety goggles", "high visibility reflective safety vests",
            "stainless steel recessed fire hose cabinets", "fall protection full body safety harnesses and safety nets"
        ),
        brands=("نافكو NAFFCO", "سفتي توتال", "كاتربيلر أحذية سلامة", "3M معدات سلامة", "هانيويل سلامة"),
        brands_en=("NAFFCO Fire Protection", "Safety Total", "Caterpillar Safety Footwear", "3M Personal Safety", "Honeywell Safety"),
        specs_and_models=("طفاية بودرة 6 كجم", "طفاية CO2 5 كجم", "خرطوم حريق 1.5 بوصة 30 متر", "سفتي مقاس 42"),
        specs_and_models_en=("6kg dry powder extinguisher", "5kg CO2 fire extinguisher", "1.5 inch 30m fire hose reel", "safety boots size EU 42"),
        packaging_types=("كراتين طفايات حريق", "طبالي أحذية وخوذ سلامة", "صناديق معدات إنذار وإطفاء"),
        packaging_types_en=("extinguisher master cartons", "safety helmets and boots pallets", "fire alarm and safety gear crates"),
        strict_inclusions=("معدات وأدوات السلامة ومكافحة الحريق والوقاية المهنية"),
        strict_exclusions=("أجهزة إلكترونية شخصية ترفيهية", "ملابس وأحذية عادية غير واقية"),
        disambiguation_anchors=("سلامة", "طفاية حريق", "سفتي شوز", "إنذار حريق", "خوذة سلامة", "إطفاء حريق", "safety equipment", "fire extinguisher", "safety shoes", "fire alarm", "ppe"),
    ),
}
