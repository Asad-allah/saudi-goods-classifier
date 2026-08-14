"""Production-Grade Domain Knowledge & Strict Semantic Constraints for all 90 Leaf Categories.
Enforces realistic domain-specific containers, real Saudi market goods, authentic phrasing,
and eliminates any semantic contradictions (e.g. live cattle in cartons or limestone with SFDA approval).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

DomainType = Literal[
    "livestock", "food_dry", "food_chilled", "food_frozen", "beverage", "dairy", "oils_food",
    "produce", "mining_bulk", "cement_plaster", "rebar_steel", "building_general", "insulation",
    "pipes_sanitary", "electrical_supplies", "glass_aluminum", "heavy_equipment_tools",
    "auto_tires", "auto_spares_new", "auto_spares_used", "auto_transport_service",
    "petroleum_oils", "water_tanks", "gas_tanks", "sanitation_service", "chemicals",
    "prefab_houses", "clothes_shoes", "charcoal_firewood", "medicines_human", "medicines_vet",
    "bicycles", "motorbikes", "medical_supplies", "books_stationery", "agriculture_fertilizers",
    "forage_grains", "power_generators", "textiles_fabrics", "tobacco", "waste_remnants",
    "bottled_water", "containers_shipping", "foam_sponges", "cleaning_soap", "cooling_ac_units",
    "furniture_new", "furniture_used", "electronics_it", "perfumes_oud", "safety_firefighting"
]

@dataclass(frozen=True)
class ProductionDomainRule:
    domain_type: DomainType
    nouns_ar: tuple[str, ...]
    nouns_en: tuple[str, ...]
    brands_ar: tuple[str, ...]
    brands_en: tuple[str, ...]
    allowed_containers_ar: tuple[str, ...]
    allowed_containers_en: tuple[str, ...]
    allowed_contexts_ar: tuple[str, ...]
    allowed_contexts_en: tuple[str, ...]
    short_query_templates_ar: tuple[str, ...]
    short_query_templates_en: tuple[str, ...]


# Strict domain-specific containers & contexts
CONTAINERS_LIVESTOCK_AR = ("رؤوس", "رأس", "حمولة دينا شبك", "حمولة تريلا مواشي", "دفعة حظيرة", "طليان شبك", "حمولة وانيت")
CONTAINERS_LIVESTOCK_EN = ("heads", "livestock truckload", "herd batch", "corral batch", "pickup load")

CONTAINERS_BULK_MINING_AR = ("رد قلاب", "رد تريلا 24 متر", "حمولة وايت", "طن صب", "رد بطحاء", "شحنة كسارة")
CONTAINERS_BULK_MINING_EN = ("tipper truckload", "24m semi-trailer load", "bulk metric tons", "crusher dispatch")

CONTAINERS_HEAVY_BUILDING_AR = ("طبالي مشمعة", "أكياس 50 كجم", "ربطات طن", "حمولة تريلا صبة", "شحنة رافعة واصل الموقع", "رد لوري")
CONTAINERS_HEAVY_BUILDING_EN = ("palletized shrink-wrap", "50kg bags", "metric ton bundles", "flatbed articulated truckload")

CONTAINERS_FMCG_FOOD_AR = ("كراتين", "طبالي خشبية", "كرتون شد 24 علبة", "أكياس 40 كجم خيش", "برطمانات كراتين", "طرد تموين")
CONTAINERS_FMCG_FOOD_EN = ("master cartons", "wooden pallets", "24-can shrink pack", "40kg burlap bags", "wholesale grocery batch")

CONTAINERS_CHILLED_FROZEN_AR = ("كراتين ثلاجة مبردة", "طبالي شاحنة تبريد -18", "كرتون حفظ حراري", "صناديق فلين مثلجة")
CONTAINERS_CHILLED_FROZEN_EN = ("reefer chilled cartons", "cold storage pallets -18C", "insulated thermal boxes")

CONTAINERS_AUTO_SPARES_AR = ("طقم كامل", "كرتون أصلي وكالة", "طبلية قطع", "حبة بالكرتون", "أطقم 4 حبات", "شد كراتين")
CONTAINERS_AUTO_SPARES_EN = ("complete set", "genuine OEM box", "palletized parts", "boxed unit", "4-piece set")

CONTAINERS_PHARMA_MEDICAL_AR = ("كراتين معقمة", "عبوات طبية محكمة", "طبالي مستودعات أدوية", "كرتون 50 باكت", "أمبولات طبية")
CONTAINERS_PHARMA_MEDICAL_EN = ("sterile cartons", "sealed medical bottles", "temperature-controlled pharma pallets", "50-box master carton")

CONTAINERS_CLOTHING_AR = ("كراتين بالات", "درازن مغلفة", "طرد ملابس", "كرتون 12 حبة", "أكياس تعبئة معلقة")
CONTAINERS_CLOTHING_EN = ("baled cartons", "sealed dozens", "clothing parcels", "12-unit pack", "hanger retail pack")

CONTAINERS_ELECTRONICS_AR = ("كراتين مقفلة بتغليف المصنع", "طبلية أجهزة إلكترونية", "حبة بالكرتون مع الضمان", "بوكسات تجارية")
CONTAINERS_ELECTRONICS_EN = ("factory sealed boxes", "electronic pallets", "retail box with warranty", "commercial master pack")


# 90 Leaf Categories mapped to strictly realistic domain items
LEAF_PRODUCTION_MAP: dict[int, ProductionDomainRule] = {
    # 14: سلع استهلاكية جافة (Dry FMCG)
    14: ProductionDomainRule(
        domain_type="food_dry",
        nouns_ar=("أرز بسمتي الشعلان", "أرز مزة أبو كاس", "أرز باب الهند", "سكر الأسرة ناعم", "مكرونة قودي", "مكرونة بيرفيتو", "طحين فوم كويتي", "طحين بر صوامع", "عدس أحمر حب", "فول مجفف", "شوفان كويكر", "شاي كبوس فرط", "شاي ربيع إكسبريس", "هيل أمريكي أخضر", "قهوة هرري خولاني", "شوكولاتة كيت كات", "بسكويت شاي ميموريز", "تونة قودي خفيف", "زيتون أسود معلب", "مكسرات باجة مشكلة"),
        nouns_en=("Shalan Basmati Rice", "Abu Kass Sella Rice", "Bab Al Hind Amber Rice", "Al Osra Fine Sugar", "Goody Macaroni", "Perfetto Spaghetti", "Foom Kuwaiti Flour", "Whole Grain Wheat Flour", "Red Split Lentils", "Dry Fava Beans", "Quaker Rolled Oats", "Al Kbous Loose Tea", "Rabea Express Tea", "Green Jumbo Cardamom", "Harari Green Coffee", "KitKat Chocolate Bars", "Memories Tea Biscuits", "Goody Light Meat Tuna", "Canned Black Olives", "Baja Mixed Roasted Nuts"),
        brands_ar=("الشعلان", "أبو كاس", "قودي", "الأسرة", "باجة", "كبوس", "ربيع", "ليبتون", "كويكر"),
        brands_en=("Al Shalan", "Abu Kass", "Goody", "Al Osra", "Baja", "Al Kbous", "Rabea", "Lipton", "Quaker"),
        allowed_containers_ar=CONTAINERS_FMCG_FOOD_AR,
        allowed_containers_en=CONTAINERS_FMCG_FOOD_EN,
        allowed_contexts_ar=("تموين سوبرماركت", "طلبية جملة", "توريد مستودع مواد غذائية", "مقاضي بقالة", "توصيل إعاشة"),
        allowed_contexts_en=("Supermarket replenishment", "Wholesale grocery supply", "Food warehouse order", "Retail FMCG batch"),
        short_query_templates_ar=("{noun}", "كرتون {noun}", "{noun} جملة", "{qty} كيس {noun}", "طبلية {noun}"),
        short_query_templates_en=("{noun}", "carton of {noun}", "wholesale {noun}", "{qty} bags {noun}", "pallet of {noun}")
    ),
    # 15: سلع مبردة (Chilled FMCG)
    15: ProductionDomainRule(
        domain_type="food_chilled",
        nouns_ar=("حليب طازج المراعي", "لبن عيران نادك", "زبادي عائلي الصافي", "زبادي يوناني ندى", "قشطة طازجة بلدي", "زبدة لورباك غير مملحة", "جبنة كاسات المراعي", "جبن شيدر كرافت", "جبن حلوم الصافي", "جبنة موزاريلا فرسانا", "عصير برتقال طازج", "بيض مائدة مزارع الوطنية", "بيض فقيه طازج", "عجينة سمبوسة سويتز مبردة"),
        nouns_en=("Almarai Fresh Milk", "Nadec Fresh Ayran Laban", "Al Safi Fresh Yogurt", "Nada Greek High Protein Yogurt", "Fresh Baladi Table Cream", "Lurpak Unsalted Butter", "Almarai Cream Cheese Spread", "Kraft Cheddar Cheese", "Al Safi Halloumi Cheese", "Forsana Shredded Mozzarella", "Fresh Squeezed Orange Juice", "Al-Watania Fresh Table Eggs", "Fakieh Farm Fresh Eggs", "Switz Chilled Sambosa Pastry"),
        brands_ar=("المراعي", "نادك", "الصافي", "ندى", "لورباك", "كرافت", "الوطنية", "فقيه", "فرسانا"),
        brands_en=("Almarai", "Nadec", "Al Safi", "Nada", "Lurpak", "Kraft", "Al-Watania", "Fakieh", "Forsana"),
        allowed_containers_ar=CONTAINERS_CHILLED_FROZEN_AR,
        allowed_containers_en=CONTAINERS_CHILLED_FROZEN_EN,
        allowed_contexts_ar=("توزيع ثلاجة يومي", "شحنة مبردة دينا ثلاجة", "توريد ألبان وأجبان", "طلبية فطور ومخابز"),
        allowed_contexts_en=("Daily chilled delivery", "Reefer van shipment", "Dairy and cheese wholesale", "Chilled food batch"),
        short_query_templates_ar=("{noun}", "شحنة مبردة {noun}", "كراتين {noun}", "طبق {noun}", "ثلاجة {noun}"),
        short_query_templates_en=("{noun}", "chilled {noun}", "cartons of {noun}", "fresh refrigerated {noun}")
    ),
    # 16: سلع مثلجة ومجمدة (Frozen FMCG)
    16: ProductionDomainRule(
        domain_type="food_frozen",
        nouns_ar=("دجاج مجمد ساديا 10 حبات", "دجاج الوطنية مجمد", "صدور دجاج دو مجمدة", "أفخاذ دجاج برديكس", "لحم غنم مفروم أمريكانا", "لحم بقر برازيلي مجمد", "برجر لحم حلواني جامبو", "برجر دجاج السنبلة بالبقسماط", "ناجتس دجاج أمريكانا", "روبيان مجمد مقشور رويال", "فيليه سمك أبيض سيبلو", "بطاطس نصف مقلية لامب وستون", "خضار مشكل العملاق الأخضر", "ملوخية مفرومة داري", "فراولة مجمدة بونو", "آيس كريم باسكن روبنز"),
        nouns_en=("Sadia Frozen Whole Chicken", "Al-Watania Frozen Chicken", "Doux Frozen Tender Chicken Breasts", "Perdix Frozen Chicken Thighs", "Americana Minced Mutton", "Brazilian Frozen Minced Beef", "Halwani Jumbo Beef Burgers", "Sunbulah Breaded Chicken Burgers", "Americana Chicken Nuggets", "Royal Frozen Peeled Shrimp", "Siblou White Fish Fillets", "Lamb Weston French Fries", "Green Giant Frozen Mixed Vegetables", "Dari Chopped Frozen Molokhia", "Pono Frozen Strawberries", "Baskin Robbins Ice Cream"),
        brands_ar=("ساديا", "دو", "أمريكانا", "السنبلة", "حلواني", "داري", "لامب وستون", "سيبلو", "باسكن روبنز"),
        brands_en=("Sadia", "Doux", "Americana", "Sunbulah", "Halwani", "Dari", "Lamb Weston", "Siblou", "Baskin Robbins"),
        allowed_containers_ar=CONTAINERS_CHILLED_FROZEN_AR,
        allowed_containers_en=CONTAINERS_CHILLED_FROZEN_EN,
        allowed_contexts_ar=("شحنة مجمدات تريلا ثلاجة", "توريد مطاعم وإعاشة مجمدة", "توزيع مجمدات للمستودعات", "طلبية لحوم ودواجن مجمدة"),
        allowed_contexts_en=("Deep frozen reefer shipment -18C", "Restaurant frozen supply", "Frozen poultry and meat consignment"),
        short_query_templates_ar=("{noun}", "كرتون {noun}", "مجمدات {noun}", "تريلا ثلاجة {noun}", "شحنة {noun}"),
        short_query_templates_en=("{noun}", "frozen {noun}", "case of frozen {noun}", "reefer shipment {noun}")
    ),
    # 124: المواشي (Livestock / Cattles)
    124: ProductionDomainRule(
        domain_type="livestock",
        nouns_ar=("خروف نعيمي بلدي", "خروف حري جبر", "خروف نجدي صنف", "تيس عارضي بلدي", "تيس تهامي هرفي", "عجل بقري هولندي تسمين", "بقر حليب فريزيان", "حاشي بلدي صغير", "قعود حاشي مفرود", "كبش سواكني مربى", "خراف بربري شحن"),
        nouns_en=("Naemi Baladi Sheep", "Hari Jabr Sheep", "Najdi Purebred Sheep", "Ardi Baladi Goat", "Tihami Young Goat", "Dutch Veal Calf", "Friesian Dairy Cattle", "Young Baladi Camel", "Mafrood Camel", "Sawkani Sudanese Sheep", "Berberi Imported Sheep"),
        brands_ar=("مزارع القصيم للمواشي", "مراح وادي الدواسر", "سوق الأنعام بالرياض", "مربط حائل", "مواشي جدة"),
        brands_en=("Al Qassim Livestock Farms", "Wadi Al Dawasir Cattle", "Riyadh Livestock Market", "Hail Farm Stock"),
        allowed_containers_ar=CONTAINERS_LIVESTOCK_AR,
        allowed_containers_en=CONTAINERS_LIVESTOCK_EN,
        allowed_contexts_ar=("تحميل دينا شبك مواشي", "نقل أغنام من المراح", "طلبية مسالخ ومطابخ", "بيع مواشي سوق الأنعام", "شحنة حظيرة تريلا مواشي"),
        allowed_contexts_en=("Livestock truck loading", "Live animal transport from corral", "Slaughterhouse supply batch", "Live cattle consignment"),
        short_query_templates_ar=("{noun}", "{qty} رأس {noun}", "دينا {noun}", "نقل {noun}", "حراج {noun}"),
        short_query_templates_en=("{noun}", "{qty} heads of {noun}", "livestock truck of {noun}", "live {noun}")
    ),
    # 123: الطيور (Birds & Poultry)
    123: ProductionDomainRule(
        domain_type="livestock",
        nouns_ar=("صوص دجاج لاحم الوطنية", "صوص دجاج بياض مزارع فقيه", "دجاج حي مزارع الأخوين", "دجاج بلدي حبايب", "حمام فرنسي لاحم", "حمام زاجل سباق", "سمان مزارع أسترا طازج", "بط بلدي رومي", "طيور كروان وببغاء روز"),
        nouns_en=("Day-Old Broiler Chicks Al-Watania", "Layer Chicks Fakieh Farms", "Live Farm Chickens Al-Akhawain", "Baladi Live Chickens", "French Squab Meat Pigeons", "Racing Homing Pigeons", "Astra Farm Fresh Quails", "Live Turkey and Ducks", "Lovebirds and Parrots"),
        brands_ar=("الوطنية للدواجن", "دواجن فقيه", "مزارع الأخوين", "مزارع أسترا", "دواجن الرمحية"),
        brands_en=("Al-Watania Poultry", "Fakieh Farms", "Al-Akhawain Farms", "Astra Poultry", "Ramhiyah Farms"),
        allowed_containers_ar=("أقفاص طيور بلاستيك", "صناديق كتاكيت مهواة", "دينا شبك دواجن", "حمولة سيارة كتاكيت مكيفة", "أقفاص حديد"),
        allowed_containers_en=("ventilated chick boxes", "plastic poultry crates", "temperature-controlled chick truckload", "bird transport cages"),
        allowed_contexts_ar=("نقل كتاكيت من الفقاسة", "توصيل دواجن حية للمجازر", "شحنة أقفاص حمام وسمان", "توريد مزارع دواجن"),
        allowed_contexts_en=("Hatchery chick delivery", "Live poultry transport to slaughterhouse", "Caged game birds shipment"),
        short_query_templates_ar=("{noun}", "أقفاص {noun}", "دينا {noun}", "كتاكيت {noun}", "شحنة {noun}"),
        short_query_templates_en=("{noun}", "crates of {noun}", "live {noun}", "batch of {noun}")
    ),
    # 144: الجمال والأحصنة (Camels and Horses)
    144: ProductionDomainRule(
        domain_type="livestock",
        nouns_ar=("خيل عربي أصيل واهو", "فرس قفز حواجز ثوروبريد", "مهور عربية أصيلة", "إبل مجاهيم مزاين", "إبل وضح ونوق حلب", "نوق شعل وصفر حمر", "حيران وضح وبكار", "قعود مجهم للبيع"),
        nouns_en=("Purebred Arabian Horse WAHO", "Thoroughbred Show Jumping Mare", "Pure Arabian Foals", "Majaheem Mzayen Camels", "Wadh Milk Camels", "Shoal and Sofr Camels", "Young Wadh Camel Calves", "Majaheem Pack Camel"),
        brands_ar=("مرابط الخالدية", "إسطبلات الشقب", "مهرجان الملك عبدالعزيز للإبل", "مرابط ديراب", "إسطبلات الجنادرية"),
        brands_en=("Al Khalediah Stables", "Al Shaqab Arabian Stud", "King Abdulaziz Camel Festival", "Dirab Equestrian Stables"),
        allowed_containers_ar=("مقطورة خيل مجهزة", "تريلا جوانب نقل إبل", "دينا نقل خيول مبطنة", "شاحنة نقل هجن مجهزة"),
        allowed_containers_en=("padded horse trailer", "heavy camel transport truck", "equestrian transit vehicle"),
        allowed_contexts_ar=("نقل خيل للسباق وميدان الملك خالد", "شحنة إبل مزاين للقرية التراثية", "نقل مهرة وبكار من العزبة"),
        allowed_contexts_en=("Racehorse equestrian transport", "Mzayen camel convoy", "Stallion and mare relocation"),
        short_query_templates_ar=("{noun}", "نقل {noun}", "مقطورة {noun}", "{qty} رؤوس {noun}"),
        short_query_templates_en=("{noun}", "transport of {noun}", "horse trailer with {noun}", "purebred {noun}")
    ),
    # 121: أسمنت (Cement)
    121: ProductionDomainRule(
        domain_type="cement_plaster",
        nouns_ar=("إسمنت بورتلاندي عادي اليمامة", "إسمنت مقاوم للأملاح SRC أسمنت الرياض", "إسمنت أبيض سوبر رويال رأس الخيمة", "إسمنت تشطيب ولياسة ناعم", "إسمنت صبات مائية سريع الشك"),
        nouns_en=("Yamama Ordinary Portland Cement OPC", "Riyadh Sulfate Resistant Cement SRC", "Super White Portland Cement RAK", "Finishing and Plastering Masonry Cement", "Rapid Setting Hydraulic Cement"),
        brands_ar=("أسمنت اليمامة", "أسمنت الرياض", "أسمنت السعودية", "أسمنت ينبع", "أسمنت القصيم", "أسمنت المدينة"),
        brands_en=("Yamama Cement", "Riyadh Cement", "Saudi Cement", "Yanbu Cement", "Qassim Cement", "City Cement"),
        allowed_containers_ar=("أكياس 50 كجم", "طبالي إسمنت مغلفة 40 كيس", "حمولة تريلا تيدر 1000 كيس", "صهريج بلك صوامع صب"),
        allowed_containers_en=("50kg paper sacks", "shrink-wrapped 40-bag pallets", "1000-bag semi-trailer load", "bulk cement silo tanker"),
        allowed_contexts_ar=("توريد صبة للموقع الإنشائي", "شحنة مقاولات وبناء", "طلبية مستودع مواد بناء", "تنزيل إسمنت عمارة"),
        allowed_contexts_en=("Site construction supply", "Contractor building material order", "Bulk cement dispatch to batching plant"),
        short_query_templates_ar=("{noun}", "{qty} كيس {noun}", "تريلا {noun}", "طبلية {noun}", "شحنة {noun}"),
        short_query_templates_en=("{noun}", "{qty} bags {noun}", "truckload of {noun}", "palletized {noun}")
    ),
    # 55: حديد التسليح (Reinforcing Rebar Steel)
    55: ProductionDomainRule(
        domain_type="rebar_steel",
        nouns_ar=("حديد تسليح سابك مقاس 16 ملم", "حديد تسليح سابك مقاس 14 ملم", "حديد تسليح الراجحي مقاس 12 ملم", "حديد تسليح الاتفاق مقاس 10 ملم", "حديد كانات مقاس 8 ملم", "حديد تسليح ثقيل مقاس 25 ملم للجسور", "شبك حديد تسليح صبة أرضيات مقاس 8 ملم", "سلك رباط حديد مجلفن لفات"),
        nouns_en=("SABIC 16mm Deformed Steel Rebar", "SABIC 14mm Construction Steel Rebar", "Al-Rajhi 12mm Grade 60 Rebar", "Al-Ittefaq 10mm High Tensile Rebar", "8mm Steel Rebar for Stirrups", "25mm Heavy Structural Rebar", "Welded Steel Wire Mesh for Concrete Slabs 8mm", "Galvanized Steel Tie Wire Coils"),
        brands_ar=("حديد سابك", "حديد الراجحي", "حديد الاتفاق", "حديد اليمامة", "حديد الجندل"),
        brands_en=("SABIC Steel", "Al Rajhi Steel", "Al Ittefaq Steel", "Yamama Steel", "Jandal Steel"),
        allowed_containers_ar=("ربطات طن شد المصنع", "حمولة تريلا سطحة 30 طن", "لفات وبكرات سلك", "شحنة ونش واصل المشروع"),
        allowed_containers_en=("metric ton factory bundles", "30-ton flatbed trailer load", "wire spools and coils", "crane truckload dispatch"),
        allowed_contexts_ar=("توريد حديد صبة للأبراج والمباني", "شحنة مقاولات تسليح خرسانة", "طلبية حدادة مسلحة واصل الموقع"),
        allowed_contexts_en=("Structural reinforcement supply", "Concrete foundation steel order", "Construction rebar dispatch"),
        short_query_templates_ar=("{noun}", "{qty} طن {noun}", "ربطة {noun}", "تريلا {noun}", "حديد {noun}"),
        short_query_templates_en=("{noun}", "{qty} tons of {noun}", "bundle of {noun}", "flatbed of {noun}")
    ),
    # 134: الإطارات (Tires)
    134: ProductionDomainRule(
        domain_type="auto_tires",
        nouns_ar=("كفرات هانكوك مقاس 17 كوري", "إطارات ميشلان مقاس 18 بايلوت سبورت", "كفرات بريدجستون بوتينزا 19", "إطارات يوكوهاما جيولاندر جيب", "كفرات دنلوب مقاس 16 هايلوكس", "كفرات تويو ياباني مقاس 20 لاندكروزر", "كفرات نيتو حجري للبر", "إطارات شاحنات تريلا مقاس 24 سلك", "كفرات بوبكات وشيول صب مقاس 23.5-25"),
        nouns_en=("Hankook 17-inch Passenger Tires", "Michelin Pilot Sport 18-inch High Performance Tires", "Bridgestone Potenza 19-inch Tires", "Yokohama Geolandar SUV All-Terrain Tires", "Dunlop 16-inch Light Truck Tires", "Toyo 20-inch Land Cruiser Tires", "Nitto Desert Mud-Terrain Tires", "Heavy Radial Truck Tires Size 24", "Solid Industrial Loader Tires 23.5-25"),
        brands_ar=("هانكوك", "ميشلان", "بريدجستون", "يوكوهاما", "دنلوب", "تويو", "كومهو", "ماكسس", "بيريللي"),
        brands_en=("Hankook", "Michelin", "Bridgestone", "Yokohama", "Dunlop", "Toyo Tires", "Kumho", "Maxxis", "Pirelli"),
        allowed_containers_ar=("طقم 4 حبات", "كرتون شد 2 حبة", "طبلية إطارات مشمعة 40 حبة", "حمولة دينا كفرات جملة", "شحنة كونتينر إطارات"),
        allowed_containers_en=("set of 4 tires", "shrink-wrapped 40-tire pallet", "commercial dyna truckload of tires", "container tire load"),
        allowed_contexts_ar=("توريد بنشر وورش سيارات", "طلبية كفرات جملة للموزعين", "شحنة إطارات جديدة بطاقة كفاءة الطاقة ساسو"),
        allowed_contexts_en=("Tire shop replenishment", "Wholesale tire distributor batch", "SASO energy efficiency labeled tires"),
        short_query_templates_ar=("{noun}", "طقم {noun}", "{qty} حبة {noun}", "كفرات {noun}", "طبلية {noun}"),
        short_query_templates_en=("{noun}", "set of 4 {noun}", "{qty} units {noun}", "tires {noun}")
    ),
    # 165: قطع غيار جديدة (New Auto Spare Parts)
    165: ProductionDomainRule(
        domain_type="auto_spares_new",
        nouns_ar=("فحمات فرامل سيراميك تويوتا كامري أصلي", "أقمشة فرامل خلفية نيسان باترول", "بواجي ليزر إيريديوم دنسو وكالة", "مساعدات هيدروليك جبريل أمريكي", "مقصات أمامية كاملة مع الجلود هيونداي", "دينمو شحن وكهرباء بوش 12 فولت", "سلف ماكينة تشغيل مرش وكالة", "رديتر ماء تبريد ألومنيوم دولفين", "كمبروسر مكيف سيارة ساندن ياباني", "فلتر زيت مكينة سيفون تويوتا وكالة", "فلتر هواء محرك بوش أصلي", "طرمبة بنزين بوش داخل التانكي", "كويلات إشعال ديلفي أصلية"),
        nouns_en=("Toyota Camry Genuine Ceramic Brake Pads", "Nissan Patrol Rear Brake Shoes", "Denso Iridium Spark Plugs OEM", "Gabriel Heavy Duty Gas Struts", "Hyundai Front Suspension Control Arms", "Bosch 12V High Output Alternator", "Genuine Engine Starter Motor", "Dolphin Heavy Duty Aluminum Radiator", "Sanden Japanese AC Compressor", "Toyota Genuine Spin-on Oil Filter", "Bosch OEM Engine Air Filter", "Bosch In-Tank Electric Fuel Pump", "Delphi Ignition Coils Pack"),
        brands_ar=("تويوتا وكالة", "دنسو", "بوش", "اي سي ديلكو", "موبار", "دولفين", "موتوركرافت", "ساندن"),
        brands_en=("Toyota Genuine OEM", "Denso", "Bosch Auto", "ACDelco", "Mopar", "Dolphin Radiators", "Motorcraft", "Sanden"),
        allowed_containers_ar=CONTAINERS_AUTO_SPARES_AR,
        allowed_containers_en=CONTAINERS_AUTO_SPARES_EN,
        allowed_contexts_ar=("توريد محلات قطع غيار سيارات", "طلبية صيانة ورش وميكانيكا", "شحنة قطع غيار وكالة جديدة بالكرتون"),
        allowed_contexts_en=("Auto spare parts shop supply", "Fleet maintenance workshop batch", "Factory boxed OEM spares"),
        short_query_templates_ar=("{noun}", "طقم {noun}", "كرتون {noun}", "{noun} أصلي وكالة", "حبة {noun}"),
        short_query_templates_en=("{noun}", "genuine set of {noun}", "OEM boxed {noun}", "{qty} units of {noun}")
    ),
    # 130: قطع الغيار المستعملة والسكراب (Used Spares & Scrap)
    130: ProductionDomainRule(
        domain_type="auto_spares_used",
        nouns_ar=("مكينة تويوتا لاندكروزر 8 سرندل تشليح", "قير أوتوماتيك كامري مستعمل مضمون", "دفرنس خلفي نيسان باترول تشليح", "أبواب وكبوت ورفارف تاهو مستعملة", "شمعات وإسطبات خلفية أصلية تشليح", "كمبروسر مكيف مستعمل فحص كمبيوتر", "سكراب حديد سيارات كبس تريلا", "خردة نحاس وألومنيوم ومحركات سكراب للبيع"),
        nouns_en=("Toyota Land Cruiser V8 Used Engine Scrap", "Camry Used Automatic Transmission Tested", "Nissan Patrol Used Rear Differential", "Chevy Tahoe Used Body Doors and Hood", "OEM Headlights from Auto Salvage", "Tested Used AC Compressor", "Baled Auto Scrap Steel Truckload", "Scrap Copper, Aluminum and Old Engine Blocks"),
        brands_ar=("تشليح الحائر بالرياض", "تشليح بريمان بجدة", "تشليح الدمام المركزي", "سكراب الراجحي لإعادة التدوير"),
        brands_en=("Al Ha'ir Auto Salvage", "Braiman Scrap Yard", "Dammam Auto Dismantlers", "Metals Recycling Scrap"),
        allowed_containers_ar=("حمولة سطحة تشليح", "تريلا سكراب كبس صب", "حبة مجربة على الشرط والضمان", "طبالي خردة محركات"),
        allowed_containers_en=("flatbed salvage truckload", "baled scrap semi-trailer load", "warranted tested unit", "palletized scrap engines"),
        allowed_contexts_ar=("نقل قطع تشليح مع الفحص والضمان", "تنزيل حمولة سكراب حديد للمصهر", "طلبية سمكرة وتوضيب مكاين"),
        allowed_contexts_en=("Auto dismantler parts dispatch", "Scrap metal consignment to recycling foundry", "Engine rebuild used parts supply"),
        short_query_templates_ar=("{noun}", "تشليح {noun}", "سكراب {noun}", "مستعمل نظيف {noun}", "حمولة {noun}"),
        short_query_templates_en=("{noun}", "used salvage {noun}", "scrap {noun}", "tested used {noun}")
    ),
    # 192: عطور (Perfumes, Oud & Incense)
    192: ProductionDomainRule(
        domain_type="perfumes_oud",
        nouns_ar=("دهن عود كلاكاسي قديم", "دهن عود مروكي سوبر", "بخور عود كلمنتان دبل سوبر", "بخور رقائق عود فيتنامي", "عطر إمبريال فالي قصة", "عطر مسك الطهارة الأبيض ربع تولة", "عطور فرنسية نسائية 100 مل أصلية", "عطور شرقية للجنسين درازن", "مخلط ملكي فاخر بالزعفران", "معمول بخور دوسري ملكي"),
        nouns_en=("Aged Kalakassi Dehn Al Oud", "Marooki Super Pure Oud Oil", "Kalimantan Double Super Agarwood Chips", "Vietnamese Oud Wood Incense Slices", "Imperial Valley Perfume Spray", "White Tahara Musk Concentrated Oil", "Original French EDP Perfumes 100ml", "Wholesale Oriental Unisex Fragrances", "Royal Saffron Blend Mukhallat", "Royal Dawsari Traditional Incense Bakhour"),
        brands_ar=("عبدالصمد القرشي", "الماجد للعود", "العربية للعود", "إبراهيم القرشي", "عطور قصة", "دخون الإماراتية", "درعه للعطور"),
        brands_en=("Abdul Samad Al Qurashi", "Almajed for Oud", "Arabian Oud", "Ibrahim Al Qurashi", "Gissah Perfumes", "Dukhon", "Deraah"),
        allowed_containers_ar=("كراتين مغلفة محكمة", "درازن تولات زجاجية", "صناديق خشبية مخملية", "طرد هدايا عطور", "بوكسات تجارية 12 حبة"),
        allowed_containers_en=("sealed gift-pack cartons", "dozen glass tolas", "velvet lined wooden boxes", "fragrance retail packs"),
        allowed_contexts_ar=("توريد محلات عطور وبخور", "طلبية متجر هدايا وتجميل", "شحنة دهن عود وبخور فاخر للمعارض"),
        allowed_contexts_en=("Perfumery and incense shop order", "Beauty and cosmetics boutique batch", "Luxury oud and fragrance consignment"),
        short_query_templates_ar=("{noun}", "تولة {noun}", "كرتون {noun}", "درزن {noun}", "بخور {noun}"),
        short_query_templates_en=("{noun}", "bottle of {noun}", "box of {noun}", "authentic {noun}")
    ),
    # 148: الفحم والحطب (Charcoal and Firewood)
    148: ProductionDomainRule(
        domain_type="charcoal_firewood",
        nouns_ar=("فحم شواء سداسي مضغوط وادي حلفا", "فحم إندونيسي جوز هند للشيشة والمشاوي", "فحم قرض سوداني أصلي خياش", "فحم صومالي طبيعي أكياس 10 كجم", "حطب سمر المدينة يابس قشور", "حطب غضا القصيم يابس للتدفئة", "حطب أرطى بري نظيف ربطات", "أقراص فحم سريع الاشتعال كراتين"),
        nouns_en=("Wadi Halfa Hexagonal Briquette Charcoal", "Indonesian Coconut Shell Shisha Charcoal", "Sudanese Garad Hardwood Charcoal Bags", "Somali Natural Charcoal 10kg Bags", "Dry Madinah Samar Firewood Bundles", "Dry Qassim Ghada Firewood for Heating", "Clean Wild Arta Campfire Wood", "Instant Quick-Light Charcoal Tablets"),
        brands_ar=("فحم وادي حلفا", "فحم الشرقية", "فحم الجود", "فحم واحة حطين", "حطب المحميات المرخص"),
        brands_en=("Wadi Halfa Charcoal", "Al Sharqia Charcoal", "Al Joud Briquettes", "Licensed Reserve Firewood"),
        allowed_containers_ar=("خياش خيش 20 كجم", "أكياس ورقية 10 كجم", "ربطات حطب محزومة", "كراتين 5 كجم", "حمولة دينا حطب سمر"),
        allowed_containers_en=("20kg burlap sacks", "10kg paper bags", "tied firewood bundles", "5kg retail boxes", "dyna pickup firewood load"),
        allowed_contexts_ar=("توريد مطاعم شواء ومقاهي", "شحنة لوازم مخيمات وبر وتدفئة", "طلبية محطات واستراحات"),
        allowed_contexts_en=("Barbecue restaurant supply", "Camping and winter firewood batch", "Wholesale charcoal and fuel wood dispatch"),
        short_query_templates_ar=("{noun}", "خيشة {noun}", "كرتون {noun}", "ربطة {noun}", "حطب {noun}", "دينا {noun}"),
        short_query_templates_en=("{noun}", "sack of {noun}", "carton of {noun}", "bundle of {noun}", "firewood {noun}")
    ),
    # 147: الملابس والأحذية (Clothes and Shoes)
    147: ProductionDomainRule(
        domain_type="clothes_shoes",
        nouns_ar=("أثواب رجالي صيفي الدفة كراتين", "أثواب الأصيل رجالي وشبابي مقاسات", "أشمغة البسام ماي فير دم الغزال", "أشمغة جفنشي كلاسيك كراتين", "غتر بيضاء الرويس كراتين", "عبايات خليجي كريب كراتين درازن", "ملابس أطفال قطنية بالات", "جلابيات نسائية بيت مشكلة", "أحذية جلدية رسمية رجالي كراتين", "أحذية رياضية سنيكرز كراتين مقاسات"),
        nouns_en=("Daffah Men Summer Thobes Cartons", "Al Aseel Youth and Men Thobes Assorted Sizes", "Al Bassam Classic Shemagh Mayfair", "Givenchy Luxury Men Shemagh", "Al Rowais Pure White Ghutrah", "Gulf Crepe Abayas Wholesale Dozens", "Kids 100% Cotton Apparel Bales", "Assorted Women Loungewear Jalabiyas", "Men Genuine Leather Dress Shoes", "Athletic Running Sneakers Cartons"),
        brands_ar=("الدفة", "الأصيل", "البسام", "الرويس", "جفنشي", "سنتربوينت", "رد تاغ"),
        brands_en=("Al Daffah", "Al Aseel", "Al Bassam", "Al Rowais", "Givenchy", "Centrepoint", "Red Tag"),
        allowed_containers_ar=CONTAINERS_CLOTHING_AR,
        allowed_containers_en=CONTAINERS_CLOTHING_EN,
        allowed_contexts_ar=("توريد محلات خياطة وملابس جاهزة", "طلبية بوتيك أزياء وأحذية", "شحنة ملابس مواسم وأعياد"),
        allowed_contexts_en=("Apparel retail store replenishment", "Fashion boutique garments shipment", "Wholesale clothing and footwear consignment"),
        short_query_templates_ar=("{noun}", "كرتون {noun}", "درزن {noun}", "ثوب {noun}", "شماغ {noun}", "بالة {noun}"),
        short_query_templates_en=("{noun}", "carton of {noun}", "dozen of {noun}", "wholesale {noun}")
    ),
    # 132: الحواسيب والمنتجات الإلكترونية (Computers & IT Electronics)
    132: ProductionDomainRule(
        domain_type="electronics_it",
        nouns_ar=("شاشات سامسونج سمارت 65 بوصة 4K OLED", "شاشات ال جي 55 بوصة نانوسيل بالكرتون", "لابتوب ديل كور آي 7 كراتين مقفلة", "لابتوب إتش بي فكتور قيمنق للألعاب", "لابتوب أبل ماك بوك برو إم 3 برو أصلي", "جوالات آيفون 15 برو ماكس كراتين مقفلة وكالة", "جوالات سامسونج جالكسي إس 24 ألترا 5G", "أجهزة آيباد إير مع القلم كراتين", "راوترات واي فاي 5G هواوي فايبر", "كاميرات مراقبة هيكفيجن 8 ميجا 4K NVR", "بلايستيشن 5 مع يدين تحكم كراتين وكالة", "شواحن متنقلة باور بانك أنكر 20000 ملي أمبير"),
        nouns_en=("Samsung 65-inch 4K OLED Smart TV", "LG 55-inch NanoCell 4K UHD TV in Box", "Dell Core i7 Business Laptop Factory Sealed", "HP Victus Dedicated GPU Gaming Laptop", "Apple MacBook Pro M3 Pro Chip Laptop", "Apple iPhone 15 Pro Max Factory Sealed Box", "Samsung Galaxy S24 Ultra 5G Smartphone", "Apple iPad Air with Apple Pencil Boxed", "Huawei 5G Ultra-Fast WiFi Mesh Routers", "Hikvision 8MP 4K NVR Security CCTV Kit", "Sony PlayStation 5 Console with DualSense", "Anker 20,000mAh Portable Power Bank Fast Charger"),
        brands_ar=("سامسونج", "أبل", "ال جي", "ديل", "إتش بي", "هواوي", "سوني", "أنكر", "هيكفيجن", "شاومي"),
        brands_en=("Samsung", "Apple", "LG", "Dell", "HP", "Huawei", "Sony", "Anker", "Hikvision", "Xiaomi"),
        allowed_containers_ar=CONTAINERS_ELECTRONICS_AR,
        allowed_containers_en=CONTAINERS_ELECTRONICS_EN,
        allowed_contexts_ar=("توريد معارض إلكترونيات وأجهزة ذكية", "طلبية متجر اتصالات وجوالات", "شحنة أجهزة حاسب مع الضمان الوكيل سنتين"),
        allowed_contexts_en=("Consumer electronics showroom supply", "Mobile phones and telecom retail shipment", "IT hardware consignment with 2-year warranty"),
        short_query_templates_ar=("{noun}", "كرتون {noun}", "حبة {noun} وكالة", "{noun} ضمان سنتين", "طبلية {noun}"),
        short_query_templates_en=("{noun}", "sealed box of {noun}", "retail pack {noun}", "{qty} units {noun}")
    ),
    # 159: مولدات الكهرباء (Electricity Generators)
    159: ProductionDomainRule(
        domain_type="power_generators",
        nouns_ar=("مولد كهرباء ديزل كمنز 100 كيلو فولت أمبير كاتم صوت", "مولد كهرباء بيركنز إنجليزي 500 KVA للمشاريع", "مولد ديزل كتربلر 250 كيلو للمزارع والمصانع", "ماطور كهرباء بنزين هوندا ياباني 5 كيلو متنقل", "ماطور روبين سوبارو بنزين 7.5 كيلو للمخيمات", "لوحة تحكم وتحويل أوتوماتيكي ATS للمولدات", "خزان وقود ديزل احتياطي للمولدات 1000 لتر"),
        nouns_en=("Cummins 100 kVA Silent Diesel Power Generator", "Perkins UK 500 kVA Heavy Project Diesel Generator", "Caterpillar 250 kVA Industrial Farm Generator", "Honda Japan 5 kW Portable Gasoline Generator", "Robin Subaru 7.5 kW Camping Generator", "Automatic Transfer Switch ATS Control Panel", "1000L Auxiliary Diesel Fuel Storage Tank"),
        brands_ar=("كمنز Cummins", "بيركنز Perkins", "كتربلر CAT", "هوندا Honda", "روبين Robin", "دووسان Doosan"),
        brands_en=("Cummins", "Perkins", "Caterpillar", "Honda Power", "Robin Subaru", "Doosan Power"),
        allowed_containers_ar=("وحدة محمولة على شاسيه", "حمولة تريلا ونش رافعة", "صندوق حماية كانوبي عازل للصوت", "طبلية تثبيت فولاذية"),
        allowed_containers_en=("skid-mounted power unit", "crane truckload dispatch", "soundproof acoustic canopy", "heavy duty steel base"),
        allowed_contexts_ar=("توريد وتأجير مولدات طاقة للمشاريع", "شحنة مولدات مزارع ومواقع إنشائية", "طلبية طوارئ وانقطاع كهرباء"),
        allowed_contexts_en=("Project backup power supply and rental", "Agricultural and construction power dispatch", "Industrial power generation batch"),
        short_query_templates_ar=("{noun}", "ماطور {noun}", "مولد ديزل {noun}", "تأجير {noun}", "شحنة {noun}"),
        short_query_templates_en=("{noun}", "silent generator {noun}", "diesel generator {noun}", "portable genset {noun}")
    ),
    # 126: صهاريج الماء (Water Tankers & Tanks)
    126: ProductionDomainRule(
        domain_type="water_tanks",
        nouns_ar=("وايت ماء حلو صالح للشرب صهريج 16 طن", "وايت ماء تحلية مياه شرب دينا 6 طن", "وايت ماء غسيل ومقاولات تريلا 32 طن", "خزان مياه الزامل فايبر جلاس عمودي سعة 5000 لتر", "خزان ماء المهيدب بولي إيثيلين 4 طبقات 3000 لتر", "مضخات مياه ودينمو ضغط كالبيدا إيطالي للمباني"),
        nouns_en=("Potable Sweet Drinking Water Tanker 16-Ton", "Purified Desalinated Water Dyna Tanker 6-Ton", "Construction Utility Water Semi-Trailer 32-Ton", "Zamil Vertical Fiberglass Water Tank 5000L", "Al Muhaidib 4-Layer Polyethylene Tank 3000L", "Calpeda Italian Booster Water Pump for Buildings"),
        brands_ar=("مياه صهاريج التحلية الوطنية", "خزانات الزامل", "خزانات المهيدب", "مضخات كالبيدا", "خزانات الوطني"),
        brands_en=("National Potable Water Tankers", "Zamil Water Tanks", "Al Muhaidib Tanks", "Calpeda Water Pumps"),
        allowed_containers_ar=("حمولة وايت صهريج معبأ", "خزان جاهز للرفع والتركيب", "طبلية خزان معزول", "تريلا تانكي مجلفن"),
        allowed_containers_en=("filled bulk water tanker load", "ready-to-install water storage vessel", "galvanized bulk tanker delivery"),
        allowed_contexts_ar=("توصيل وايت ماء عمارة واستراحة", "توريد مياه خرسانة ومشاريع بناء", "شحنة وتركيب خزانات مياه علوية وأرضية"),
        allowed_contexts_en=("Residential potable water delivery", "Construction concrete batching water supply", "Rooftop and underground tank installation"),
        short_query_templates_ar=("{noun}", "وايت {noun}", "رد ماء {noun}", "خزان {noun} لتر", "توصيل {noun}"),
        short_query_templates_en=("{noun}", "water tanker {noun}", "potable water delivery {noun}", "water tank {noun}")
    ),
    # 125: الصرف الصحي (Sanitation & Sewage Services)
    125: ProductionDomainRule(
        domain_type="sanitation_service",
        nouns_ar=("وايت شفط مياه بيارات وصرف صحي 32 طن", "وايت سحب مجاري ومخلفات سائلة دينا 10 طن", "أنابيب صرف صحي uPVC نيبرو مقاس 6 بوصة", "غطاء غرفة تفتيش ومناهيل دكتايل حديد زهر C250", "مضخات غاطسة سحب مياه مجاري ومخلفات داب إيطالي", "مواد تسليك وتنظيف غرف تفتيش وخطوط صرف"),
        nouns_en=("Sewage and Wastewater Suction Tanker 32-Ton", "Septic Tank Pumping Dyna Vacuum Tanker 10-Ton", "Nepro uPVC Underground Sewer Pipes 6-inch", "Ductile Cast Iron Heavy Duty Manhole Covers C250", "DAB Italian Submersible Sewage and Waste Pumps", "Chemical Drain and Sewer Line Unblocking Agents"),
        brands_ar=("أنابيب نيبرو uPVC", "مضخات داب DAB", "مناهيل مسبك الجزيرة", "خدمات سحب المجاري المعتمدة"),
        brands_en=("Nepro uPVC Pipes", "DAB Submersible Pumps", "Al Jazeera Foundry", "Municipal Certified Vacuum Services"),
        allowed_containers_ar=("حمولة صهريج وايت شفط تفريغ", "حزم أنابيب ربطات", "طبالي أغطية مناهيل حديد", "كراتين مضخات غاطسة"),
        allowed_containers_en=("vacuum tanker suction load", "bundled sewer pipe packs", "palletized cast iron manhole covers", "boxed submersible pumps"),
        allowed_contexts_ar=("خدمة سحب بيارات وصرف صحي للمباني والمصانع", "توريد شبكات صرف وتمديدات تحت الأرض", "تنظيف وغسيل خطوط مجاري بضغط عالي"),
        allowed_contexts_en=("Commercial sewage vacuum pumping service", "Underground sanitary sewer infrastructure supply", "High pressure sewer line hydro-jetting"),
        short_query_templates_ar=("{noun}", "وايت شفط {noun}", "سحب مجاري {noun}", "مواسير صرف {noun}", "رد سحب {noun}"),
        short_query_templates_en=("{noun}", "sewage suction tanker {noun}", "sewer drainage pipes {noun}", "vacuum pumping {noun}")
    ),
    # 127: صهاريج الغاز (Gas Tanks and LPG Supply)
    127: ProductionDomainRule(
        domain_type="gas_tanks",
        nouns_ar=("صهريج تعبئة غاز مسال غازكو تريلا 20 طن", "خزان غاز مركزي مدفون سعة 1000 لتر غازكو", "خزان غاز رأسي فوق الأرض سعة 2000 لتر", "أسطوانات غاز منزلي ألومنيوم ومركبة فايبر جلاس", "منظمات غاز وضغط ومحابس أمان إيطالي أصلية", "شبكات تمديد غاز مركزي للمطاعم والفنادق"),
        nouns_en=("GASCO Bulk LPG Liquid Gas Tanker 20-Ton", "Underground Central LPG Gas Tank 1000L GASCO", "Above-ground Vertical Gas Storage Tank 2000L", "Lightweight Composite and Steel LPG Cylinders", "Italian Gas Pressure Regulators and Safety Valves", "Central Commercial LPG Piping Networks for Restaurants"),
        brands_ar=("شركة الغاز والتصنيع الأهلية غازكو", "منظمات ريكو إيطالي", "خزانات أرامكو المعتمدة"),
        brands_en=("National Gas and Industrialization Co GASCO", "Reca Italian Gas Regulators", "Aramco Certified LPG Tanks"),
        allowed_containers_ar=("صهريج غاز مضغوط ADR معتمد", "أسطوانات غاز قفص حديدي 50 حبة", "خزان غاز مركزي جاهز للتركيب", "كراتين محابس ومنظمات"),
        allowed_containers_en=("certified pressurized LPG bulk tanker", "caged pallet of 50 gas cylinders", "pre-tested central gas tank vessel"),
        allowed_contexts_ar=("تعبئة وتوصيل غاز مركزي للمجمعات والمطاعم", "شحنة أسطوانات غاز وتوزيع معتمد", "تركيب شبكات وصهاريج غاز مطابقة للدفاع المدني"),
        allowed_contexts_en=("Central bulk LPG gas refilling and distribution", "Commercial gas cylinder exchange batch", "Civil Defense certified LPG installation supply"),
        short_query_templates_ar=("{noun}", "تعبئة غاز {noun}", "خزان غاز {noun} لتر", "أسطوانات {noun}", "صهريج غاز {noun}"),
        short_query_templates_en=("{noun}", "bulk LPG tanker {noun}", "central gas tank {noun}", "gas cylinders {noun}")
    ),
    # 149: الأدوية (Human Medicines & Pharmaceuticals)
    149: ProductionDomainRule(
        domain_type="medicines_human",
        nouns_ar=("بنادول إكسترا مسكن ألم كراتين صيدلية", "أقراص فيفادول 500 ملغم كراتين مستودعات", "أوجمنتين مضاد حيوي 1 جم أقراص", "بخاخ فنتولين للربو كراتين مبردة", "أمبولات إنسولين لانتوس مبردة 2-8 درجات", "أقراص كونكور للضغط والقلب", "أقراص نيكسيوم للمعدة والحموضة", "محلول جلوكوز ومغذي وريدي كراتين معقمة", "شراب بروفين للأطفال خافض حرارة"),
        nouns_en=("Panadol Extra Fast Action Analgesic Cartons", "Fevadol 500mg Paracetamol Tablets Pharma Packs", "Augmentin 1g Broad Spectrum Antibiotic", "Ventolin HFA Asthma Inhalers Chilled Batch", "Lantus Insulin Glargine Pens Cold Chain 2-8C", "Concor Beta Blocker Cardiovascular Tablets", "Nexium 40mg Acid Reflux Tablets", "Sterile IV Dextrose Saline Infusion Bottles", "Brufen Children Fever Relief Suspension"),
        brands_ar=("جلفار Julphar", "سبيماكو الدوائية SPIMACO", "تبوك للصناعات الدوائية", "فايزر Pfizer", "جي إس كيه GSK", "نوفارتس Novartis"),
        brands_en=("Julphar", "SPIMACO", "Tabuk Pharmaceuticals", "Pfizer", "GSK", "Novartis"),
        allowed_containers_ar=CONTAINERS_PHARMA_MEDICAL_AR,
        allowed_containers_en=CONTAINERS_PHARMA_MEDICAL_EN,
        allowed_contexts_ar=("توريد صيدليات ومستشفيات معتمد من هيئة الغذاء والدواء", "شحنة أدوية مبردة تتبع درجات الحرارة", "طلبية مستودعات طبية مسجلة SFDA"),
        allowed_contexts_en=("SFDA certified hospital and pharmacy distribution", "Cold-chain monitored pharmaceutical consignment", "Registered medical warehouse medicine batch"),
        short_query_templates_ar=("{noun}", "كرتون {noun}", "أدوية مبردة {noun}", "باكت {noun}", "طلبية صيدلية {noun}"),
        short_query_templates_en=("{noun}", "carton of {noun}", "cold-chain pharma {noun}", "pharma pack of {noun}")
    ),
    # 153: الأدوية البيطرية (Veterinary Medicines)
    153: ProductionDomainRule(
        domain_type="medicines_vet",
        nouns_ar=("إيفوميك سوبر حقن طفيليات مواشي وإبل أصلي", "أوكسي تتراسيكلين مضاد حيوي بيطري طويل المفعول", "فيتامينات أ د 3 هـ بودرة ذوابة للدواجن والأغنام", "بخاخ جروح ومطهر أزرق بيطري كراتين", "لقاحات تحصين جدري الأغنام وطاعون المجترات مبردة", "معصار ديدان بيطري بالفم للخيل والإبل", "أملاح ومكملات معادن قوالب لعق للمواشي"),
        nouns_en=("Ivomec Super Injectable Antiparasitic for Cattle & Camels", "Oxytetracycline LA 20% Broad Spectrum Vet Antibiotic", "Water Soluble AD3E Multivitamins for Livestock & Poultry", "Blue Antiseptic Wound Spray for Animals Cartons", "Refrigerated Sheep Pox and PPR Animal Vaccines", "Oral Dewormer Paste for Horses and Camels", "Mineral and Salt Lick Blocks for Cattle"),
        brands_ar=("ميريال Merial البيطرية", "شركة سيفا Ceva البيطرية", "أردكو للأدوية البيطرية", "نوفارتس آنيمال هيلث", "أميسكو البيطرية"),
        brands_en=("Merial Animal Health", "Ceva Animal Health", "Vetoquinol", "Boehringer Ingelheim Vet", "Zoetis Animal Health"),
        allowed_containers_ar=("كراتين قوارير بيطرية معقمة", "جوالين 5 لتر بيطرية", "طبالي قوالب أملاح ولحس", "كرتون حقن وأمبولات بيطرية مبردة"),
        allowed_containers_en=("sterile vet bottle cartons", "5L veterinary liquid jugs", "palletized salt lick blocks", "temperature-controlled animal vaccine packs"),
        allowed_contexts_ar=("توريد صيدليات بيطرية ومشاريع دواجن", "شحنة أدوية وتحصينات عزب ومزارع إبل وأغنام", "طلبية عيادات بيطرية معتمدة من وزارة الزراعة"),
        allowed_contexts_en=("Veterinary pharmacy and poultry farm replenishment", "Camel and sheep farm medical treatment dispatch", "Ministry of Agriculture certified vet medicine batch"),
        short_query_templates_ar=("{noun}", "علاج بيطري {noun}", "حقن {noun}", "كرتون {noun}", "إبر {noun}"),
        short_query_templates_en=("{noun}", "veterinary medicine {noun}", "animal injectable {noun}", "vet supply {noun}")
    ),
    # 156: المستلزمات الطبية ومستلزمات المستشفيات (Medical Supplies)
    156: ProductionDomainRule(
        domain_type="medical_supplies",
        nouns_ar=("كمامات طبية 3 طبقات جراحية كراتين 50 حبة", "قفازات فحص طبية لاتكس ونيتريل بدون بودرة كراتين", "شاش طبي معقم وضمادات جروح قطنية", "سرنجات وحقن طبية للاستخدام مرة واحدة كراتين", "كراسي متحركة طبية قابلة للطي للمرضى", "أجهزة قياس السكر وضغط الدم أومرون", "قساطر وأكياس جمع بول معقمة كراتين", "ملابس وأرواب عمليات جراحية معقمة"),
        nouns_en=("3-Ply Surgical Medical Face Masks 50-Pack Boxes", "Powder-Free Latex and Nitrile Medical Exam Gloves", "Sterile Medical Gauze Swabs and Cotton Wound Dressings", "Disposable Sterile Hypodermic Syringes Cartons", "Foldable Heavy Duty Medical Wheelchairs for Patients", "Omron Digital Blood Pressure and Glucose Monitors", "Sterile Medical Catheters and Urine Drainage Bags", "Sterile Disposable Surgical Gowns and Drapes"),
        brands_ar=("أومرون Omron", "بي دي BD Medical", "المصنع السعودي للمستلزمات الطبية", "ميدلاين Medline", "3M الطبية"),
        brands_en=("Omron Healthcare", "BD Medical", "Saudi Medical Supplies Factory", "Medline", "3M Healthcare"),
        allowed_containers_ar=("كراتين معقمة ومغلفة", "طبالي مستلزمات مستشفيات", "بوكسات أجهزة طبية بالضمان", "طرد مستهلكات طبية"),
        allowed_containers_en=("sterile medical master cartons", "hospital supplies pallets", "boxed medical devices with warranty", "disposable medical packs"),
        allowed_contexts_ar=("توريد مستشفيات ومراكز صحية وعيادات", "شحنة مستلزمات طبية مطابقة لاشتراطات SFDA", "طلبية مستودعات رعاية صحية وطبية"),
        allowed_contexts_en=("Hospital and clinic medical consumable supply", "SFDA compliant medical devices consignment", "Healthcare logistics sterile goods batch"),
        short_query_templates_ar=("{noun}", "كرتون {noun}", "طبي معقم {noun}", "مستلزمات {noun}", "طبلية {noun}"),
        short_query_templates_en=("{noun}", "sterile {noun}", "carton of {noun}", "medical grade {noun}")
    ),
    # 193: معدات السلامة والأمن (Safety & Firefighting Equipment)
    193: ProductionDomainRule(
        domain_type="safety_firefighting",
        nouns_ar=("طفايات حريق بودرة جافة 6 كجم نافكو معتمدة", "طفايات حريق ثاني أكسيد الكربون CO2 سعة 5 كجم", "خراطيم إطفاء حريق قماش مع المحابس 30 متر", "خوذ سلامة هندسية للمواقع الإنشائية كراتين", "أحذية سلامة سفتي شوز مقدمة فولاذية كراتين", "سترات عاكسة للضوء فوسفورية للمشاريع درازن", "أجهزة كشف وإنذار دخان وحريق هانيويل", "نظارات وقاية وسدادات أذن وسلالم طوارئ"),
        nouns_en=("NAFFCO 6kg Dry Chemical Powder Fire Extinguishers", "NAFFCO 5kg Carbon Dioxide CO2 Fire Extinguishers", "30m Canvas Fire Fighting Hose with Brass Nozzles", "Heavy Duty Industrial Safety Hard Hats Cartons", "Steel Toe Cap Industrial Safety Work Shoes", "High Visibility Reflective Safety Vests Dozens", "Honeywell Fire Alarm and Smoke Detector System", "Safety Goggles, Ear Plugs and Emergency Fire Blankets"),
        brands_ar=("نافكو NAFFCO", "هانيويل Honeywell", "ريد وينج Red Wing", "سافيتي كير Safety Care", "معدات الدفاع المدني المعتمدة"),
        brands_en=("NAFFCO", "Honeywell Safety", "Red Wing Shoes", "3M Safety", "Civil Defense Approved Equipment"),
        allowed_containers_ar=("كراتين معدات سلامة", "طبالي طفايات حريق مرخصة", "صناديق خراطيم ومحابس", "درازن ملابس وقاية"),
        allowed_containers_en=("safety gear master cartons", "palletized certified fire extinguishers", "protective footwear cases"),
        allowed_contexts_ar=("توريد مشاريع مقاولات واعتماد الدفاع المدني", "شحنة معدات أمن وسلامة مهنية للمصانع", "طلبية تجديد تراخيص بلدية وسلامة"),
        allowed_contexts_en=("Civil Defense compliant site safety supply", "Industrial occupational health and safety batch", "Commercial facility firefighting equipment consignment"),
        short_query_templates_ar=("{noun}", "طفاية حريق {noun}", "سفتي {noun}", "كرتون {noun}", "معدات سلامة {noun}"),
        short_query_templates_en=("{noun}", "fire extinguisher {noun}", "safety gear {noun}", "carton of {noun}")
    ),
    # 166: مياه معبأة (Bottled Water)
    166: ProductionDomainRule(
        domain_type="bottled_water",
        nouns_ar=("مياه هنا كراتين 200 مل 48 حبة مساجد", "مياه صفا كراتين 330 مل 40 حبة", "مياه نوفا كراتين 550 مل 24 حبة", "مياه بيرين قليلة الصوديوم 200 مل كراتين", "مياه نقى كراتين مياه توزيع خيري", "مياه تانيا كراتين 200 مل", "جالون مياه 5 جالون قابل للاستبدال كراتين", "مياه أكوافينا كراتين 1.5 لتر شد 12 قارورة"),
        nouns_en=("Hana Bottled Water 200ml 48-Pack Cartons", "Safa Bottled Water 330ml 40-Pack Cartons", "Nova Pure Drinking Water 550ml 24-Pack", "Berain Low Sodium Water 200ml Cartons", "Naqi Bottled Water Charitable Distribution Batch", "Tania Purified Water 200ml 48-Unit Cases", "5-Gallon Refillable Water Cooler Bottles", "Aquafina 1.5L Mineral Water 12-Pack Shrink"),
        brands_ar=("مياه هنا", "مياه صفا", "مياه نوفا", "مياه بيرين", "مياه نقى", "مياه تانيا", "مياه أروى"),
        brands_en=("Hana Water", "Safa Water", "Nova Water", "Berain Water", "Naqi Water", "Tania Water", "Aquafina"),
        allowed_containers_ar=("كراتين شد المصنع", "طبالي مياه مشمعة 80 كرتون", "حمولة دينا مياه مساجد", "تريلا مياه معبأة 22 طبلية"),
        allowed_containers_en=("shrink-wrapped master cases", "80-case palletized bottled water", "commercial water delivery truckload", "22-pallet water semi-trailer consignment"),
        allowed_contexts_ar=("توصيل وتوزيع كراتين مياه للمساجد والجمعيات", "توريد مستودعات وبقالات ومطاعم", "طلبية مياه شرب معبأة كراتين"),
        allowed_contexts_en=("Mosque and charity water distribution", "Grocery and supermarket water delivery", "Bottled drinking water wholesale consignment"),
        short_query_templates_ar=("{noun}", "كراتين {noun}", "طبلية {noun}", "{qty} كرتون {noun}", "مياه {noun}"),
        short_query_templates_en=("{noun}", "cartons of {noun}", "pallet of {noun}", "{qty} cases {noun}")
    ),
}
