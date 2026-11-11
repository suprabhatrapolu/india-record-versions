#!/usr/bin/env python3
"""Validate the india-record-versions v0 archive.

Checks (per the task spec):
  1. Every versions.csv row has a source_url, an existing source_file, and verified=yes.
  2. superseded_on integrity: for a given indicator+period, superseded_on must equal the
     published_on of the later row for the same indicator+period (or be blank).
  3. claims.csv version_row_then / version_row_now point at rows that actually exist in
     versions.csv (ref format: indicator/period/published_on/value).
  4. No duplicate rows in either CSV (by full logical key).
  5. sources/manifest.csv: every source file listed exists and matches its SHA-256; every
     source_file in versions.csv and every claim_url is covered by the manifest; every file
     under sources/ is listed.
  6. Each claim's version_row_now is the latest version held for that indicator+period.
  7. Re-run build_table.py and confirm the "Before and after" table in README.md is in
     sync with what build_table.py would now generate.

Exit code 0 = all checks pass; non-zero = at least one failure. Prints a human summary.
"""
import csv
import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

VERSIONS = os.path.join(ROOT, "data", "versions.csv")
CLAIMS = os.path.join(ROOT, "data", "claims.csv")
SOURCES = os.path.join(ROOT, "sources")
MANIFEST = os.path.join(SOURCES, "manifest.csv")
README = os.path.join(ROOT, "README.md")

VER_COLS = [
    "indicator", "reference_period", "value", "unit", "series", "estimate_type",
    "published_on", "superseded_on", "source_title", "source_url", "source_file",
    "page_or_table", "verified",
]
CLAIM_COLS = [
    "claim_text", "speaker_or_outlet", "claim_date", "claim_url", "indicator",
    "reference_period", "value_claimed", "matches_record_on_claim_date",
    "matches_record_today", "version_row_then", "version_row_now",
]


def read_rows(path, want_cols):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        got = reader.fieldnames or []
        rows = list(reader)
    missing = [c for c in want_cols if c not in got]
    extra = [c for c in got if c not in want_cols]
    return rows, missing, extra


