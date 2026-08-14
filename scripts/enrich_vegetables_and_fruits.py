import json
from pathlib import Path
from app.nlp.normalizer import normalize_text

contexts_path = Path("storage/catalog/saudi_market_category_contexts.json")
with open(contexts_path, "r", encoding="utf-8") as f:
    contexts = json.load(f)

# Comprehensive Inventory of Fresh Produce, Fruits, Vegetables, Herbs, Saudi Cultivars, Arabized English & Dialect terms
fruits_and_vegetables_ar = [
    # 🐉 فاكهة التنين والفواكه الاستوائية والمعربة
    "دراغون فروت", "دراجون فروت", "دراكون فروت", "فاكهة التنين", "فاكهة التنين الاحمر", "فاكهة التنين الابيض",
    "باشن فروت", "فاكهة الالام", "ماراكويا", "افوكادو", "افوكادو هاس", "افوكادو كيني وبيروفي",
    "بابايا رد ليدي", "بابايا جازان", "بابايا فيليبيني", "جوافة مصري وسعودي", "قشطة بلدي واستوائي",
    "اناناس سكري", "اناناس فيليبيني", "مانجوستين", "رامبوتان", "دوريان", "ليتشي", "جاك فروت",
    "كيوي اخضر", "كيوي ذهبي", "كاكا فرسيمون", "سفرجل", "كرامبولا فاكهة النجمة",

    # 🥭 المانجو وأصناف جازان والمحلي
    "مانجو جيزان", "مانجو جازان تومي", "مانجو كيت", "مانجو عويس", "مانجو زبدة", "مانجو جلن",
    "مانجو سنسيشن", "مانجو سمكة سنارة", "مانجو الفونسو هندي", "مانجو سكري", "مانجو فونس", "مانجو باكستاني شونسا",

    # 🫐 التوتيات والفراولة والكرز
    "بلوبيري", "توت ازرق", "بلاك بيري", "توت اسود", "رازبيري", "توت احمر", "كرانبيري", "توت بري",
    "فراولة دريسكول", "فراولة طازجة بلدي ومستورد", "كرز احمر", "كرز سكري شامي", "كرز اسباني", "توت شامي",

    # 🍉 البطيخ والشمام والحمضيات
    "حبحب شاحنات كراتين", "حبحب احمر سكري", "جح نجد والقصيم", "رقي عراقي وكويتي", "بطيخ احمر واصفر",
    "شمام كوز", "شمام عسلي", "شمام اناناس", "خربز", "برتقال ابو صرة", "برتقال عصير فالنسيا",
    "برتقال سكري مصري وجنوب افريقي", "يوسفي كليمنتينا", "يوسفي مندلينا ومغربي", "كريفون جريب فروت",
    "بوملي صيني وابيض", "ليمون بنزهير اخضر صغير", "ليمون حساوي", "ليمون اصفر تركي وجنوب افريقي",
    "ليمون اضاليا", "كمكوات برتقال ياباني ذهبي",

    # 🍎 الفواكه البستانية والتمور الرطبة
    "تفاح احمر سكري واشنطن وجالا", "تفاح اخضر جراني سميث", "تفاح اصفر جولدن", "تفاح لبناني وايراني",
    "رمان الطائف", "رمان يمني صعدي", "رمان مصري منفلوطي", "برشومي تين شوكي صبار", "حماط تين بلدي",
    "تين تركي واسباني", "عنب طائفي", "عنب اسود وبناتي بدون بذور", "عنب احمر كريمسون", "عنب اخضر لبناني",
    "موز جازان بلدي", "موز اكوادوري وفلبيني كراتين شربتلي", "دراق سكري ومفلطح", "خوخ كعكة",
    "نكتارين", "مشمش حموي وتركي", "بخارى حمراء وصفراء", "قراصيا وبرقوق", "اكي دنيا اسكدنيا",
    "رطب برحي مزارع الخرج والقصيم", "رطب سكري وخلاص طازج", "كستناء ابو فروة مشوي", "لوز اخضر وجوز اخضر",

    # 🥬 الورقيات والأعشاب والسلطات
    "جرجير بلدي حزم", "خس مدور كابوتشا ايسبرج", "خس روماني طويل", "خس لولو روزو احمر",
    "سبانخ بلدي طازج", "ملوخية طازجة ورق وعيدان", "بقدونس مفروم حزم", "كزبرة خضراء طازجة",
    "شبت اخضر", "نعناع مديني ومغربي", "حبق ريحان سعودي", "دوش وعطرة وشاي اخضر",
    "كراث حساوي", "سلق اخضر", "رجلة بربير", "بصل اخضر حزم", "هندباء وشيكوريا", "كيل اخضر عضوي",
    "روكا واوراق سلطة مشكلة",

    # 🍅 الخضروات الثمرية والقرعيات
    "طماطم محمية كراتين شاحنات", "طماط بلدي وصوب زراعية", "طماطم كرزية شيري", "خيار صالات ومحمي كراتين",
    "كوسا بلدي اخضر وصغير", "باذنجان رومي اسود", "باذنجان طويل حشو", "باذنجان ابيض ومخطط",
    "فلفل رومي بارد اخضر والوان احمر واصفر", "فلفل شقراء حار بلدي", "فلفل هندي وتايلندي حار",
    "فلفل هلابينو مكسيكي", "بامية خضراء زيرو وبلدي", "فاصوليا خضراء فرنسية وعريضة", "بازلاء خضراء قرون",
    "لوبيا خضراء", "ذرة صفراء سكرية كيزان", "قرع عسلي احمر وبرتقالي", "يقطين ودباء", "كوسا صفراء زوكيني",

    # 🥔 الجذور والدرنات والبصليات
    "بطاطس مائدة كراتين وخياش تبوك وحائل والقصيم", "بطاطس قلي وتحمير", "بطاطا حلوة جزرية سكرية",
    "بصل احمر هندي ويمني ومصري خياش", "بصل ابيض سكري واسباني", "ثوم صيني بلدي ابيض خياش",
    "جزر استرالي ومصري وسعودي كراتين", "لفت ابيض وبنفسجي مخلل", "شوندر بنجر احمر سكري",
    "فجل احمر دائري وفجل ابيض طويل رويد", "زنجبيل طازج صيني وهندي", "كركم طازج اصفر",
    "قلقاس صعيدي", "هليون اسباراجوس طازج", "فطر عيش الغراب مشروم ابيض وبني وبورتوبيلو",
    "خرشوف ارضي شوكي", "كرفس امريكي واوروبي سيقان", "كرات فرنسي ليك", "قرنبيط زهرة بيضاء كراتين",
    "بروكلي اخضر طازج", "ملفوف كرنب ابيض واحمر", "خضار مشكل طازج وسلطة جاهزة"
]

