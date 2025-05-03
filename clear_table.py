# clean_parties.py  (оновлена версія)

import pandas as pd
from pathlib import Path

# --- 1. Базова директорія — папка, де лежить сам цей скрипт ---------------
BASE_DIR = Path(__file__).resolve().parent

# --- 2. Файли-джерела ------------------------------------------------------
TEAM2_FILE = BASE_DIR / "База даних команди 2.xlsx"
CHES_FILE  = BASE_DIR / "CHES-Ukraine.xlsx"

# --- 3. Куди зберегти результат -------------------------------------------
OUTPUT = BASE_DIR / "Team2_updated.xlsx"
# (можете додати дату/час, якщо потрібно кілька версій, напр.:
# OUTPUT = BASE_DIR / f"Team2_updated_{pd.Timestamp.today().date()}.xlsx")

# --- 4. Далі код без змін --------------------------------------------------
EU_COUNTRIES = [
    "Austria", "Ireland", "Belgium", "Italy", "Bulgaria", "Latvia",
    "Croatia", "Lithuania", "Cyprus", "Malta", "Czech Republic",
    "Netherlands", "Denmark", "Poland", "Estonia", "Portugal",
    "Finland", "Romania", "France", "Slovakia", "Germany",
    "Slovenia", "Greece", "Spain", "Hungary", "Sweden"
]

def main() -> None:
    df_team2 = pd.read_excel(TEAM2_FILE, sheet_name=0, engine="openpyxl")
    df_ches  = pd.read_excel(CHES_FILE, sheet_name=0, engine="openpyxl")

    df_team2_eu = df_team2[df_team2["country"].isin(EU_COUNTRIES)].copy()
    df_ches_eu  = df_ches[df_ches["country"].isin(EU_COUNTRIES)].copy()

    df_team2_clean = df_team2_eu[df_team2_eu["party_id"].isin(df_ches_eu["party_id"])]
    missing_from_team2 = df_ches_eu[~df_ches_eu["party_id"].isin(df_team2_eu["party_id"])]

    merged_df = pd.concat([df_team2_clean, missing_from_team2], ignore_index=True)
    merged_df.sort_values(["country", "party"], inplace=True)

    merged_df.to_excel(OUTPUT, index=False)
    print(f"✔ Готово! Збережено {len(merged_df)} рядків у «{OUTPUT.name}».")

if __name__ == "__main__":
    main()