def main():
    errors, notes = [], []

    vrows, vmiss, vextra = read_rows(VERSIONS, VER_COLS)
    crow, cmass, cextra = read_rows(CLAIMS, CLAIM_COLS)
    if vmiss:
        errors.append("versions.csv missing columns: " + ", ".join(vmiss))
    if cmass:
        errors.append("claims.csv missing columns: " + ", ".join(cmass))
    if vextra:
        notes.append("versions.csv has unexpected columns: " + ", ".join(vextra))

    # ---- versions row checks ----
    vkey_refs = set()
    logical_keys = []
    for i, r in enumerate(vrows, start=2):  # +1 header
        tag = "versions.csv line {}".format(i)
        if not r.get("source_url"):
            errors.append(tag + ": missing source_url")
        sf = r.get("source_file") or ""
        if not os.path.isfile(os.path.join(SOURCES, sf)):
            errors.append(tag + ": source_file not found under sources/: " + sf)
        if r.get("verified") != "yes":
            errors.append(tag + ": verified must be 'yes' (got %r)" % r.get("verified"))
        if r.get("unit") not in ("percent", "index"):
            errors.append(tag + ": unit must be percent/index (got %r)" % r.get("unit"))
        ref = "/".join([r.get("indicator", ""), r.get("reference_period", ""),
                        r.get("published_on", ""), r.get("value", "")])
        vkey_refs.add(ref)
        logical_keys.append((r["indicator"], r["reference_period"],
                             r["series"], r["published_on"], r["value"]))

    # duplicates
    seen = set()
    dupes = [k for k in logical_keys if k in seen or seen.add(k)]
    if dupes:
        for d in dupes:
            errors.append("duplicate versions row: " + " | ".join(d))

    # superseded_on integrity, grouped by indicator+period
    groups = {}
    for r in vrows:
        groups.setdefault((r["indicator"], r["reference_period"]), []).append(r)
    for (ind, per), rs in groups.items():
        pubs = sorted(rs, key=lambda r: r["published_on"])
        if len(rs) == 1:
            if pubs[0].get("superseded_on"):
                errors.append(
                    "superseded_on set but no later version exists for %s/%s: %s"
                    % (ind, per, pubs[0]["superseded_on"]))
        else:
            for j, r in enumerate(pubs):
                if j == len(pubs) - 1:
                    if r.get("superseded_on"):
                        errors.append(
                            "latest version for %s/%s should have blank superseded_on (got %s)"
                            % (ind, per, r["superseded_on"]))
                else:
                    expected = pubs[j + 1]["published_on"]
                    got = r.get("superseded_on") or ""
                    if got != expected:
                        errors.append(
                            "superseded_on mismatch for %s/%s (%s): expected %s, got %r"
                            % (ind, per, r["published_on"], expected, got))

    # ---- manifest checks ----
    manifest_files, manifest_urls = set(), set()
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        mrows = list(csv.DictReader(f))
    for i, m in enumerate(mrows, start=2):
        tag = "manifest.csv line {}".format(i)
        fn = m.get("file", "")
        if fn in manifest_files:
            errors.append(tag + ": duplicate manifest entry: " + fn)
        manifest_files.add(fn)
        manifest_urls.add(m.get("url", ""))
        for col in ("url", "date_retrieved", "sha256"):
            if not m.get(col):
                errors.append(tag + ": missing " + col)
        path = os.path.join(SOURCES, fn)
        if not os.path.isfile(path):
            errors.append(tag + ": listed file does not exist: " + fn)
            continue
        with open(path, "rb") as fh:
            actual = hashlib.sha256(fh.read()).hexdigest()
        if actual != m.get("sha256", "").lower():
            errors.append(tag + ": SHA-256 mismatch for {} (manifest {}, actual {})".format(
                fn, m.get("sha256"), actual))
    for fn in sorted(os.listdir(SOURCES)):
        if fn != "manifest.csv" and fn not in manifest_files:
            errors.append("sources/" + fn + " is not listed in manifest.csv")
    for i, r in enumerate(vrows, start=2):
        if r.get("source_file") not in manifest_files:
            errors.append("versions.csv line {}: source_file not in manifest: {}".format(
                i, r.get("source_file")))
        if r.get("source_url") not in manifest_urls:
            errors.append("versions.csv line {}: source_url not in manifest: {}".format(
                i, r.get("source_url")))
    notes.append("manifest: {} files checked against SHA-256".format(len(mrows)))

    # ---- claims row checks ----
    latest_ref = {}
    for r in vrows:
        k = (r["indicator"], r["reference_period"])
        if k not in latest_ref or r["published_on"] > latest_ref[k][0]:
            latest_ref[k] = (r["published_on"], "/".join(
                [r["indicator"], r["reference_period"], r["published_on"], r["value"]]))
    clkeys = []
    for i, r in enumerate(crow, start=2):
        tag = "claims.csv line {}".format(i)
        for field in ("version_row_then", "version_row_now"):
            ref = r.get(field, "")
            if ref not in vkey_refs:
                errors.append(tag + ": {} does not match any versions.csv row: {}".format(field, ref))
        if r.get("claim_url") not in manifest_urls:
            errors.append(tag + ": claim_url not saved in manifest: " + r.get("claim_url", ""))
        lk = (r.get("indicator"), r.get("reference_period"))
        if lk in latest_ref and r.get("version_row_now") != latest_ref[lk][1]:
            errors.append(tag + ": version_row_now is not the latest version held ({})".format(
                latest_ref[lk][1]))
        if r.get("matches_record_on_claim_date") not in ("yes", "no"):
            errors.append(tag + ": matches_record_on_claim_date must be yes/no")
        if r.get("matches_record_today") not in ("yes", "no"):
            errors.append(tag + ": matches_record_today must be yes/no")
        clkeys.append((r["indicator"], r["reference_period"], r["claim_date"], r["value_claimed"], r["claim_url"]))
    seen2 = set()
    cl_dupes = [k for k in clkeys if k in seen2 or seen2.add(k)]
    if cl_dupes:
        for d in cl_dupes:
            errors.append("duplicate claims row: " + " | ".join(d))

    # ---- table sync ----
    pre = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_table.py")],
                         capture_output=True, text=True)
    if pre.returncode != 0:
        errors.append("build_table.py failed: " + pre.stderr.strip())
    else:
        newtext = open(README, encoding="utf-8").read()
        # Regenerate in-memory and confirm it is what now sits in README.
        import build_table
        expected_block = build_table.build(vrows)
        begin = "<!-- BEGIN GENERATED TABLE -->"
        end = "<!-- END GENERATED TABLE -->"
        if begin not in newtext or end not in newtext:
            errors.append("README.md missing generated-table markers")
        else:
            cur = newtext.split(begin, 1)[1].split(end, 1)[0]
            if cur != expected_block:
                errors.append("README 'Before and after' table is out of sync with versions.csv; re-run build_table.py")
            else:
                notes.append("README table is in sync with versions.csv")

    print("=" * 60)
    print("india-record-versions validation")
    print("=" * 60)
    print("versions.csv rows: {}".format(len(vrows)))
    print("claims.csv rows:   {}".format(len(crow)))
    print("  revised indicator+periods (>=2 versions): "
          "{}".format(sum(1 for rs in groups.values() if len(rs) > 1)))
    for n in notes:
        print("  - " + n)
    if errors:
        print("\nFAILURES ({}):".format(len(errors)))
        for e in errors:
            print("  ! " + e)
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
