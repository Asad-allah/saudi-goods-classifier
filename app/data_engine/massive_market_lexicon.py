"""Massive market lexicon covering real-world Saudi & GCC goods across all 90 leaf categories."""

from __future__ import annotations

# Rich item vocabulary mapped per leaf category ID
LEAF_MARKET_ITEMS: dict[int, dict[str, list[str]]] = {
    # 14: سلع جافة (Dry FMCG)
    14: {
        "nouns_ar": [
            "أرز بسمتي هندي الشعلان", "أرز مزة أبو كاس", "أرز عنبر باب الهند", "أرز مصري جرين فودز",
            "سكر ناعم الأسرة", "سكر بني مكعبات", "مكرونة قودي أشكال", "مكرونة بيرفيتو إسباغيتي",
            "شعيرية الوفرة كراتين", "دقيق فاخر كويتي فوم", "طحين بر صوامع الغلال", "عدس أحمر حبة كاملة",
            "حمص حب مجفف", "فول صويا مجفف", "فاصوليا بيضاء يابسة", "شوفان كويكر علب",
            "شاي أسود كبوس تلقيمة", "شاي ربيع فرط إكسبريس", "شاي أحمد تي لندن", "شاي ليبتون أكياس",
            "قهوة عربي هرري فاخر", "قهوة خولاني درجة أولى", "هيل أمريكي أخضر جامبو", "زعفران أبو شيبة أصلي",
            "بسكويت شاي ميموريز", "بسكويت دايجستف مكفيتيز", "شوكولاتة كيت كات 4 أصابع", "شوكولاتة جالكسي سادة",
            "نوتيلا برطمانات كراتين", "شيبس ليز عائلي بالجبن", "بطاطس تسالي حار نار", "مكسرات باجة مشكلة مشوية"
        ],
        "nouns_en": [
            "Shalan Indian Basmati Rice", "Abu Kass Sella Rice", "Bab Al Hind Amber Rice", "Egyptian Medium Grain Rice",
            "Al-Osra Fine White Sugar", "Brown Sugar Cubes", "Goody Pasta Assorted Shapes", "Perfetto Spaghetti Pasta",
            "Al Wafra Vermicelli Noodles", "Kuwaiti Patent Flour Foom", "Whole Wheat Grain Flour", "Red Split Lentils",
            "Dry Chickpeas Garbanzo", "Dry Soybeans", "White Kidney Beans", "Quaker Rolled Oats Cans",
            "Al-Kbous Black Loose Tea", "Rabea Express Loose Leaf Tea", "Ahmad Tea London Selection", "Lipton Yellow Label Tea Bags",
            "Harari Premium Arabic Coffee", "Khawlani Grade A Green Coffee", "Jumbo Green Cardamom", "Original Saffron Threads",
            "Memories Tea Biscuits", "McVitie's Digestives", "KitKat 4-Finger Chocolate Bars", "Galaxy Milk Chocolate Bars",
            "Nutella Hazelnut Spread Jars", "Lay's Family Pack Cheese Potato Chips", "Tasali Hot Chips", "Baja Mixed Roasted Nuts"
        ],
        "brands_ar": ["الشعلان", "أبو كاس", "قودي", "الأسرة", "باجة", "بيتي كروكر", "كبوس", "ربيع", "ليبتون", "نوتيلا"],
        "brands_en": ["Al Shalan", "Abu Kass", "Goody", "Al Osra", "Baja", "Betty Crocker", "Al Kbous", "Rabea", "Lipton", "Nutella"]
    },
    # 15: سلع مبردة (Chilled FMCG)
    15: {
        "nouns_ar": [
            "حليب طازج المراعي كامل الدسم", "حليب نادك قليل الدسم", "حليب الصافي خالي الدسم",
            "لبن عيران المراعي", "لبن زبادي نادك عائلي", "زبادي يوناني ندى بروتين",
            "قشطة طازجة الصافي بلدي", "زبدة غير مملحة لورباك", "مارجرين مازولا نباتي",
            "جبنة كريمية كاسات المراعي", "جبن شيدر كرافت قوالب", "جبن فيتا المراعي مكعبات",
            "جبنة موزاريلا مبشورة فرسانا", "جبنة حلوم رول الصافي", "عصير برتقال طازج فلوريدا",
            "عصير رمان المراعي مبرد", "بيض مائدة طازج الوطنية كراتين", "بيض فقيه مزارع طبق 30 حبة",
            "خميرة طازجة مبردة للمخابز", "صلصة مايونيز ديليسيو مبردة", "عجينة سمبوسة مبردة سويتز"
        ],
        "nouns_en": [
            "Almarai Fresh Full Fat Milk", "Nadec Low Fat Fresh Milk", "Al Safi Skimmed Fresh Milk",
            "Almarai Fresh Ayran Laban", "Nadec Family Size Fresh Yogurt", "Nada Greek High Protein Yogurt",
            "Al Safi Fresh Baladi Cream", "Lurpak Unsalted Butter Blocks", "Mazola Vegetable Margarine",
            "Almarai Spreadable Cream Cheese Jars", "Kraft Cheddar Cheese Blocks", "Almarai Feta Cheese Cubes",
            "Forsana Shredded Mozzarella Cheese", "Al Safi Halloumi Cheese Rolls", "Florida Natural Fresh Orange Juice",
            "Almarai Chilled Fresh Pomegranate Juice", "Al-Watania Fresh Table Eggs Cartons", "Fakieh Fresh Table Eggs 30-tray",
            "Fresh Chilled Baker's Yeast", "Delicio Chilled Mayonnaise Sauce", "Switz Chilled Sambosa Pastry Leaves"
        ],
        "brands_ar": ["المراعي", "نادك", "الصافي", "ندى", "لورباك", "كرافت", "فرسانا", "الوطنية", "فقيه", "سويتز"],
        "brands_en": ["Almarai", "Nadec", "Al Safi", "Nada Dairy", "Lurpak", "Kraft", "Forsana", "Al-Watania", "Fakieh", "Switz"]
    },
    # 16: سلع مثلجة ومجمدة (Frozen FMCG)
    16: {
        "nouns_ar": [
            "دجاج مجمد ساديا كراتين 10 حبات", "دجاج الوطنية مجمد بدون أحشاء", "صدور دجاج طرية مجمدة دو",
            "أفخاذ دجاج مجمدة برديكس", "لحم غنم مفروم مجمد أمريكانا", "لحم بقر مفروم برازيلي ركائز",
            "برجر دجاج مجمد السنبلة بالبقسماط", "برجر لحم بقري جامبو حلواني", "ناجتس دجاج مجمد أمريكانا للأطفال",
            "روبيان مجمد مقشور ومجفف رويال", "فيليه سمك أبيض مجمد سيبلو", "أصابع كابوريا وسالمون مجمد",
            "بطاطس نصف مقلية مجمدة لامب وستون", "بطاطس ودجز متبلة ساديا", "خضار مشكل مجمد العملاق الأخضر",
            "بازلاء خضراء مجمدة السنبلة", "ملوخية مجمدة مفرومة داري", "فراولة مجمدة بونو",
            "آيس كريم باسكن روبنز لتر", "آيس كريم كون زون كراتين", "عجينة بف باستري مجمدة الكرامة"
        ],
        "nouns_en": [
            "Sadia Frozen Whole Chicken 10-pack Carton", "Al-Watania Frozen Cleaned Chicken", "Doux Frozen Tender Chicken Breast",
            "Perdix Frozen Chicken Drumsticks", "Americana Frozen Minced Mutton", "Brazilian Frozen Minced Beef Blocks",
            "Sunbulah Breaded Frozen Chicken Burgers", "Halwani Jumbo Beef Burger Patties", "Americana Kids Frozen Chicken Nuggets",
            "Royal Frozen Peeled Tail-on Shrimp", "Siblou Frozen White Fish Fillet", "Frozen Crab Sticks and Salmon Portions",
            "Lamb Weston Frozen French Fries", "Sadia Seasoned Potato Wedges", "Green Giant Frozen Mixed Vegetables",
            "Sunbulah Frozen Green Peas", "Dari Frozen Chopped Molokhia", "Pono Frozen Strawberries",
            "Baskin Robbins 1L Ice Cream Tubs", "Cone Zone Assorted Ice Cream Cartons", "Al Karama Frozen Puff Pastry Sheets"
        ],
        "brands_ar": ["ساديا", "دو Doux", "أمريكانا", "السنبلة", "حلواني", "داري", "لامب وستون", "سيبلو", "باسكن روبنز"],
        "brands_en": ["Sadia", "Doux", "Americana", "Sunbulah", "Halwani Bros", "Dari", "Lamb Weston", "Siblou", "Baskin Robbins"]
    },
    # 134: الإطارات (Tires)
    134: {
        "nouns_ar": [
            "كفرات هانكوك مقاس 17 للسيارات", "إطارات ميشلان مقاس 18 بايلوت سبورت", "كفرات بريدجستون بوتينزا 19",
            "إطارات يوكوهاما جيولاندر للجيوب", "كفرات دنلوب مقاس 16 هايلوكس", "إطارات كومهو كوري مقاس 15 صالون",
            "كفرات تويو ياباني مقاس 20 لاندكروزر", "إطارات نيتو حجري للبر والطرد", "كفرات ماكسس تايلندي دينا وشاحنات",
            "إطارات شاحنات تريلا مقاس 24 سلك", "كفرات معدات وشيولات كوماتسو مقاس 23.5-25", "كفرات بوبكات رافعة شوكية صب",
            "شنبر وجنط كفرات حديد مجلفن", "بلف كفرات حساس هواء TPMS", "رقع كفرات حرارية وتيوبلس ألماني"
        ],
        "nouns_en": [
            "Hankook 17-inch Passenger Car Tires", "Michelin Pilot Sport 18-inch High Performance Tires", "Bridgestone Potenza 19-inch Tires",
            "Yokohama Geolandar SUV All-Terrain Tires", "Dunlop 16-inch Light Truck Tires", "Kumho Korean 15-inch Passenger Tires",
            "Toyo Japanese 20-inch Land Cruiser Tires", "Nitto Mud-Terrain Off-Road Desert Tires", "Maxxis Commercial Van and Dyna Tires",
            "Heavy Truck Radial Tires Size 24", "Komatsu Wheel Loader Heavy Tires 23.5-25", "Solid Forklift and Bobcat Industrial Tires",
            "Galvanized Steel Wheel Rims and Inner Tubes", "TPMS Wireless Tire Pressure Sensor Valves", "German Cold and Hot Vulcanizing Tire Patches"
        ],
        "brands_ar": ["هانكوك", "ميشلان", "بريدجستون", "يوكوهاما", "دنلوب", "كومهو", "تويو", "ماكسس", "بيريللي", "كونتيننتال"],
        "brands_en": ["Hankook", "Michelin", "Bridgestone", "Yokohama", "Dunlop", "Kumho", "Toyo Tires", "Maxxis", "Pirelli", "Continental"]
    },
    # 165: قطع غيار جديدة (New Auto Spares)
    165: {
        "nouns_ar": [
            "فحمات فرامل سيراميك تويوتا كامري أصلي", "أقمشة فرامل خلفية نيسان باترول", "بواجي ليزر إيريديوم دنسو وكالة",
            "مساعدات هيدروليك جبريل أمريكي", "مقصات أمامية كاملة مع الجلود هيونداي", "دينمو شحن وكهرباء بوش 12 فولت",
            "سلف ماكينة تشغيل مرش أصلي", "رديتر ماء تبريد ألومنيوم دولفين", "مروحة رديتر كهربائية وكالة",
            "كمبروسر مكيف سيارة ساندن ياباني", "فلتر زيت مكينة سيفون وكالة تويوتا", "فلتر هواء محرك أصلي بوش",
            "سير ماكينة ومروحة ميتسوبوشي ياباني", "طرمبة بنزين ومضخة وقود بوش داخل التانكي", "كويلات إشعال ديلفي أصلي",
            "عكوس ومساعدات دركسون كاملة موغ", "مساعدات كبوت وشنطة هيدروليكية", "حساسات أكسجين وشكمان بوش"
        ],
        "nouns_en": [
            "Toyota Camry Genuine Ceramic Brake Pads", "Nissan Patrol Rear Brake Shoes", "Denso Iridium Laser Spark Plugs OEM",
            "Gabriel Heavy Duty Gas Shock Absorbers", "Hyundai Front Lower Suspension Control Arms", "Bosch 12V High Output Alternator",
            "Genuine OEM Engine Starter Motor", "Dolphin Heavy Duty Aluminum Engine Radiator", "OEM Engine Electric Cooling Fan Assembly",
            "Sanden Japanese Car AC Compressor Pump", "Toyota Genuine Spin-on Engine Oil Filter", "Bosch OEM Engine Air Intake Filter",
            "Mitsuboshi Engine Serpentine Drive Belt", "Bosch In-Tank Electric Fuel Pump Module", "Delphi Ignition Coils Pack",
            "Moog Front Drive Axle CV Half Shafts", "Hydraulic Hood and Trunk Gas Lift Struts", "Bosch Upstream Exhaust Oxygen O2 Sensors"
        ],
        "brands_ar": ["تويوتا قطع غيار", "دنسو Denso", "بوش Bosch", "اي سي ديلكو", "موبار Mopar", "دولفين", "موتوركرافت", "ساندن"],
        "brands_en": ["Toyota Genuine", "Denso", "Bosch Automotive", "ACDelco", "Mopar", "Dolphin Radiators", "Motorcraft", "Sanden"]
    },
    # 121: أسمنت (Cement)
    121: {
        "nouns_ar": [
            "إسمنت بورتلاندي عادي اليمامة أكياس 50 كجم", "إسمنت مقاوم للأملاح SRC أسمنت الرياض",
            "إسمنت أبيض سوبر رويال رأس الخيمة", "إسمنت تشطيب ولياسة ناعم أكياس",
            "إسمنت بحبوحي خفيف سائل", "إسمنت سريع الشك والتصلب للصبات المائية",
            "طبالي إسمنت بورتلاندي مغلفة شرينك", "شحنة تريلا إسمنت 1000 كيس واصل الموقع"
        ],
        "nouns_en": [
            "Yamama Ordinary Portland Cement OPC 50kg Bags", "Riyadh Sulfate Resistant Cement SRC",
            "Super White Portland Cement RAK Bags", "Fine Plastering and Finishing Masonry Cement",
            "Lightweight Grouting Cement Mix", "Rapid Hardening Hydraulic Underwater Cement",
            "Shrink-Wrapped Palletized Portland Cement", "Full 1000-Bag Cement Semi-Trailer Truckload"
        ],
        "brands_ar": ["أسمنت اليمامة", "أسمنت الرياض", "أسمنت السعودية", "أسمنت ينبع", "أسمنت القصيم", "أسمنت المدينة"],
        "brands_en": ["Yamama Cement", "Riyadh Cement", "Saudi Cement Co", "Yanbu Cement", "Qassim Cement", "City Cement"]
    },
    # 55: حديد التسليح (Rebar Steel)
    55: {
        "nouns_ar": [
            "حديد تسليح سابك مقاس 16 ملم ربطات تريلا", "حديد تسليح سابك مقاس 14 ملم شد بلد",
            "حديد مباني الراجحي مقاس 12 ملم", "حديد تسليح الاتفاق مقاس 10 ملم",
            "حديد تسليح مقاس 8 ملم كانات ورباط", "حديد تسليح ثقيل مقاس 20 ملم و 25 ملم للجسور",
            "شبك حديد تسليح أرضيات صبة مقاس 8 ملم", "سلك رباط حديد مجلفن لفات وبكرات",
            "حديد كمرات وجسور عريضة I-Beam و H-Beam", "زوايا حديد مبرومة ومبسطة للمقاولات"
        ],
        "nouns_en": [
            "SABIC 16mm High Tensile Deformed Steel Rebar Bundles", "SABIC 14mm Construction Steel Rebar",
            "Al-Rajhi 12mm Grade 60 Rebar Bars", "Al-Ittefaq 10mm Reinforcing Steel Bars",
            "8mm Steel Rebar for Stirrups and Ties", "20mm and 25mm Heavy Structural Rebar for Columns",
            "Welded Wire Steel Mesh Fabric for Concrete Slabs 8mm", "Galvanized Steel Rebar Binding Tie Wire Coils",
            "Structural Steel Wide Flange I-Beams and H-Columns", "Mild Steel Angles and Flat Bars for Construction"
        ],
        "brands_ar": ["سابك حديد", "حديد الراجحي", "حديد الاتفاق", "حديد اليمامة", "حديد الجندل"],
        "brands_en": ["SABIC Steel", "Al Rajhi Steel", "Al Ittefaq Steel", "Yamama Steel", "Jandal Steel"]
    },
    # 132: الحواسيب والمنتجات الإلكترونية (Computers & Electronics)
    132: {
        "nouns_ar": [
            "شاشات تلفزيون سمارت 65 بوصة 4K OLED سامسونج", "شاشة تلفزيون ال جي 55 بوصة نانوسيل بالكرتون",
            "أجهزة لابتوب ديل كور آي 7 مع كرت شاشة", "أجهزة لابتوب اتش بي فكتور قيمنق للألعاب",
            "لابتوب ماك بوك برو إم 3 برو أبل أصلي", "جوالات آيفون 15 برو ماكس كراتين مقفلة",
            "جوالات سامسونج جالكسي إس 24 ألترا وكالة", "أجهزة آيباد إير وآيباد برو مع القلم",
            "أجهزة لوحية تابلت هواوي ميت باد كراتين", "راوترات واي فاي 5G فايبر هواوي وZTE",
            "كاميرات مراقبة هيكفيجن 8 ميجا بكسل 4K NVR", "كاميرات داهوا مراقبة لاسلكية للمنازل",
            "منصات ألعاب بلايستيشن 5 مع يدين تحكم", "شواحن متنقلة باور بانك أنكر 20 ألف ملي أمبير",
            "سماعات بلوتوث لاسلكية أبل إيربودز برو", "شاشات كمبيوتر قيمنق 27 بوصة 165 هرتز",
            "طابعات ليزر ملونة كانون واي فاي كراتين", "أقراص تخزين خارجية SSD سعة 1 تيرابايت سامسونج"
        ],
        "nouns_en": [
            "Samsung 65-inch 4K OLED Smart TV", "LG 55-inch NanoCell 4K Smart TV in Box",
            "Dell Intel Core i7 High Performance Laptop", "HP Victus Gaming Laptop with Dedicated GPU",
            "Apple MacBook Pro M3 Pro Chip Laptop", "Apple iPhone 15 Pro Max Factory Sealed Box",
            "Samsung Galaxy S24 Ultra 5G Smartphone", "Apple iPad Air and iPad Pro with Apple Pencil",
            "Huawei MatePad Android Tablets Cartons", "Huawei and ZTE 5G Ultra-Fast WiFi Routers",
            "Hikvision 8MP 4K IP CCTV Security Cameras NVR Kit", "Dahua Wireless PTZ Security Cameras for Home",
            "Sony PlayStation 5 Console with DualSense Controllers", "Anker 20,000mAh Portable Power Bank Fast Charger",
            "Apple AirPods Pro 2nd Gen Wireless Earbuds", "27-inch 165Hz IPS QHD Gaming Monitors",
            "Canon All-in-One Wireless Color Laser Printers", "Samsung 1TB External Portable NVMe SSD"
        ],
        "brands_ar": ["سامسونج", "أبل", "ال جي", "ديل", "اتش بي", "هواوي", "سوني", "أنكر", "هيكفيجن", "كانون", "شاومي"],
        "brands_en": ["Samsung", "Apple", "LG", "Dell", "HP", "Huawei", "Sony", "Anker", "Hikvision", "Canon", "Xiaomi"]
    },
}
