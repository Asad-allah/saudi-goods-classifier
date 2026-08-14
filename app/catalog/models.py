from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GoodType:
    id: int
    ar_name: str
    en_name: str
    common_names: tuple[str, ...]
    parent_id: int | None


@dataclass(frozen=True)
class RootCategory:
    id: int
    name_ar: str
    name_en: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "nameAr": self.name_ar, "nameEn": self.name_en}


@dataclass(frozen=True)
class GoodTypeNode:
    id: int
    name_ar: str
    name_en: str
    parent_id: int | None
    child_ids: tuple[int, ...] = ()

    @property
    def is_selectable(self) -> bool:
        return not self.child_ids

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nameAr": self.name_ar,
            "nameEn": self.name_en,
            "parentId": self.parent_id,
            "childIds": list(self.child_ids),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoodTypeNode:
        return cls(
            id=int(data["id"]),
            name_ar=str(data["nameAr"]),
            name_en=str(data["nameEn"]),
            parent_id=None if data.get("parentId") is None else int(data["parentId"]),
            child_ids=tuple(int(item) for item in data.get("childIds", ())),
        )


@dataclass(frozen=True)
class SearchTerm:
    root_good_type_id: int
    source_good_type_id: int
    raw_term: str
    normalized_term: str
    compact_term: str
    source_type: str
    language_hint: str
    is_cross_root_ambiguous: bool = False
    is_cross_good_type_ambiguous: bool = False

    def with_ambiguity(
        self,
        *,
        is_cross_root_ambiguous: bool,
        is_cross_good_type_ambiguous: bool,
    ) -> SearchTerm:
        return SearchTerm(
            root_good_type_id=self.root_good_type_id,
            source_good_type_id=self.source_good_type_id,
            raw_term=self.raw_term,
            normalized_term=self.normalized_term,
            compact_term=self.compact_term,
            source_type=self.source_type,
            language_hint=self.language_hint,
            is_cross_root_ambiguous=is_cross_root_ambiguous,
            is_cross_good_type_ambiguous=is_cross_good_type_ambiguous,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rootGoodTypeId": self.root_good_type_id,
            "sourceGoodTypeId": self.source_good_type_id,
            "rawTerm": self.raw_term,
            "normalizedTerm": self.normalized_term,
            "compactTerm": self.compact_term,
            "sourceType": self.source_type,
            "languageHint": self.language_hint,
            "isCrossRootAmbiguous": self.is_cross_root_ambiguous,
            "isCrossGoodTypeAmbiguous": self.is_cross_good_type_ambiguous,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SearchTerm:
        return cls(
            root_good_type_id=int(data["rootGoodTypeId"]),
            source_good_type_id=int(data["sourceGoodTypeId"]),
            raw_term=str(data["rawTerm"]),
            normalized_term=str(data["normalizedTerm"]),
            compact_term=str(data["compactTerm"]),
            source_type=str(data["sourceType"]),
            language_hint=str(data["languageHint"]),
            is_cross_root_ambiguous=bool(data.get("isCrossRootAmbiguous", False)),
            is_cross_good_type_ambiguous=bool(
                data.get("isCrossGoodTypeAmbiguous", False)
            ),
        )


@dataclass(frozen=True)
class Catalog:
    version: str
    source_sha256: str
    roots: dict[int, RootCategory]
    good_types: dict[int, GoodTypeNode]
    terms: tuple[SearchTerm, ...]

    @property
    def root_count(self) -> int:
        return len(self.roots)

    @property
    def term_count(self) -> int:
        return len(self.terms)

    @property
    def good_type_count(self) -> int:
        return len(self.good_types)

    @property
    def selectable_count(self) -> int:
        return sum(1 for node in self.good_types.values() if node.is_selectable)

    @property
    def selectable_terms(self) -> tuple[SearchTerm, ...]:
        return tuple(
            term for term in self.terms if self.is_selectable(term.source_good_type_id)
        )

    def root(self, root_id: int) -> RootCategory:
        return self.roots[root_id]

    def good_type(self, good_type_id: int) -> GoodTypeNode:
        return self.good_types[good_type_id]

    def is_selectable(self, good_type_id: int) -> bool:
        return self.good_types[good_type_id].is_selectable

    def root_id_for(self, good_type_id: int) -> int:
        current = self.good_types[good_type_id]
        seen: set[int] = set()
        while current.parent_id is not None:
            if current.id in seen:
                raise ValueError(f"Cycle detected at good_type {current.id}")
            seen.add(current.id)
            current = self.good_types[current.parent_id]
        return current.id

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "sourceSha256": self.source_sha256,
            "roots": [root.to_dict() for root in self.roots.values()],
            "goodTypes": [node.to_dict() for node in self.good_types.values()],
            "terms": [term.to_dict() for term in self.terms],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Catalog:
        if "goodTypes" not in data:
            raise ValueError("Catalog artifact is missing goodTypes; rebuild it from SQL")
        roots = {
            int(item["id"]): RootCategory(
                id=int(item["id"]),
                name_ar=str(item["nameAr"]),
                name_en=str(item["nameEn"]),
            )
            for item in data["roots"]
        }
        good_types = {
            int(item["id"]): GoodTypeNode.from_dict(item)
            for item in data["goodTypes"]
        }
        terms = tuple(SearchTerm.from_dict(item) for item in data["terms"])
        return cls(
            version=str(data["version"]),
            source_sha256=str(data["sourceSha256"]),
            roots=roots,
            good_types=good_types,
            terms=terms,
        )
