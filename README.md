# India Record Versions (v0)

What India's headline statistics said on each date, with sources.

This archive records, for a handful of India's headline statistics, the *different
versions of the official figure that were on the record on different dates* — and
links those dated versions to public statements that quoted them. Every value in
`data/versions.csv` was read from a primary government release (MoSPI / PIB) that
has been saved under `sources/` and listed in `sources/manifest.csv`.

## Before and after

The table below is generated from `data/versions.csv` by `scripts/build_table.py`
(re-run it after changing the data; `scripts/validate.py` checks they stay in sync).
A row appears in the "revised" table when we hold two or more versions of the same
indicator for the same period — typically because the statistical base year or
deflator changed. Rows we have seen only once in this archive are listed separately.

<!-- BEGIN GENERATED TABLE -->
**Before and after** (revised figures, per indicator + period; where three or more versions are held, the first and the latest are shown):

| Indicator | Period | Earlier value | Later value | Earlier series (published) | Later series (published) | Versions held |
|---|---|---|---|---|---|---|
| iip_general_growth | 2024-25 | 6.4 | 5.7 | IIP base 2022-23 WPI-deflated Quick Estimates (2026-06-01) | IIP base 2022-23 PPI-deflated Quick Estimates (2026-06-29) | 2 |
| iip_general_index | April 2026 | 118.9 | 118.2 | IIP base 2022-23 WPI-deflated Quick Estimates (2026-06-01) | IIP base 2022-23 PPI-deflated not named in release (2026-06-29) | 2 |
| real_gdp_growth | 2023-24 | 8.2 | 7.3 | GDP base 2011-12 Provisional Estimates (2024-05-31) | GDP base 2022-23 Updated Final Estimates (2026-08-31) | 4 |
| real_gdp_growth | 2024-25 | 6.5 | 7.2 | GDP base 2011-12 Provisional Estimates (2025-05-30) | GDP base 2022-23 First Revised Estimates (updated) (2026-08-31) | 3 |


**Released once in this archive** (no earlier version recorded here):

| Indicator | Period | Value (unit) | Series & type | Published |
|---|---|---|---|---|
| cpi_inflation_yoy | December 2025 | 1.33 percent | CPI base 2012 Final | 2026-02-12 |
| cpi_inflation_yoy | January 2026 | 2.75 percent | CPI base 2024 Provisional | 2026-02-12 |
| iip_general_growth | April 2026 | 4.9 percent | IIP base 2022-23 WPI-deflated Quick Estimates | 2026-06-01 |
| iip_general_growth | May 2026 | 5.1 percent | IIP base 2022-23 PPI-deflated Quick Estimates | 2026-06-29 |
| iip_general_index | May 2026 | 122.7 index | IIP base 2022-23 PPI-deflated Quick Estimates | 2026-06-29 |

<!-- END GENERATED TABLE -->

The GDP pairs differ in both base year and estimate stage; the 2026-08-31 rows are the updated estimates from the National Accounts Statistics - 2026 publication, which incorporated the new PPI / IIP base-2022-23 series. The industrial production pairs differ in the deflator used; the April 2026 figure also reflects updated production data. The 2023-24 chain is 8.2 (2024-05-31) -> 9.2 (2025-02-28) -> 7.2 (2026-02-27) -> 7.3 (2026-08-31); the 2024-25 chain is 6.5 (2025-05-30) -> 7.1 (2026-02-27) -> 7.2 (2026-08-31).

## How to read the columns

- **indicator** — which series: `real_gdp_growth`, `iip_general_growth`,
  `iip_general_index`, `cpi_inflation_yoy`.
- **reference_period** — the period the figure describes (financial year `2023-24`,
  or a month `April 2026`).
- **value** / **unit** — the number and its unit (`percent`, `index`).
- **series** — the base-year / deflator version of the series, e.g. `GDP base 2011-12`,
  `GDP base 2022-23`, `IIP base 2022-23 WPI-deflated`, `IIP base 2022-23 PPI-deflated`,
  `CPI base 2012`, `CPI base 2024`.
