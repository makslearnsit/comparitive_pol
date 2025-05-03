# family_stats_family_blocks.py
# -*- coding: utf-8 -*-
"""
Блоки:  govt1  →  govt0  →  кожен group  →  total
для кожної family, метрики mean / std / se.
"""

import math, pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT  = BASE_DIR / "Data_Base_Group7 (all in).xlsx"
OUTPUT = BASE_DIR / "family_blocks_stats.xlsx"

VARIABLES = [
    "refugees", "weapons", "energy_costs", "ua_eu", "eu_foreign",
    "eu_intmark", "eu_position", "eu_cohesion", "eu_budgets", "eu_asylum",
    "redistribution", "deregulation", "protectionism", "climate_change",
    "environment", "spendvtax", "immigrate_policy", "womens_rights",
    "lgbtq_rights", "samesex_marriage", "religious_principles",
    "ethnic_minorities", "multiculturalism", "nationalism", "urban_rural",
    "civlib_laworder", "regions", "executive_power", "judicial_independence",
    "lrecon", "galtan", "lrgen", "antielite_salience"
]

def se(x: pd.Series) -> float:
    return x.std(ddof=1) / math.sqrt(x.count())

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Повертає 3‑рядковий DataFrame (mean / std / se).
    Якщо у df немає жодної колонки → повертає порожній DF.
    """
    if df.empty or df.shape[1] == 0:
        return pd.DataFrame()          # нічого рахувати

    means = df.mean()
    stds  = df.std(ddof=1)
    ses   = df.apply(se)

    # concat по осі 1 → усі об'єкти стають Series
    out = pd.concat([means, stds, ses], axis=1).T
    out.index = ["mean", "std", "se"]
    return out.round(3)


def main() -> None:
    df = pd.read_excel(INPUT, engine="openpyxl")

    # — ключові колонки
    if "gvt" in df.columns and "govt" not in df.columns:
        df = df.rename(columns={"gvt": "govt"})
    if "govt" not in df.columns:
        raise KeyError("Немає 'govt'/'gvt'.")
    if "family" not in df.columns:
        raise KeyError("Немає 'family'.")
    if "group" not in df.columns:
        raise KeyError("Немає стовпця 'group' (eugroup).")

    # — нормалізуємо govt
    df["govt"] = (df["govt"].fillna(0) > 0).astype(int)

    vars_in_df = [v for v in VARIABLES if v in df.columns]

    blocks = []
    for fam, fam_df in df.groupby("family"):

        # govt1
        blk1 = summarize(fam_df[fam_df["govt"] == 1][vars_in_df])
        blk1.index = pd.MultiIndex.from_product([[fam], ["govt1"], blk1.index])

        # govt0
        blk0 = summarize(fam_df[fam_df["govt"] == 0][vars_in_df])
        blk0.index = pd.MultiIndex.from_product([[fam], ["govt0"], blk0.index])

        # кожна group
        for grp, sub in fam_df.groupby("group"):
            blkg = summarize(sub[vars_in_df])
            blkg.index = pd.MultiIndex.from_product([[fam], [grp], blkg.index])
            blocks.append(blkg)

        # total
        blkt = summarize(fam_df[vars_in_df])
        blkt.index = pd.MultiIndex.from_product([[fam], ["total"], blkt.index])

        blocks.extend([blk1, blk0, blkt])

    result = pd.concat(blocks).sort_index(level=[0, 1])

    result.to_excel(
        OUTPUT,
        sheet_name="family_blocks",
        index_label=["family", "block", "metric"]
    )
    print(f"✔ Збережено у: {OUTPUT.resolve()}")

if __name__ == "__main__":
    main()
