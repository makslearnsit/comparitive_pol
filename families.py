# family_stats_by_family_and_govt.py
# -*- coding: utf-8 -*-
import math, sys, os, subprocess
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT  = BASE_DIR / "Data_Base_Group7 (all in).xlsx"           # ← або Team2_updated.xlsx
OUTPUT = BASE_DIR / "family_govt_stats_test3.xlsx"

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

def flatten_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Перетворює MultiIndex-колонки на var_metric."""
    df.columns = [
        f"{var}_{stat if stat!='<lambda>' else 'se'}"
        for var, stat in df.columns
    ]
    return df

def main() -> None:
    df = pd.read_excel(INPUT, engine="openpyxl")

    # -- нормалізуємо govt
    if "govt" not in df.columns and "gvt" in df.columns:
        df.rename(columns={"gvt": "govt"}, inplace=True)
    if "govt" not in df.columns:
        raise KeyError("Не знайдено колонки 'govt' або 'gvt'.")
    df["govt"] = (df["govt"].fillna(0) > 0).astype(int)

    if "family" not in df.columns:
        raise KeyError("Не знайдено колонки 'family'.")

    vars_in_df = [v for v in VARIABLES if v in df.columns]

    # -- 1. mean / std / se для family × govt
    base = (
        df.groupby(["family", "govt"])[vars_in_df]
          .agg(["mean", "std", se])
    )
    base = flatten_cols(base)

    # -- 2. додаємо Total усередині кожної сім'ї
    total = (
        df.groupby("family")[vars_in_df]
          .agg(["mean", "std", se])
    )
    total = flatten_cols(total)
    # помічаємо як govt = 'total'
    total.index = pd.MultiIndex.from_product(
        [total.index, ["total"]], names=["family", "govt"]
    )

    result = (
        pd.concat([base, total])
          .sort_index(level=["family", "govt"])
    )

    # -- 3. зберігаємо
    result.to_excel(
        OUTPUT,
        sheet_name="family_govt_summary",
        index_label=["family", "govt"]
    )
    full = OUTPUT.resolve()
    print(f"✔ Збережено у: {full}")

if __name__ == "__main__":
    main()