fruits_and_vegetables_en = [
    # 🐉 Dragon Fruit & Exotic Produce
    "dragon fruit", "red dragon fruit", "white dragon fruit", "pitaya", "passion fruit", "maracuya",
    "hass avocado", "fresh avocado", "red lady papaya", "philippine papaya", "fresh guava", "custard apple",
    "cherimoya", "sweet pineapple", "mangosteen", "rambutan", "durian", "lychee", "jackfruit",
    "green kiwi", "golden kiwi", "persimmon", "quince", "star fruit carambola",

    # 🥭 Mangoes & Saudi Cultivars
    "jazan mango", "tommy atkins mango", "keitt mango", "owais mango", "zebda mango", "glenn mango",
    "sensation mango", "samaka mango", "alphonso mango", "chaunsa pakistani mango", "sugar mango",

    # 🫐 Berries & Cherries
    "blueberries", "blackberries", "raspberries", "cranberries", "driscoll strawberries", "fresh strawberries",
    "red sweet cherries", "spanish cherries", "mulberries", "wild berries",

    # 🍉 Melons & Citrus
    "sweet red watermelon", "yellow watermelon", "habhab watermelon", "sweet melon cantaloupe", "honeydew melon",
    "navel oranges", "valencia juicing oranges", "sugar oranges", "clementines", "mandarin tangerines",
    "grapefruit", "white pomelo", "small green baladi lime", "hasawi lime", "yellow turkish lemons",
    "adalia lemons", "kumquats golden oranges",

    # 🍎 Orchard Fruits & Fresh Dates
    "red delicious apples", "gala apples", "granny smith green apples", "golden delicious apples",
    "taif pomegranates", "yemeni pomegranates", "manfalouti pomegranates", "prickly pear cactus fruit",
    "fresh baladi figs", "taif grapes", "seedless black grapes", "crimson red grapes", "white green grapes",
    "local jazan bananas", "ecuadorian chiquita bananas", "sweet flat donut peaches", "peaches",
    "nectarines", "apricots", "red and yellow plums", "prunes", "loquats",
    "fresh barhi rutab dates", "fresh khalas rutab dates", "sweet roasted chestnuts", "fresh green almonds",

    # 🥬 Leafy Greens & Culinary Herbs
    "fresh arugula watercress", "iceberg lettuce", "romaine lettuce", "lollo rosso red lettuce",
    "fresh baladi spinach", "fresh molokhia leaves", "fresh flat parsley", "fresh green coriander cilantro",
    "fresh dill", "madinah mint leaves", "saudi basil habaq", "sweet marjoram doush",
    "hasawi leeks", "swiss chard", "purslane", "green spring onions scallions", "curly endive chicory",
    "organic green kale", "mixed salad rocket leaves",

    # 🍅 Fruiting Vegetables & Squash
    "greenhouse tomatoes", "cherry tomatoes", "greenhouse cucumbers", "green zucchini marrow",
    "black globe eggplants", "long stuffed eggplants", "green red and yellow bell peppers",
    "hot shaqa chili peppers", "indian bird eye chilies", "jalapeno peppers", "fresh zero okra",
    "french green beans", "green sweet peas", "black eyed peas", "sweet corn on the cob",
    "red and orange pumpkin", "butternut squash", "yellow courgettes",

    # 🥔 Roots, Tubers & Alliums
    "table potatoes hail tabuk", "crispy frying potatoes", "sweet carrots potatoes",
    "red onions sacks", "white spanish onions", "fresh white garlic bulbs",
    "fresh australian carrots", "white and purple pickling turnips", "red sweet table beetroot",
    "round red radishes", "long white daikon radishes", "fresh ginger root", "fresh yellow turmeric root",
    "taro root", "fresh green asparagus", "white button and brown portobello mushrooms",
    "fresh globe artichokes", "american celery stalks", "french leeks", "fresh white cauliflower heads",
    "fresh green broccoli crowns", "white and red round cabbage heads", "mixed fresh vegetables and salad packs"
]

