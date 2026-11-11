#!/usr/bin/env python3
"""Regenerate the "Before and after" table in README.md from data/versions.csv.

The table is written between the BEGIN/END markers in README.md so it can
never drift from the data. Run:  python scripts/build_table.py
"""
import csv
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "versions.csv")
README = os.path.join(ROOT, "README.md")
BEGIN = "<!-- BEGIN GENERATED TABLE -->"
END = "<!-- END GENERATED TABLE -->"


def load_versions():
    rows = []
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def build(rows):
    by_key = {}
    for r in rows:
        key = (r["indicator"], r["reference_period"])
        by_key.setdefault(key, []).append(r)

    def sortk(rs):
        return sorted(rs, key=lambda r: (r["published_on"], r["series"], r["value"]))

    out = io.StringIO()
    out.write("\n")
    out.write(
        "**Before and after** (revised figures, per indicator + period; where three or "
        "more versions are held, the first and the latest are shown):\n\n"
    )
    out.write(
        "| Indicator | Period | Earlier value | Later value | "
        "Earlier series (published) | Later series (published) | Versions held |\n"
        "|---|---|---|---|---|---|---|\n"
    )
    revised = []
    single = []
    for key in sorted(by_key):
        rs = sortk(by_key[key])
        if len(rs) >= 2:
            first, last = rs[0], rs[-1]
            revised.append(
                "| {} | {} | {} | {} | {} ({}) | {} ({}) | {} |\n".format(
                    key[0],
                    key[1],
                    first["value"],
                    last["value"],
                    first["series"] + " " + first["estimate_type"],
                    first["published_on"],
                    last["series"] + " " + last["estimate_type"],
                    last["published_on"],
                    len(rs),
                )
            )
        else:
            r = rs[0]
            single.append(
                "| {} | {} | {} {} | {} | {} |\n".format(
                    r["indicator"],
                    r["reference_period"],
                    r["value"],
                    r["unit"],
                    r["series"] + " " + r["estimate_type"],
                    r["published_on"],
                )
            )

    out.write("".join(revised))
    out.write("\n\n**Released once in this archive** (no earlier version recorded here):\n\n")
    out.write("| Indicator | Period | Value (unit) | Series & type | Published |\n|---|---|---|---|---|\n")
    out.write("".join(single))
    out.write("\n")
    return out.getvalue()


def main():
    rows = load_versions()
    block = build(rows)
    text = open(README, encoding="utf-8").read()
    if BEGIN not in text or END not in text:
        raise SystemExit("README.md is missing the generated-table markers; cannot update.")
    pre, rest = text.split(BEGIN, 1)
    post = rest.split(END, 1)[1]
    new = pre + BEGIN + block + END + post
    open(README, "w", encoding="utf-8").write(new)
    print("Updated the generated table in README.md from", len(rows), "version rows.")


if __name__ == "__main__":
    main()
