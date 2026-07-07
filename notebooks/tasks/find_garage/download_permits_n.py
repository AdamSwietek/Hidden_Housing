"""Download the newer "(N)" LADBS building-permit datasets to parquet.

Two Socrata datasets with an identical 38-column schema, refreshed daily:
  - dyxf-7hc4: Building Permits Issued Between 2010 and 2019 (~533k rows)
  - pi9x-tg5x: Building Permits Issued from 2020 to Present (~400k rows)

Unlike hbkd-qubn these carry APN, untruncated work_desc, lat/lon, census
tract, and du_changed/adu_changed/junior_adu flags — but only the Building
permit group (no Electrical/Plumbing/HVAC/Fire Sprinkler trade permits).

Pages through the SODA API ordered by :id, one parquet chunk per page so an
interrupted run can resume, then combines chunks per dataset.

Usage:
    python download_permits_n.py
"""

from pathlib import Path

import pandas as pd
import requests

DATASETS = {
    "dyxf-7hc4": "ladbs_building_permits_2010_2019",
    "pi9x-tg5x": "ladbs_building_permits_2020_present",
}
PAGE_SIZE = 50_000
DATA_DIR = Path("/Users/adamswietek/Documents/PostDoc/HiddenHousing/data/01_raw/permits")

DATE_COLS = ["submitted_date", "issue_date", "cofo_date", "status_date", "refresh_time"]
NUM_COLS = [
    "valuation",
    "square_footage",
    "height",
    "du_changed",
    "adu_changed",
    "junior_adu",
    "lat",
    "lon",
]
DROP_COLS = ["geolocation"]  # nested point; lat/lon columns already carry it


def fetch_page(dataset_id: str, offset: int, session: requests.Session) -> pd.DataFrame:
    params = {
        "$order": ":id",
        "$limit": PAGE_SIZE,
        "$offset": offset,
    }
    r = session.get(f"https://data.lacity.org/resource/{dataset_id}.json", params=params, timeout=120)
    r.raise_for_status()
    return pd.DataFrame(r.json())


def download(dataset_id: str, chunk_dir: Path) -> None:
    chunk_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    offset = 0
    while True:
        chunk_path = chunk_dir / f"chunk_{offset:08d}.parquet"
        if chunk_path.exists():
            offset += PAGE_SIZE
            continue
        df = fetch_page(dataset_id, offset, session)
        if df.empty:
            break
        df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])
        df.astype("string").to_parquet(chunk_path, index=False)
        print(f"{dataset_id} offset {offset}: {len(df)} rows", flush=True)
        if len(df) < PAGE_SIZE:
            break
        offset += PAGE_SIZE


def combine(chunk_dir: Path, out_path: Path) -> None:
    chunks = sorted(chunk_dir.glob("chunk_*.parquet"))
    df = pd.concat([pd.read_parquet(p) for p in chunks], ignore_index=True)
    # Socrata omits fields that are null on every row (e.g. junior_adu in
    # 2010-2019); add them back so both parquets share one schema
    for col in DATE_COLS + NUM_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in NUM_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.to_parquet(out_path, index=False)
    print(f"wrote {len(df):,} rows -> {out_path}")


if __name__ == "__main__":
    for dataset_id, stem in DATASETS.items():
        download(dataset_id, DATA_DIR / f"chunks_{dataset_id}")
        combine(DATA_DIR / f"chunks_{dataset_id}", DATA_DIR / f"{stem}.parquet")
