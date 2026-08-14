import json
from pathlib import Path
from app.nlp.normalizer import normalize_text

contexts_path = Path("storage/catalog/saudi_market_category_contexts.json")
with open(contexts_path, "r", encoding="utf-8") as f:
    contexts = json.load(f)

# Comprehensive Stationery, Pens, Office & Paper Supplies for Category 151 (الورق ومنتجاته - Root 5 صناعية)
stationery_ar = [
    # 🖊️ الأقلام وأدوات الكتابة
    "قلم ازرق", "قلم جاف ازرق", "قلم حبر ازرق", "قلم جاف اسود", "قلم جاف احمر", "قلم جاف اخضر",
    "اقلام بيك كريستال", "اقلام روترنج", "اقلام باركر فاخرة", "اقلام يوني بول", "اقلام زيبرا ساراسا",
    "قلم رصاص اتش بي", "اقلام رصاص ميكانيكية سنون", "علب سنون رصاص 0.5 و 0.7", "اقلام حبر سائل وجل",
    "اقلام تظليل هايلايتر ملونة اصفر وفوسفوري", "اقلام سبورة بيضاء وايت بورد قابلة للمسح",
    "اقلام خط عربي وقصب", "اقلام فلوماستر والوان شمعية ومائية وخشبية فابر كاستل",
    "اقلام ماركر تحديد ثابت شاربي", "قلم تصحيح طامس كوريكتر بليد",

    # 📚 الدفاتر والكشاكيل والقرطاسية
    "دفاتر مدرسية مسطرة وانجليزي", "كشاكيل جامعية سلك حلزوني", "دفاتر مربعات رسم بياني",
    "نوت بوك ومذكرات جيب", "دفاتر رسم اسكتش بوك ورق كانسون", "دفاتر تحضير معلمين",
    "دفاتر فواتير وسندات قبض وصرف وكاربون", "اوراق ملاحظات ذاتية اللصق ستيكي نوتس",

    # 📄 ورق الطباعة والتصوير والتغليف
    "ورق تصوير ايه 4 كراتين 80 جرام دبل ايه وروتو ودابل ايه", "ورق طباعة A4 و A3 خمس رزم كرتون",
    "ورق كمبيوتر متصل كربون", "ورق كوشيه لماع ومطفي للمطابع", "ورق مقوى بريستول وكانسون ملون",
    "رولات ورق كرافت بني للتغليف", "رولات فواتير كاشير وحراري مدى ونقاط بيع", "ورق تغليف هدايا وسولوفان",
    "ورق كرتون مضلع ودوبلكس كراتين فارغة للشحن", "اكياس ورقية كرافت بمقابض", "اظرف رسائل بيضاء وبنية",

    # ✂️ الادوات والمستلزمات المكتبية والمدرسية
    "قرطاسية وادوات مكتبية ومدرسية كراتين", "برايات ومحايات ممحاة رصاص", "مساطر بلاستيك وحديد ومثلثات هندسية",
    "دباسات ورق ودبابيس مقاس 24/6 و 26/6", "خرامات ورق مكتبية ثنائية ورباعية",
    "مشابك ورق حديد وكلبسات ورق", "مقصات ورق ومشارط كتر مكتبية", "غراء اصابع يوهو ومسدس شمع ولاصق سائل",
    "اشرطة لاصقة تيب شفاف وعريض وشطرطون تغليف", "ملفات فايلات حفظ وثائق وبوكس فايل",
    "حافظات اوراق بلاستيكية شفافة وجيوب نايلون", "شنط وحقائب مدرسية ومقالم اقلام اطفال"
]

stationery_en = [
    # 🖊️ Pens & Writing Instruments
    "blue ballpoint pen", "blue ink pen", "black ballpoint pen", "red pen", "green pen",
    "bic cristal pens", "pilot gel pens", "uniball rollerball pens", "zebra sarasa gel pens",
    "parker luxury pens", "hb wooden pencils", "mechanical pencils 0.5 0.7 leads", "pencil lead refills",
    "colored highlighter markers pastel and neon", "whiteboard dry erase markers", "arabic calligraphy pens",
    "faber castell color pencils wax crayons", "permanent sharpie markers", "correction tape and fluid",

    # 📚 Notebooks & Stationery
    "ruled school notebooks", "spiral university notebooks", "graph grid notebooks",
    "pocket note pads", "canson sketch books for drawing", "sticky notes memo pads",
    "receipt invoice vouchers and carbonless books", "school stationery supplies bulk boxes",

    # 📄 Printing Paper & Packaging
    "a4 copy paper 80gsm cartons double a rotoprint", "a4 and a3 printing paper 5 reams box",
    "continuous computer carbon paper", "glossy and matte art paper for printing press",
    "colored bristol cardboard paper", "brown kraft packaging paper rolls",
    "pos thermal cashier receipt rolls", "gift wrapping paper and cellophane rolls",
    "corrugated cardboard shipping boxes", "kraft paper shopping bags with handles", "white and brown postal envelopes",

    # ✂️ Office & School Supplies
    "office stationery and desk supplies", "pencil sharpeners and erasers", "plastic and metal rulers geometry sets",
    "paper staplers and standard staples 24/6", "office 2-hole and 4-hole paper punchers",
    "metal paper clips and binder bulldog clips", "stationery scissors and utility craft cutters",
    "uhu glue sticks liquid adhesive glue", "transparent packaging tape and sealing tapes",
    "document ring binders box files lever arch files", "clear plastic sheet protectors sleeves",
    "school backpacks student bags and pencil cases"
]

