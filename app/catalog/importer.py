from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from app.catalog.models import Catalog, GoodType, GoodTypeNode, RootCategory, SearchTerm
from app.nlp.language import detect_language
from app.nlp.normalizer import compact_text, normalize_text


class CatalogIntegrityError(ValueError):
    pass


def _parse_sql_tuple(line: str) -> list[str | None]:
    value = line.strip().rstrip(",;")
    if not value.startswith("(") or not value.endswith(")"):
        raise ValueError(f"Not a SQL tuple row: {line[:80]}")

    items: list[str | None] = []
    token: list[str] = []
    in_string = False
    index = 1
    end = len(value) - 1

    while index < end:
        char = value[index]
        if in_string:
            if char == "\\" and index + 1 < end:
                token.append(value[index + 1])
                index += 2
                continue
            if char == "'":
                in_string = False
                index += 1
                continue
            token.append(char)
            index += 1
            continue

        if char == "'":
            in_string = True
            index += 1
            continue
        if char == ",":
            raw = "".join(token).strip()
            items.append(None if raw.upper() == "NULL" else raw)
            token = []
            index += 1
            continue

        token.append(char)
        index += 1

    raw = "".join(token).strip()
    items.append(None if raw.upper() == "NULL" else raw)
    return items


def _parse_common_names(raw_value: str | None) -> tuple[str, ...]:
    if not raw_value:
        return ()
    try:
        names = json.loads(raw_value)
    except json.JSONDecodeError:
        return ()
    if not isinstance(names, list):
        return ()
    return tuple(name.strip() for name in names if isinstance(name, str) and name.strip())


def load_good_types_from_sql(path: str | Path) -> list[GoodType]:
    sql_path = Path(path)
    rows: list[GoodType] = []
    inside_good_types_insert = False

    for line in sql_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "INSERT INTO `good_types`" in line:
            inside_good_types_insert = True
            continue
        if not inside_good_types_insert:
            continue
        if not line.lstrip().startswith("("):
            continue

        values = _parse_sql_tuple(line)
        if len(values) < 5:
            continue
        rows.append(
            GoodType(
                id=int(values[0] or 0),
                ar_name=str(values[1] or ""),
                en_name=str(values[2] or ""),
                common_names=_parse_common_names(values[3]),
                parent_id=None if values[4] is None else int(values[4]),
            )
        )
        if line.rstrip().endswith(";"):
            break

    if not rows:
        raise CatalogIntegrityError(f"No good_types rows found in {sql_path}")
    return rows


def _source_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _default_version(source_sha256: str) -> str:
    date_part = datetime.now(UTC).strftime("%Y-%m-%d")
    return f"{date_part}.{source_sha256[:8]}"


def build_catalog(
    good_types: list[GoodType],
    *,
    source_sha256: str = "",
    version: str = "",
) -> Catalog:
    by_id = {item.id: item for item in good_types}
    child_ids_by_parent: dict[int, list[int]] = defaultdict(list)
    for item in good_types:
        if item.parent_id is not None:
            child_ids_by_parent[item.parent_id].append(item.id)

    good_type_nodes = {
        item.id: GoodTypeNode(
            id=item.id,
            name_ar=item.ar_name,
            name_en=item.en_name,
            parent_id=item.parent_id,
            child_ids=tuple(sorted(child_ids_by_parent.get(item.id, ()))),
        )
        for item in good_types
    }
    roots = {
        item.id: RootCategory(id=item.id, name_ar=item.ar_name, name_en=item.en_name)
        for item in good_types
        if item.parent_id is None
    }
    if not roots:
        raise CatalogIntegrityError("good_types contains no root categories")

    def root_id_for(item: GoodType) -> int:
        seen: set[int] = set()
        current = item
        while current.parent_id is not None:
            if current.id in seen:
                raise CatalogIntegrityError(f"Cycle detected at good_type {current.id}")
            seen.add(current.id)
            parent = by_id.get(current.parent_id)
            if parent is None:
                raise CatalogIntegrityError(
                    f"Missing parent {current.parent_id} for good_type {current.id}"
                )
            current = parent
        return current.id

    draft_terms: list[SearchTerm] = []
    seen_pairs: set[tuple[int, str, str]] = set()

    for item in good_types:
        root_id = root_id_for(item)
        term_sources: list[tuple[str, str]] = [
            (item.ar_name, "ROOT_NAME" if item.parent_id is None else "CHILD_NAME"),
        ]
        term_sources.extend((name, "COMMON_NAME") for name in item.common_names)

        for raw_term, source_type in term_sources:
            normalized = normalize_text(raw_term)
            if not normalized:
                continue
            compact = compact_text(normalized)
            key = (item.id, normalized, compact)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            draft_terms.append(
                SearchTerm(
                    root_good_type_id=root_id,
                    source_good_type_id=item.id,
                    raw_term=raw_term.strip(),
                    normalized_term=normalized,
                    compact_term=compact,
                    source_type=source_type,
                    language_hint=detect_language(raw_term),
                )
            )

    roots_by_normalized: dict[str, set[int]] = defaultdict(set)
    good_types_by_normalized: dict[str, set[int]] = defaultdict(set)
    for term in draft_terms:
        roots_by_normalized[term.normalized_term].add(term.root_good_type_id)
        good_types_by_normalized[term.normalized_term].add(term.source_good_type_id)
        if term.compact_term:
            roots_by_normalized[term.compact_term].add(term.root_good_type_id)
            good_types_by_normalized[term.compact_term].add(term.source_good_type_id)

    terms = tuple(
        term.with_ambiguity(
            is_cross_root_ambiguous=(
                len(roots_by_normalized[term.normalized_term]) > 1
                or len(roots_by_normalized[term.compact_term]) > 1
            ),
            is_cross_good_type_ambiguous=(
                len(good_types_by_normalized[term.normalized_term]) > 1
                or len(good_types_by_normalized[term.compact_term]) > 1
            ),
        )
        for term in draft_terms
    )

    return Catalog(
        version=version or _default_version(source_sha256 or "local"),
        source_sha256=source_sha256,
        roots=dict(sorted(roots.items())),
        good_types=dict(sorted(good_type_nodes.items())),
        terms=terms,
    )


def load_catalog_from_sql(path: str | Path, *, version: str = "") -> Catalog:
    source_sha256 = _source_sha256(path)
    return build_catalog(
        load_good_types_from_sql(path),
        source_sha256=source_sha256,
        version=version,
    )


def load_catalog_artifact(path: str | Path) -> Catalog:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Catalog.from_dict(data)
