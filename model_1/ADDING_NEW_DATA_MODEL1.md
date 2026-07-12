# Adding a New Data Series to the Econ Model

Quick reference for wiring a new variable into `econ_model.py`.

---

## TL;DR — the edits

| # | File | What to add | Required? |
|---|------|-------------|-----------|
| 1 | The `L0`–`L5` source script | The new column on the returned DataFrame | **Always** |
| 2 | `module0_data_get_all.py` → `LAG_N` list | Prefixed column name | **Yes**, if it has any publication lag |
| 3 | `module1_data_standardize.py` → `TIEBREAKER_*` dict | Prefixed column name | Recommended (see below) |
| 4 | `module8_added_factors.py` → `COMPOSITE_CANDIDATES` | Prefixed column name | Optional |

Everything else (aggregation, prefixing, z-score standardization, factor
assignment) happens **automatically**.

---

## Step 1 — Add the column in the source script (always)

In the relevant `L*_*.py` script, add your series as one more column on the
DataFrame the function returns. Keep it:

- **Monthly**, month-start (`MS`) `DatetimeIndex` — resample/forward-fill if the
  raw source is quarterly/weekly/daily (copy the pattern of an existing column).
- **Named bare** — do *not* prefix it. Use e.g. `mortgage_90plus_delinquency`,
  **not** `L2_mortgage_90plus_delinquency`.

The column flows up through that level's `L*_all_data_get.py` automatically
(those aggregators just `pd.concat(..., axis=1)`). **No edit needed there.**

> Exception: adding a brand-new *script* (not just a column) — you must import
> and add its function call to the relevant `L*_all_data_get.py`.

### The prefix is added for you

`module0_data_get_all.py` calls `prefix_columns(df, 'L2_')`, so
`mortgage_90plus_delinquency` becomes `L2_mortgage_90plus_delinquency`
downstream. **Use the prefixed name in Steps 2–4 below.**

---

## Step 2 — Register the publication lag (`module0_data_get_all.py`)

Add the **prefixed** name to the correct `LAG_N` list so the series is shifted
forward by its real release delay (avoids look-ahead bias in backtests):

- `LAG_0` — real-time / market data (rates, VIX, spreads)
- `LAG_1` — ~1-month lag (monthly BLS/Fed releases)
- `LAG_2` — ~2-month lag (quarterly Fed/BEA data, e.g. delinquency)
- `LAG_3`, `LAG_12` — longer lags

**If you skip this:** `apply_publication_lags()` prints a `WARNING: ... no lag
assignment` and the series is **not** shifted. The model runs, but with
look-ahead bias. Treat this step as mandatory.

---

## Step 3 — Tiebreaker bucket (`module1_data_standardize.py`)

Each series is auto-classified into Growth / Discount / Risk_Premium by its R²
vs the SPX target. A **tiebreaker dict** only decides cases where the top two
buckets are too close to call. Add the prefixed name to the matching set:
`TIEBREAKER_GROWTH`, `TIEBREAKER_DISCOUNT`, `TIEBREAKER_RISK_PREMIUM`
(or `TIEBREAKER_EXCLUDE` to deliberately leave it out).

**Conditional, but recommended:** if the series passes the R²/p-value filter and
its classification is ambiguous and it's in *no* tiebreaker dict, it's logged as
`tiebreaker_missing` and dropped to UNUSED. Adding it guarantees a deterministic
bucket. (A series that clearly wins one bucket, or that fails the filter, ignores
the tiebreaker entirely — so this isn't strictly always required.)

---

## Step 4 — Composite candidate (`module8_added_factors.py`) — optional

Add the prefixed name to a `COMPOSITE_CANDIDATES` category
(`Financial_Stress`, `Labor`, `Consumer`, `Corporate`, `Government`) only if you
want the series eligible to be recycled into a new composite factor in the
exploratory Step 8. **Purely diagnostic — the core 3-factor model is unaffected
if you skip it.**

---

## Do NOT touch

These hard-code the 3 factor anchors and target variables; they are read-only and
should not change when adding an ordinary series:

- `module1_data_standardize.py` — `ANCHOR_GROWTH/DISCOUNT/RISK_PREMIUM`
- `module2_factor_*.py` — anchor sign-correction references
- `module5_fundamental_valuation.py` — `anchor_map`
- `module7_final_results.py` — `anchor_map`, target-horizon map
- `module8_added_factors.py` — `ALWAYS_EXCLUDE`

---

## Checklist

```
[ ] 1. Column added to L*_*.py, monthly MS index, bare name
[ ] 2. Prefixed name added to a LAG_N list in module0_data_get_all.py
[ ] 3. Prefixed name added to a TIEBREAKER_* dict in module1_data_standardize.py
[ ] 4. (optional) Prefixed name added to COMPOSITE_CANDIDATES in module8_added_factors.py
```