# Comprehensive Books, Educational Curricula & Publications for Category 157 (الكتب - Root 157)
books_ar = [
    "كتب دراسية ومناهج تعليمية وزارة التعليم", "كتب جامعية واكاديمية ومراجع علمية",
    "روايات وكتب ادب وقصص اطفال وناشئة", "كتب دينية وفقه وتفاسير ومصاحف شريفة",
    "كتب تطوير ذات وتنمية بشرية وادارة اعمال", "كتب تاريخ وسير وتراجم وموسوعات",
    "قواميس ومعاجم لغوية عربي وانجليزي وفرنساوي", "كتب طبخ وتغذية وصحة",
    "كتب قانون وانظمة ولوائح قانونية", "مجلات وكتالوجات ومطبوعات دورية",
    "اطلس وخرائط جغرافية ومراجع بحثية", "كتب ومطبوعات جرير والعبيكان والرشد كراتين"
]

books_en = [
    "ministry of education school textbooks and curricula", "university textbooks and academic reference books",
    "literary novels storybooks and children literature", "holy quran copies islamic religious and tafseer books",
    "self development human development and business management books", "history books biographies and encyclopedias",
    "arabic english dictionaries and language lexicons", "cooking nutrition and culinary books",
    "law books legal regulations and jurisprudence references", "magazines periodicals and catalogs",
    "geographical atlases maps and research publications", "jarir and obeikan published books cartons"
]

# Update Category 151 (الورق ومنتجاته)
c151 = contexts.get("151", {})
c151["good_type_id"] = 151
c151["name_ar"] = "الورق ومنتجاته"
c151["name_en"] = "Paper and its products"
c151["root_id"] = 5
c151["root_name_ar"] = "صناعية"
c151["root_name_en"] = "Industrial"

existing_151_ar = {normalize_text(t) for t in c151.get("trade_terms_ar", [])}
existing_151_en = {t.lower().strip() for t in c151.get("trade_terms_en", [])}
new_151_ar = [t for t in stationery_ar if normalize_text(t) not in existing_151_ar]
new_151_en = [t for t in stationery_en if t.lower().strip() not in existing_151_en]

c151["trade_terms_ar"] = list(dict.fromkeys(c151.get("trade_terms_ar", []) + new_151_ar))
c151["trade_terms_en"] = list(dict.fromkeys(c151.get("trade_terms_en", []) + new_151_en))
c151["market_context_ar"] = (
    "يشمل تصنيف الورق ومنتجاته والقرطاسية المكتبية والمدرسية (المجموعة الرئيسية: صناعية): "
    "أقلام جاف وحبر ورصاص وتظليل (قلم أزرق، أسود، أحمر، فلوماستر، ماركر)، دفاتر وكشاكيل مسطرة وسلك، "
    "ورق تصوير وطباعة A4 كراتين، ورق كرافت وتغليف، كراتين شحن، فواتير حرارية ومدى، أدوات مكتبية ومدرسية "
    "(برايات، مساطر، محايات، مقصات، دباسات، خرامات، غراء ولاصق، مشابك)، ملفات وحافظات أوراق وحقائب مدرسية ومقالم."
)
c151["market_context_en"] = (
    "Category Paper and its products under Industrial includes all paper goods, stationery, writing instruments and office supplies: "
    "ballpoint pens (blue pen, black, red pens, gel pens, pencils, highlighters, markers), school and spiral notebooks, "
    "A4 copy paper cartons, brown packaging kraft paper, cardboard shipping boxes, thermal receipt rolls, "
    "office and school desk accessories (sharpeners, erasers, rulers, staplers, punchers, scissors, glues, clips, tapes), "
    "ring binders, file folders, student backpacks and pencil cases."
)
contexts["151"] = c151

# Update Category 157 (الكتب)
c157 = contexts.get("157", {})
c157["good_type_id"] = 157
c157["name_ar"] = "الكتب"
c157["name_en"] = "Books"
c157["root_id"] = 157
c157["root_name_ar"] = "الكتب"
c157["root_name_en"] = "Books"

existing_157_ar = {normalize_text(t) for t in c157.get("trade_terms_ar", [])}
existing_157_en = {t.lower().strip() for t in c157.get("trade_terms_en", [])}
new_157_ar = [t for t in books_ar if normalize_text(t) not in existing_157_ar]
new_157_en = [t for t in books_en if t.lower().strip() not in existing_157_en]

c157["trade_terms_ar"] = list(dict.fromkeys(c157.get("trade_terms_ar", []) + new_157_ar))
c157["trade_terms_en"] = list(dict.fromkeys(c157.get("trade_terms_en", []) + new_157_en))
c157["market_context_ar"] = (
    "يشمل تصنيف الكتب والمطبوعات (المجموعة الرئيسية: الكتب): المناهج والكتب المدرسية المقررة، الكتب والمراجع الأكاديمية والجامعية، "
    "المصاحف الشريفة وكتب الفقه والتفاسير، الروايات والقصص الأدبية، الموسوعات والقواميس والمعاجم، كتب تطوير الذات والإدارة، والمجلات والدوريات."
)
c157["market_context_en"] = (
    "Category Books includes school curricula textbooks, academic university reference materials, the Holy Quran and Islamic literature, "
    "literary novels, encyclopedias, dictionaries, self-help books, law references, and periodicals."
)
contexts["157"] = c157

with open(contexts_path, "w", encoding="utf-8") as f:
    json.dump(contexts, f, ensure_ascii=False, indent=2)

print(f"✅ Category 151 (الورق والقرطاسية) now has {len(c151['trade_terms_ar'])} AR and {len(c151['trade_terms_en'])} EN terms!")
print(f"✅ Category 157 (الكتب) now has {len(c157['trade_terms_ar'])} AR and {len(c157['trade_terms_en'])} EN terms!")
