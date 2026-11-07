#!/usr/bin/env python3
"""Do the AGENTS.md "After a merge" project steps in one command.

  python scripts/finish-issue.py 236           # show the plan, change nothing
  python scripts/finish-issue.py 236 --apply   # close, Status Done, clear Order, renumber

Needs `gh` signed in with the `project` scope (`gh auth refresh -s project`).
Prints only a short summary so agents do not have to read project JSON.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

OWNER = "whatvlad"
PROJECT = "1"
REPO = "whatvlad/practiceloop"


def gh(*args: str) -> str:
    result = subprocess.run(  # noqa: S603
        ["gh", *args],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"gh {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout


def gh_json(*args: str) -> Any:
    return json.loads(gh(*args))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("issue", type=int)
    parser.add_argument("--apply", action="store_true", help="make the changes")
    args = parser.parse_args()

    project_id = gh_json("project", "view", PROJECT, "--owner", OWNER, "--format", "json")["id"]
    fields = gh_json("project", "field-list", PROJECT, "--owner", OWNER, "--format", "json")[
        "fields"
    ]
    by_name = {field["name"]: field for field in fields}
    status_field, order_field = by_name["Status"], by_name["Order"]
    done_id = next(o["id"] for o in status_field["options"] if o["name"] == "Done")
    items = gh_json(
        "project", "item-list", PROJECT, "--owner", OWNER, "--format", "json", "--limit", "1000"
    )["items"]
    open_numbers = {
        issue["number"]
        for issue in gh_json(
            "issue",
            "list",
            "--repo",
            REPO,
            "--state",
            "open",
            "--limit",
            "1000",
            "--json",
            "number",
        )
    }

    target = next((i for i in items if i.get("content", {}).get("number") == args.issue), None)
    if target is None:
        sys.exit(f"Issue #{args.issue} is not in the project")

    queue = sorted(
        (
            i
            for i in items
            if i is not target
            and i.get("content", {}).get("number") in open_numbers
            and i.get("order") is not None
        ),
        key=lambda i: i["order"],
    )
    renumber = [
        (item, position)
        for position, item in enumerate(queue, start=1)
        if item["order"] != position
    ]

    print(
        f"#{args.issue}: {'open -> close' if args.issue in open_numbers else 'already closed'}; "
        f"Status {target.get('status')} -> Done; Order {target.get('order')} -> cleared"
    )
    for item, position in renumber:
        print(f"#{item['content']['number']}: Order {item['order']} -> {position}")
    if not args.apply:
        print("Dry run. Re-run with --apply to make these changes.")
        return 0

    if args.issue in open_numbers:
        gh("issue", "close", str(args.issue), "--repo", REPO)
    edit = ("project", "item-edit", "--project-id", project_id, "--id", target["id"])
    gh(*edit, "--field-id", status_field["id"], "--single-select-option-id", done_id)
    if target.get("order") is not None:
        gh(*edit, "--field-id", order_field["id"], "--clear")
    for item, position in renumber:
        gh(
            "project",
            "item-edit",
            "--project-id",
            project_id,
            "--id",
            item["id"],
            "--field-id",
            order_field["id"],
            "--number",
            str(position),
        )

    after = gh_json(
        "project", "item-list", PROJECT, "--owner", OWNER, "--format", "json", "--limit", "1000"
    )["items"]
    orders = sorted(
        i["order"]
        for i in after
        if i.get("content", {}).get("number") in open_numbers - {args.issue}
        and i.get("order") is not None
    )
    ok = orders == list(range(1, len(orders) + 1))
    print(
        f"Done. Open queue Order values: 1..{len(orders)}",
        "OK" if ok else f"NOT continuous: {orders}",
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
