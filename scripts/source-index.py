#!/usr/bin/env python3
"""Print a compact view of the Analysis PDF source matrix.

The matrix (docs/architecture/analysis_pdf_source_index.json) is ~850 KB; read
it through this script instead of opening the whole file.

  python scripts/source-index.py --issue 236            # items for one Issue
  python scripts/source-index.py --issue 236 --families # family contracts only
  python scripts/source-index.py --id AM1/24            # one item or family, as JSON
  python scripts/source-index.py --summary              # summary block
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "docs/architecture/analysis_pdf_source_index.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--issue", type=int, help="filter items/families by Issue number")
    parser.add_argument("--families", action="store_true", help="list family contracts")
    parser.add_argument("--id", help="print one item id or family contract id as JSON")
    parser.add_argument("--summary", action="store_true", help="print the summary block")
    args = parser.parse_args()
    data = json.loads(INDEX.read_text(encoding="utf-8"))

    if args.summary:
        print(json.dumps(data.get("summary"), indent=2, ensure_ascii=False))
        return 0
    if args.id:
        found = [item for item in data["items"] if item["id"] == args.id]
        if args.id in data["family_contracts"]:
            found.append({args.id: data["family_contracts"][args.id]})
        if not found:
            print(f"no item or family contract {args.id!r}", file=sys.stderr)
            return 1
        print(json.dumps(found, indent=2, ensure_ascii=False))
        return 0
    if args.families:
        for key, family in data["family_contracts"].items():
            if args.issue is None or family.get("issue") == args.issue:
                status = family.get("delivery", {}).get("status", family.get("existing_coverage"))
                print(f"{key}\t{family.get('family')}\t{family.get('contract')}\t{status}")
        return 0
    for item in data["items"]:
        if args.issue is None or item.get("issue") == args.issue:
            pages = ",".join(map(str, item.get("pages", [])))
            print(f"{item['id']}\tp{pages}\t{item.get('family')}\t{item.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
