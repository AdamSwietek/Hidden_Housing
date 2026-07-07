"""Download the full LADBS permits dataset (Socrata id hbkd-qubn) to parquet.

Pages through the SODA API ordered by :id, writing one parquet chunk per page
so an interrupted run can resume. Run `combine()` (or the script end-to-end)
to merge chunks into a single parquet file.

Dataset: LADBS-Permits, ~1.63M rows, issue_date 2013-01-01 .. 2023-05-19.
Note: work_description is truncated at ~70 characters at the source.

Usage:
    python download_permits.py
"""

from pathlib import Path

import pandas as pd
import requests

RESOURCE_URL = "https://data.lacity.org/resource/hbkd-qubn.json"
PAGE_SIZE = 50_000
DATA_DIR = Path("/Users/adamswietek/Documents/PostDoc/HiddenHousing/data/01_raw/permits")
CHUNK_DIR = DATA_DIR / "chunks"
OUT_PATH = DATA_DIR / "ladbs_permits_hbkd-qubn.parquet"

DATE_COLS = ["issue_date", "license_expiration_date"]
NUM_COLS = [
    "address_start",
    "valuation",
    "of_residential_dwelling_units",
    "of_stories",
]


def fetch_page(offset: int, session: requests.Session) -> pd.DataFrame:
    params = {
        "$order": ":id",
        "$limit": PAGE_SIZE,
        "$offset": offset,
    }
    r = session.get(RESOURCE_URL, params=params, timeout=120)
    r.raise_for_status()
    return pd.DataFrame(r.json())


def download() -> None:
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    offset = 0
    while True:
        chunk_path = CHUNK_DIR / f"chunk_{offset:08d}.parquet"
        if chunk_path.exists():
            offset += PAGE_SIZE
            continue
        df = fetch_page(offset, session)
        if df.empty:
            break
        df.astype("string").to_parquet(chunk_path, index=False)
        print(f"offset {offset}: {len(df)} rows", flush=True)
        if len(df) < PAGE_SIZE:
            break
        offset += PAGE_SIZE


def combine() -> pd.DataFrame:
    chunks = sorted(CHUNK_DIR.glob("chunk_*.parquet"))
    df = pd.concat([pd.read_parquet(p) for p in chunks], ignore_index=True)
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in NUM_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.to_parquet(OUT_PATH, index=False)
    print(f"wrote {len(df):,} rows -> {OUT_PATH}")
    return df


if __name__ == "__main__":
    download()
    combine()
