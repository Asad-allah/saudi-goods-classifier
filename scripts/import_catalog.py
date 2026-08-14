from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.catalog.importer import load_catalog_from_sql


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Dandan good_types catalog.")
    parser.add_argument("--source", required=True, help="Path to sub_db.sql")
    parser.add_argument(
        "--output",
        default="storage/catalog/catalog.json",
        help="Output catalog artifact path.",
    )
    parser.add_argument("--version", default="", help="Optional catalog version.")
    args = parser.parse_args()

    catalog = load_catalog_from_sql(args.source, version=args.version)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        f"Imported catalog {catalog.version}: "
        f"{catalog.root_count} roots, "
        f"{catalog.good_type_count} good types, "
        f"{catalog.selectable_count} selectable, "
        f"{catalog.term_count} search terms"
    )


if __name__ == "__main__":
    main()
