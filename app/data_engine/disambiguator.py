"""Cross-root collision prevention and polysemy disambiguation engine."""

from __future__ import annotations
import re
from dataclasses import dataclass
from app.data_engine.ontology import ROOT_ONTOLOGY


@dataclass(frozen=True)
class PolysemyRule:
    token: str
    root_contexts: dict[int, tuple[str, ...]]  # root_id -> required anchor terms


# Rules for high-risk ambiguous words across the 37 roots
POLYSEMY_RULES: tuple[PolysemyRule, ...] = (
    PolysemyRule(
        token="زيت",
        root_contexts={
            12: ("طعام", "دوار الشمس", "زيتون", "عافية", "قلي", "طبخ", "نباتي", "كانولا", "سمسم", "مازولا"),
            129: ("محرك", "سيارة", "قير", "بترومين", "تخليقي", "10w40", "5w30", "20w50", "فرامل", "كاسترول", "فوكس"),
            10: ("بترولي", "خام", "أساس", "تشحيم صناعي", "تكرير", "نفطي", "مشتقات"),
            192: ("عطري", "مساج", "جسم", "شعر", "لافندر", "عود", "مركز"),
        },
    ),
    PolysemyRule(
        token="بطارية",
        root_contexts={
            129: ("سيارة", "هانكوك", "اي سي ديلكو", "مركبات", "70 أمبير", "80 أمبير", "12 فولت", "شاحنة"),
            131: ("جوال", "لابتوب", "آيفون", "سامسونج", "باور بانك", "ليثيوم", "شحن متنقل"),
            162: ("سكراب", "تالفة", "خردة", "رصاص مستعمل"),
        },
    ),
    PolysemyRule(
        token="خشب",
        root_contexts={
            34: ("بليود", "بناء", "طوبار", "ألواح خرسانة", "سويدي إنشائي", "مسلح"),
            133: ("أثاث", "غرفة نوم", "طاولة", "دولاب", "زان", "مجلس", "مكتب"),
            148: ("حطب", "تدفئة", "سمر", "قرض", "شواء", "ناشف"),
            162: ("طبالي مكسرة", "خردة", "سكراب", "بقايا نجارة للتدوير"),
        },
    ),
    PolysemyRule(
        token="حديد",
        root_contexts={
            34: ("تسليح", "سابك", "مباني", "16 ملم", "14 ملم", "شبك أرضيات", "إنشائي"),
            5: ("صناعي", "تروس", "قوالب", "سحب", "درفلة", "أعمدة صناعية"),
            162: ("سكراب", "خردة", "كبس", "تالف", "قصاصات ورش للوزن"),
        },
    ),
    PolysemyRule(
        token="ثلاجة",
        root_contexts={
            179: ("عرض", "سوبرماركت", "باب زجاجي", "تبريد", "فريزر تجاري", "محلات"),
            12: ("لحوم مبردة", "خضار ثلاجة", "مجمدات"),
        },
    ),
    PolysemyRule(
        token="خزان",
        root_contexts={
            126: ("ماء", "مويا", "فايبر جلاس", "بولي إيثيلين", "علوي", "أرضي", "الزامل"),
            127: ("غاز", "مركزي", "غازكو", "ضغط عالي", "LPG", "فوق الأرض"),
            167: ("IBC", "وسائط", "قفص حديدي", "1000 لتر فارغ"),
        },
    ),
    PolysemyRule(
        token="أنابيب",
        root_contexts={
            125: ("صرف صحي", "مجاري", "مياه عادمة", "uPVC برتقالي", "غرف تفتيش"),
            34: ("سباكة", "كلاس 5", "مباني", "مياه رمادي", "حراري خضراء"),
            4: ("ري", "تنقيط", "زراعي", "مزارع", "رشاشات"),
        },
    ),
)


class DisambiguationEngine:
    """Detects and resolves cross-root collisions, enforcing unambiguous context."""

    def __init__(self) -> None:
        self._rules = POLYSEMY_RULES

    def validate_and_anchor(self, text: str, root_id: int) -> tuple[bool, str]:
        """
        Validates whether text is unambiguous for the assigned root.
        If ambiguous, injects an anchor or returns (False, text) to drop it.
        """
        spec = ROOT_ONTOLOGY.get(root_id)
        if not spec:
            return False, text

        # Check strict exclusions
        for exclusion in spec.strict_exclusions:
            if exclusion in text:
                return False, text

        modified_text = text
        for rule in self._rules:
            if re.search(rf"\b{rule.token}\b", text):
                # Word is present: check if root is supported for this word
                if root_id not in rule.root_contexts:
                    # Token belongs to other categories unless explicitly qualified
                    return False, text

                valid_anchors = rule.root_contexts[root_id]
                has_anchor = any(anchor in text for anchor in valid_anchors)

                if not has_anchor:
                    # Inject primary anchor to guarantee 0% ambiguity
                    chosen_anchor = valid_anchors[0]
                    modified_text = f"{text} {chosen_anchor}"

        return True, modified_text
