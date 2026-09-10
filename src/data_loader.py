import os
import time
import requests
import pandas as pd


CACHE_PATH = "data/raw/sber_stock_cache.csv"

URL = (
    "https://iss.moex.com/iss/history/engines/stock/"
    "markets/shares/boards/TQBR/securities/SBER.json"
)


def load_sber_stock_data(
    start="2020-01-01",
    end="2026-01-01",
    limit=500
):

    os.makedirs("data/raw", exist_ok=True)

    # если уже есть кэш — используем его
    if os.path.exists(CACHE_PATH):
        print("Loading from cache...")
        return pd.read_csv(CACHE_PATH)


    print("Requesting MOEX API...")


    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(X11; Linux x86_64) "
            "Python requests"
        ),
        "Accept": "application/json"
    }


    params = {
        "from": start,
        "till": end,
        "limit": limit,
        "iss.meta": "off"
    }


    session = requests.Session()

    retries = 5


    for attempt in range(retries):

        try:

            response = session.get(
                URL,
                params=params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            break


        except Exception as e:

            print(
                f"Attempt {attempt + 1}/{retries} failed:",
                e
            )

            if attempt == retries - 1:
                raise

            time.sleep(5)


    history = data["history"]


    columns = history["columns"]
    rows = history["data"]


    df = pd.DataFrame(
        rows,
        columns=columns
    )


    # оставляем нужные признаки

    df = df[
        [
            "TRADEDATE",
            "OPEN",
            "CLOSE",
            "HIGH",
            "LOW",
            "VALUE",
            "VOLUME"
        ]
    ]


    df.columns = [
        "date",
        "open",
        "close",
        "high",
        "low",
        "value",
        "volume"
    ]


    df["date"] = pd.to_datetime(df["date"])


    df = df.sort_values("date")


    df.to_csv(
        CACHE_PATH,
        index=False
    )


    print(
        f"Saved cache: {CACHE_PATH}"
    )


    return df



if __name__ == "__main__":

    df = load_sber_stock_data()

    print(df.head())

    print(df.shape)