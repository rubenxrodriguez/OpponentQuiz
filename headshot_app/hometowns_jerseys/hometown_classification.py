import pandas as pd

US_STATE_CODES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC","Wash.","Mont."
}

def classify_hometown(hometown: str) -> str:
    """Return one of: 'intl', 'us_ca', 'us_nonca', 'unknown'."""
    if pd.isna(hometown):
        return "unknown"

    s = str(hometown).strip()
    if not s:
        return "unknown"

    parts = [p.strip() for p in s.split(",")]

    # Typical US format: "City, ST"
    if len(parts) >= 2:
        last = parts[-1].upper()
        if last in US_STATE_CODES:
            return "us_ca" if last == "CA" else "us_nonca"

    # If it doesn't clearly match a US state, treat as international
    return "intl"


def main():
    df = pd.read_csv("wcc_roster.csv")

    # 👇 APPLY CLASSIFICATION
    df["hometown_class"] = df["Hometown"].apply(classify_hometown)

    # Optional: sanity check
    print("\nHometown breakdown:")
    print(df["hometown_class"].value_counts())

    # Save updated file
    df.to_csv("wcc_roster_with_hometown_class.csv", index=False)
    print("\nSaved: wcc_roster_with_hometown_class.csv")
    intl = df[df["hometown_class"] == "intl"]
    intl = intl[["Full Name","Team","Hometown"]]
    intl2 = intl[["Hometown"]]
    intl2.to_csv("wcc_intl_hometowns.csv",index =False)
    intl.to_csv("wcc_international_players.csv",index = False)

if __name__ == "__main__":
    main()
