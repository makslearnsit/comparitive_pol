# fill_missing_safe.py
# -*- coding: utf-8 -*-
"""
Заповнюємо пропуски в Team2_updated.xlsx:
  • спершу з CHES-Ukraine.xlsx
  • потім з CHES-2019.xlsx
НЕ змінюємо існуючі непорожні клітинки.
Зберігаємо у Team2_completed.xlsx.
"""

import pandas as pd
from pathlib import Path

# ------------------- файли -----------------------------------------------
BASE_DIR      = Path(__file__).resolve().parent

RECIPIENT     = BASE_DIR / "Team2_updated.xlsx"
DONOR1        = BASE_DIR / "CHES-Ukraine.xlsx"
DONOR2        = BASE_DIR / "CHES-2019.xlsx"
OUTPUT        = BASE_DIR / "Team2_completed.xlsx"

KEYS = ["country", "party_id"]        # ключові колонки для співставлення
# -------------------------------------------------------------------------

def make_index(df: pd.DataFrame) -> pd.DataFrame:
    """Ставимо індекс за KEYS, сортуємо, видаляємо дублікати."""
    return (df
            .set_index(KEYS)
            .sort_index()
            .loc[~df.index.duplicated(keep="first")]
           )

def fill_from_donor(target: pd.DataFrame,
                    donor: pd.DataFrame,
                    cols_common: list[str]) -> int:
    """
    Заповнює NaN у target значеннями з donor (тільки перетин колонок),
    повертає, скільки клітинок стало непорожніми.
    """
    before_na = target.isna()
    # по-колонково, щоб уникнути проблем з dtype
    for col in cols_common:
        target[col] = target[col].fillna(donor[col])
    filled = (before_na & ~target.isna()).sum().sum()
    return int(filled)

def main() -> None:
    # 1. читаємо
    rec_orig = pd.read_excel(RECIPIENT, engine="openpyxl")
    d1       = pd.read_excel(DONOR1,    engine="openpyxl")
    d2       = pd.read_excel(DONOR2,    engine="openpyxl")

    rec = make_index(rec_orig.copy(deep=True))
    d1  = make_index(d1)
    d2  = make_index(d2)

    # спільні колонки
    common1 = [c for c in rec.columns if c in d1.columns]
    common2 = [c for c in rec.columns if c in d2.columns]

    # 2. заповнюємо
    filled1 = fill_from_donor(rec, d1[common1], common1)
    filled2 = fill_from_donor(rec, d2[common2], common2)

    # --- 3. перевірка на небажані перезаписи -----------------------------
    orig_idx = rec_orig.set_index(KEYS)
    common_cols = [c for c in orig_idx.columns if c in rec.columns]
    rec_subset  = rec.loc[orig_idx.index, common_cols]
    rec_subset  = rec_subset[orig_idx[common_cols].columns]

    changes_in_non_na = (
        (orig_idx[common_cols].notna()) &
        (orig_idx[common_cols] != rec_subset)
    ).sum().sum()



    # 4. зберігаємо
    rec.reset_index().to_excel(OUTPUT, index=False)

    # 5. звіт
    print(f"✔ Файл «{OUTPUT.name}» збережено.")
    print(f"Заповнено клітинок:")
    print(f"  • з CHES-Ukraine : {filled1}")
    print(f"  • з CHES-2019    : {filled2}")
    if changes_in_non_na:
        print(
            "\n⚠️  Увага: виявлено",
            changes_in_non_na,
            "клітинок, де існуючі дані були б перезаписані.\n"
            "Скрипт цього НЕ робив, але перевірте структуру колонок / типи, "
            "щоб уникнути конфліктів надалі."
        )
    else:
        print("\nІснуючі заповнені клітинки залишилися без змін.")

if __name__ == "__main__":
    main()
