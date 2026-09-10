from pathlib import Path
from datetime import date

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = (
    "https://iss.moex.com/iss/engines/stock/"
    "markets/shares/securities/SBER/candles.json"
)

DATA_DIR = Path("data/raw")
CACHE_PATH = DATA_DIR / "sber_stock_cache.csv"

START_DATE = "2020-01-01"
END_DATE = date.today().isoformat()
PAGE_SIZE = 500


def create_session() -> requests.Session:
    session = requests.Session()

    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def load_sber_stock_data() -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    session = create_session()

    all_rows = []
    start = 0

    print(
        f"Requesting MOEX API: "
        f"{START_DATE} → {END_DATE}"
    )

    while True:
        params = {
            "from": START_DATE,
            "till": END_DATE,
            "interval": 24,
            "start": start,
        }

        print(f"Loading rows from {start}...")

        response = session.get(
            BASE_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()
        candles = payload.get("candles", {})

        columns = candles.get("columns", [])
        data = candles.get("data", [])

        if not data:
            break

        batch = pd.DataFrame(data, columns=columns)
        all_rows.append(batch)

        print(f"Received: {len(batch)} rows")

        if len(batch) < PAGE_SIZE:
            break

        start += PAGE_SIZE

    if not all_rows:
        raise RuntimeError("MOEX API returned no data.")

    df = pd.concat(all_rows, ignore_index=True)

    # Keep only the columns needed for the project.
    required_columns = [
        "begin",
        "open",
        "close",
        "high",
        "low",
        "value",
        "volume",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise RuntimeError(
            f"Missing columns from MOEX response: {missing}"
        )

    df = df[required_columns].copy()

    df = df.rename(
        columns={
            "begin": "date",
        }
    )

    df["date"] = pd.to_datetime(df["date"])

    numeric_columns = [
        "open",
        "close",
        "high",
        "low",
        "value",
        "volume",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = (
        df
        .dropna(subset=["date", "close"])
        .drop_duplicates(subset=["date"])
        .sort_values("date")
        .reset_index(drop=True)
    )

    df.to_csv(
        CACHE_PATH,
        index=False,
    )

    print(f"Saved cache: {CACHE_PATH}")
    print(f"Dataset shape: {df.shape}")
    print(
        f"Date range: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()}"
    )

    return df


if __name__ == "__main__":
    df = load_sber_stock_data()

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nLast 5 rows:")
    print(df.tail())

    print("\nShape:")
    print(df.shape)