- **estimate_type** — the release's own wording: `Provisional Estimates`,
  `First Revised Estimates`, `Quick Estimates`, `Final`, etc. Some labels are
  descriptive: `Estimates (new base year)` (the release names only 2024-25 as First
  Revised in the 2022-23-base series), `not named in release`, `Updated Final
  Estimates` and `First Revised Estimates (updated)` (both from the National Accounts
  Statistics - 2026 publication, which republished those years' estimates updated
  with the new price and industrial series).
- **published_on** — the date the version carrying this value was published (ISO date).
- **superseded_on** — the `published_on` of the *next* version we hold for the same
  indicator + period, else blank. For the latest version we hold, it is blank.
- **source_title / source_url / source_file / page_or_table** — where the figure was
  read from. `source_file` is a saved copy under `sources/`; `page_or_table` names the
  exact table, statement or page.
- **verified** — always `yes` here, meaning the figure was read in the saved primary
  release. (Rows are only included if they verified.)

`data/claims.csv` holds public statements that quoted a figure: what was claimed, who
said it, when, a link, and whether the claim matched the record *on the date it was
made* (`version_row_then`) versus *today* (`version_row_now`). A claim that quoted a
figure later revised will match its then-version but not the current one.

## Why this exists

Official statistics are revised: the base year of the index changes, the deflator
changes, and a "provisional" figure is replaced by a "final" one. So the number that
was *the* figure on one date is not the number on a later date, and a claim that was
correct when made can look wrong later. This repo tracks that directly: it records
the dated versions and ties them to the claims that quoted them. The problem is not
rhetorical. In my audit of 4,669 news claims about US economic data, 17.8% of claims the record supported at publication are contradicted by the revised record today; this archive applies that observation to Indian headline statistics.

## What this is NOT

- It is **v0**: a small, hand-verified start, not a complete archive of Indian
  statistics.
- It makes **no judgement about any speaker** who quoted a figure. Revised figures
  were not wrong when they were stated; the record changed afterwards.
- It is **not** a current-data dashboard.

**Related work.** [India Data Review](https://github.com/kartiks/india-data-review)
collects the *current* official data (GDP, CPI, PLFS, HCES, budget assumptions, and
forecasts from multiple agencies) into a live site, retaining source snapshots so its
revision history builds up over time. This repo is different in purpose: it records
*dated versions* of the same headline figures and *links them to the public claims that
quoted them*, so you can see which statement was right on which date. It complements
rather than replaces a current-data collection.

## Planned next

- Add the matching CPI month under *both* bases where available, and the IIP old-base
  monthly values published with the 2022-23 series.
- Expand claims from government releases to named public statements (ministers, budget
  documents, the Economic Survey, major newspapers), recorded with the date each was made.

## Data provenance

- Primary sources are saved under `sources/` (HTML press pages and two PDF press notes)
  and listed in `sources/manifest.csv` with URL, retrieval date (2026-11-11 or 2026-11-12) and
  SHA-256. The same folder holds saved copies of the News On AIR pages that the
  third-party rows in `data/claims.csv` point to.
- `data/versions.csv` and `data/claims.csv` are the records.

## Files

- `data/versions.csv` — dated versions of each figure.
- `data/claims.csv` — public claims and which record version they match, then and now.
- `sources/` — saved primary releases + `manifest.csv` (integrity hashes).
- `scripts/validate.py` — checks the archive (run `python scripts/validate.py`).
- `scripts/build_table.py` — regenerates the "Before and after" table in this README.

---

**Author.** Suprabhat Rapolu, independent researcher, India. Contact: suprabhat@dirmacs.com.

**Licensing.** Code: MIT (`LICENSE`). Data: CC BY 4.0 (`LICENSE-DATA`). See
`CITATION.cff`.
