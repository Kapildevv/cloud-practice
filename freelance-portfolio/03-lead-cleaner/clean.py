"""Clean, validate and de-duplicate a messy lead list.

- Names to Title Case, whitespace trimmed
- Indian mobile numbers normalised to +91XXXXXXXXXX; landlines/invalid flagged
- Emails lower-cased and syntax-checked
- City aliases unified (Bombay -> Mumbai, Gurgaon -> Gurugram, ...)
- Duplicates merged on phone, email, or name+city, keeping the most complete row

Usage: python clean.py samples/messy_leads.csv output/clean_leads.xlsx
"""
import re
import sys
from pathlib import Path

import pandas as pd

CITY_ALIASES = {"bombay": "Mumbai", "bangalore": "Bengaluru", "madras": "Chennai",
                "calcutta": "Kolkata", "gurgaon": "Gurugram", "new delhi": "Delhi"}
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def clean_phone(raw: str) -> tuple[str | None, str]:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in "6789":
        return f"+91{digits}", "mobile"
    if len(digits) == 10:
        return f"+91{digits}", "landline"
    return None, "invalid" if digits else "missing"


def clean_email(raw: str) -> tuple[str | None, bool]:
    email = (raw or "").strip().lower()
    return (email or None), bool(EMAIL_RE.match(email))


def clean_city(raw: str) -> str | None:
    city = (raw or "").strip()
    return CITY_ALIASES.get(city.lower(), city.title()) or None


def main(src: str, dest: str) -> None:
    df = pd.read_csv(src, dtype=str, keep_default_na=False)
    df = df[df.apply(lambda r: any(v.strip() for v in r), axis=1)]  # drop blank rows

    out = pd.DataFrame({
        "name": df["Name"].str.strip().str.title().replace("", None),
        "company": df["Company"].str.strip().replace("", None),
        "city": df["City"].map(clean_city),
    })
    out[["phone", "phone_type"]] = df["Phone"].map(clean_phone).tolist()
    out[["email", "email_valid"]] = df["Email"].map(clean_email).tolist()
    out["email_valid"] = out["email_valid"].astype(bool)
    out["email_raw"] = df["Email"].str.strip()
    out.loc[~out["email_valid"], "email"] = None
    out["completeness"] = out[["name", "company", "city", "phone", "email"]].notna().sum(axis=1)

    # Merge duplicates: rows sharing a phone, email or name+city are one group.
    out = out.sort_values("completeness", ascending=False).reset_index(drop=True)
    group, seen = [], {}
    for i, row in out.iterrows():
        keys = [k for k in (row["phone"], row["email"]) if pd.notna(k)]
        if pd.notna(row["name"]) and pd.notna(row["city"]):
            keys.append((row["name"].lower(), row["city"]))
        gid = next((seen[k] for k in keys if k in seen), i)
        for k in keys:
            seen[k] = gid
        group.append(gid)
    out["group"] = group
    # Most complete row first, then fill its gaps from the duplicates.
    clean = out.groupby("group", sort=False).first().reset_index(drop=True)
    removed = len(out) - len(clean)

    issues = out[(out["phone_type"].isin(["invalid", "missing"])) | (~out["email_valid"])]
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(dest) as xl:
        clean.drop(columns=["email_valid", "email_raw", "completeness"]).to_excel(xl, sheet_name="Clean Leads", index=False)
        issues.drop(columns=["group", "email_valid", "completeness"]).to_excel(xl, sheet_name="Needs Review", index=False)
    print(f"{len(df)} rows in -> {len(clean)} unique leads ({removed} duplicates merged, "
          f"{len(issues)} rows with bad phone/email) -> {dest}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
