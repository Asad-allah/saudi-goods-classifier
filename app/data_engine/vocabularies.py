"""Bilingual (Arabic/English) logistics packaging, dialect vocabularies, and mutators."""

from __future__ import annotations
import random

PACKAGING_CONTAINERS_AR: tuple[str, ...] = (
    "طبلية", "طبالي", "كرتون", "كراتين", "برميل", "براميل",
    "شوال", "شوالات", "خيشة", "خياش", "لفة", "لفات",
    "ربطة", "ربطات", "رول", "رولات", "شد", "شدات",
    "صندوق", "صناديق", "بوكس", "بوكسات", "حمولة دينا", "حمولة تريلا",
    "شحنة", "دفعة", "طلبية", "كونتينر", "تانكي", "صهريج", "طرد", "طرود"
)

PACKAGING_CONTAINERS_EN: tuple[str, ...] = (
    "pallet", "pallets", "carton", "cartons", "drum", "drums",
    "bag", "bags", "sack", "sacks", "roll", "rolls",
    "bundle", "bundles", "box", "boxes", "crate", "crates",
    "truckload", "container", "IBC tote", "tanker load", "package", "packages",
    "batch of", "consignment of", "cargo of", "bulk shipment of"
)

QUANTITY_PREFIXES_AR: tuple[str, ...] = (
    "1", "2", "3", "4", "5", "6", "8", "10", "12", "15", "20", "24",
    "30", "40", "50", "60", "75", "100", "150", "200", "250", "500", "1000",
    "حبتين", "كرتونين", "طبلتين", "شوالين", "برميلين", "صندوقين", "لفتين",
    "كمية", "دفعة كاملة من", "حمولة كاملة من", "طلب جملة"
)

QUANTITY_PREFIXES_EN: tuple[str, ...] = (
    "1", "2", "3", "4", "5", "6", "8", "10", "12", "15", "20", "24",
    "30", "40", "50", "60", "75", "100", "150", "200", "250", "500", "1000",
    "2x", "5x", "10x", "20x", "50x", "100x",
    "10 pcs", "25 pcs", "50 units", "100 units", "20 boxes", "10 pallets",
    "full truckload of", "bulk order of", "wholesale batch of"
)

PREFIXES_AR: tuple[str, ...] = (
    "شحنة", "حمولة", "أغراض", "طلبية", "نقل", "توصيل", "تحميل",
    "كراتين", "طبالي", "مقاضي", "عفش", "دفعة", "طلبية مستعجلة",
    "توصيل سريع", "أغراض محل", "بضاعة مستودع", "تنزيل", "توريد", "إرسالية"
)

PREFIXES_EN: tuple[str, ...] = (
    "Shipment of", "Delivery of", "Cargo:", "Order:", "Freight:",
    "Transport of", "Loading:", "Dispatch:", "Bulk order of", "Supply of",
    "Consignment of", "Express delivery:", "Warehouse stock:", "Wholesale order:"
)

MODIFIERS_AR: tuple[str, ...] = (
    "جديد بالكرتون", "وكالة أصلي", "نظيف شغال", "مستعمل بحالة ممتازة",
    "مستورد أصلي", "سعودي بلدي", "مغلف وجاهز", "دفعة جديدة",
    "درجة أولى فاخر", "كامل مع ملحقاته", "مضمون أصلي", "جاهز للشحن",
    "نخب أول", "مواصفات سعودية", "تصفية مستودع", "بسعر الجملة"
)

MODIFIERS_EN: tuple[str, ...] = (
    "brand new in box", "OEM original", "grade A quality", "heavy duty",
    "export quality", "commercial grade", "ready for dispatch", "certified original",
    "fresh stock", "industrial standard", "sealed in carton", "premium quality",
    "Saudi SASO specs", "warehouse clearance", "wholesale price"
)

PACKAGING_CONTAINERS: tuple[str, ...] = PACKAGING_CONTAINERS_AR + PACKAGING_CONTAINERS_EN
QUANTITY_PREFIXES: tuple[str, ...] = QUANTITY_PREFIXES_AR + QUANTITY_PREFIXES_EN
SAUDI_DIALECT_PREFIXES: tuple[str, ...] = PREFIXES_AR + PREFIXES_EN
DESCRIPTIVE_MODIFIERS: tuple[str, ...] = MODIFIERS_AR + MODIFIERS_EN

_ARABIC_KEYBOARD_NEIGHBORS: dict[str, str] = {
    "ق": "فغ", "ف": "قث", "غ": "فع", "ع": "غه", "ه": "عخ", "خ": "هح",
    "ح": "خج", "ج": "حد", "د": "جذ", "ش": "س", "س": "شيب", "ي": "سب",
    "ب": "يت", "ت": "بن", "ن": "تم", "م": "نك", "ك": "مط", "ط": "ك",
    "ر": "ز", "ز": "رو", "و": "ز", "ة": "ه", "ه": "ة", "ى": "ي", "ي": "ى",
    "ا": "إآأ", "إ": "ا", "أ": "ا", "ء": "ئؤ"
}


def apply_realistic_noise(text: str, noise_probability: float = 0.20) -> str:
    """Applies realistic orthographic variation or keyboard slip."""
    if random.random() > noise_probability or len(text) < 5:
        return text

    noise_type = random.choice(["hamza_drop", "taa_marbuta", "yaa_alif", "keyboard_slip", "space_variation"])

    if noise_type == "hamza_drop":
        return text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    elif noise_type == "taa_marbuta":
        if "ة" in text:
            return text.replace("ة", "ه")
        elif "ه" in text:
            return text.replace("ه", "ة")
    elif noise_type == "yaa_alif":
        if "ي" in text:
            return text.replace("ي", "ى")
        elif "ى" in text:
            return text.replace("ى", "ي")
    elif noise_type == "keyboard_slip":
        chars = list(text)
        candidates = [i for i, c in enumerate(chars) if c in _ARABIC_KEYBOARD_NEIGHBORS]
        if candidates:
            idx = random.choice(candidates)
            chars[idx] = random.choice(_ARABIC_KEYBOARD_NEIGHBORS[chars[idx]])
            return "".join(chars)
    elif noise_type == "space_variation":
        return text.replace(" و ", " و")

    return text
