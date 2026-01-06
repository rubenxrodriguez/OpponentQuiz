#!/usr/bin/env python3
"""
Break down hometown counts into:
1) International vs American
2) For Americans: California vs Non-California

Input CSV must have columns:
- Hometown
- count   (numeric; number of players from that hometown)

Example:
python hometown_breakdown.py /path/to/hometown_counts.csv
"""

import argparse
import re
import sys
import pandas as pd

US_STATE_CODES = set("""
AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC Wash. Mont.
""".split())

def classify_hometown(hometown: str) -> str:
    """Return one of: 'intl', 'us_ca', 'us_nonca', 'unknown'."""
    if pd.isna(hometown):
        return "unknown"

    s = str(hometown).strip()
    if not s:
        return "unknown"

    parts = [p.strip() for p in s.split(",")]

    # Typical US format is "City, ST" where ST is a 2-letter code.
    if len(parts) >= 2:
        last = parts[-1].upper()
        if last in US_STATE_CODES:
            return "us_ca" if last == "CA" else "us_nonca"

    # Fallback: sometimes state might be embedded weirdly; keep it conservative.
    # If it doesn't clearly match a US state code, treat as international.
    return "intl"

def pct(n: float, d: float) -> float:
    return 0.0 if d == 0 else (100.0 * n / d)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path", help="Path to hometown_counts.csv (columns: Hometown,count)")
    args = ap.parse_args()

    df = pd.read_csv(args.csv_path)

    required = {"Hometown", "count"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {sorted(missing)}. Found: {list(df.columns)}")

    # Clean / coerce
    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0).astype(int)
    df["bucket"] = df["Hometown"].apply(classify_hometown)

    total = int(df["count"].sum())
    intl = int(df.loc[df["bucket"] == "intl", "count"].sum())
    us_ca = int(df.loc[df["bucket"] == "us_ca", "count"].sum())
    us_nonca = int(df.loc[df["bucket"] == "us_nonca", "count"].sum())
    us_total = us_ca + us_nonca
    unknown = int(df.loc[df["bucket"] == "unknown", "count"].sum())

    print("\n=== International vs American ===")
    print(f"Total players: {total}")
    print(f"International: {intl} ({pct(intl, total):.1f}%)")
    print(f"American:      {us_total} ({pct(us_total, total):.1f}%)")
    if unknown:
        print(f"Unknown/blank: {unknown} ({pct(unknown, total):.1f}%)")

    print("\n=== Americans: California vs Non-California ===")
    if us_total == 0:
        print("No American hometowns detected.")
    else:
        print(f"California (CA): {us_ca} ({pct(us_ca, us_total):.1f}% of Americans; {pct(us_ca, total):.1f}% of all)")
        print(f"Non-CA:          {us_nonca} ({pct(us_nonca, us_total):.1f}% of Americans; {pct(us_nonca, total):.1f}% of all)")

    # Optional: show top hometowns per bucket (helps sanity-check)
    topn = 10
    print(f"\n=== Top {topn} hometowns by count (overall) ===")
    print(df.sort_values("count", ascending=False)[["Hometown", "count"]].head(topn).to_string(index=False))

    print(f"\n=== Top {topn} international hometowns ===")
    intl_df = df[df["bucket"] == "intl"].sort_values("count", ascending=False)[["Hometown", "count"]].head(topn)
    print(intl_df.to_string(index=False) if len(intl_df) else "(none)")

    print(f"\n=== Top {topn} California hometowns ===")
    ca_df = df[df["bucket"] == "us_ca"].sort_values("count", ascending=False)[["Hometown", "count"]].head(topn)
    print(ca_df.to_string(index=False) if len(ca_df) else "(none)")

if __name__ == "__main__":
    main()