# Update Category 171
c171 = contexts.get("171", {})
c171["good_type_id"] = 171
c171["name_ar"] = "الخضروات والفواكه"
c171["name_en"] = "Fresh Vegetables and Fruits"
c171["root_id"] = 12
c171["root_name_ar"] = "مواد غذائية"
c171["root_name_en"] = "Food Items"

existing_ar = {normalize_text(t) for t in c171.get("trade_terms_ar", [])}
existing_en = {t.lower().strip() for t in c171.get("trade_terms_en", [])}

new_ar = [t for t in fruits_and_vegetables_ar if normalize_text(t) not in existing_ar]
new_en = [t for t in fruits_and_vegetables_en if t.lower().strip() not in existing_en]

c171["trade_terms_ar"] = list(dict.fromkeys(c171.get("trade_terms_ar", []) + new_ar))
c171["trade_terms_en"] = list(dict.fromkeys(new_en))  # completely clean out broken electrical placeholder!

c171["market_context_ar"] = (
    "يشمل تصنيف الخضروات والفواكه الطازجة (المجموعة الرئيسية: مواد غذائية) جميع المحاصيل الزراعية والبستانية "
    "المتداولة في أسواق النفع العام وسوق الخضار المركزي بالمملكة: دراغون فروت (دراجون فروت فاكهة التنين)، "
    "باشن فروت، افوكادو، بلوبيري، كرز، فراولة، حبحب، جح، بطيخ، شمام، مانجو جيزان، رمان الطائف، برشومي تين شوكي، "
    "حمضيات (برتقال، يوسفي، ليمون بنزهير وحساوي)، تفاح، موز، دراق وخوخ، تمور ورطب برحي، ورقيات (جرجير، خس، سبانخ، ملوخية، "
    "بقدونس، كزبرة، شبت، نعناع مديني، كراث حساوي)، خضروات ثمرية (طماطم، خيار، كوسا، باذنجان، فلفل رومي وحار، بامية، فاصوليا، "
    "قرع عسلي)، وجذور وبصليات (بطاطس، بطاطا حلوة، بصل، ثوم، جزر، فجل، زنجبيل، كركم، مشروم فطر عيش الغراب، بروكلي، زهرة قرنبيط)."
)

c171["market_context_en"] = (
    "Category Fresh Vegetables and Fruits under Food Items encompasses all fresh produce, fruits, vegetables, and culinary herbs "
    "in the Saudi market: dragon fruit (red and white pitaya), passion fruit, hass avocado, blueberries, raspberries, strawberries, "
    "cherries, watermelons (habhab, gah), sweet melons, jazan mangoes, taif pomegranates, prickly pears, citrus fruits (oranges, "
    "mandarins, limes, lemons), apples, bananas, peaches, fresh rutab dates, leafy greens (arugula, lettuce, spinach, molokhia, "
    "parsley, coriander, mint, leeks), fruiting vegetables (tomatoes, cucumbers, zucchini, eggplants, bell peppers, hot chilies, "
    "okra, green beans, pumpkins), and root vegetables (potatoes, sweet potatoes, onions, garlic, carrots, radishes, fresh ginger, "
    "mushrooms, broccoli, and cauliflower)."
)

contexts["171"] = c171

with open(contexts_path, "w", encoding="utf-8") as f:
    json.dump(contexts, f, ensure_ascii=False, indent=2)

print(f"✅ Category 171 (الخضروات والفواكه) successfully enriched with {len(c171['trade_terms_ar'])} Arabic and {len(c171['trade_terms_en'])} English terms!")
