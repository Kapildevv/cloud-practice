"""Extract key fields from a folder of invoice PDFs into one Excel workbook.

Usage: python extract.py samples/ output/invoices.xlsx
"""
import re
import sys
from pathlib import Path

import pandas as pd
import pdfplumber

PATTERNS = {
    "invoice_no": r"Invoice No[:.]?\s*([A-Z0-9\-/]+)",
    "invoice_date": r"Invoice Date[:.]?\s*(\d{2}/\d{2}/\d{4})",
    "gstin": r"GSTIN[:.]?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]{3})",
    "subtotal": r"Subtotal[:.]?\s*([\d,]+\.\d{2})",
    "gst": r"GST\s*@\s*\d+%[:.]?\s*([\d,]+\.\d{2})",
    "grand_total": r"Grand Total[:.]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.\d{2})",
}
MONEY = {"subtotal", "gst", "grand_total"}


def parse_text(text: str) -> dict:
    row = {}
    for field, pattern in PATTERNS.items():
        m = re.search(pattern, text, re.IGNORECASE)
        value = m.group(1) if m else None
        if value and field in MONEY:
            value = float(value.replace(",", ""))
        row[field] = value
    # First non-empty line is treated as the vendor name.
    row["vendor"] = next((ln.strip() for ln in text.splitlines() if ln.strip()), None)
    return row


def check(row: dict) -> str:
    missing = [k for k, v in row.items() if v is None]
    if missing:
        return "MISSING: " + ", ".join(missing)
    if abs(row["subtotal"] + row["gst"] - row["grand_total"]) > 0.05:
        return "TOTAL MISMATCH"
    return "OK"


def main(src: str, dest: str) -> None:
    rows = []
    for pdf_path in sorted(Path(src).glob("*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        row = {"file": pdf_path.name, **parse_text(text)}
        row["status"] = check({k: v for k, v in row.items() if k != "file"})
        rows.append(row)
    df = pd.DataFrame(rows)
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(dest) as xl:
        df.to_excel(xl, sheet_name="Invoices", index=False)
        df.groupby("vendor", as_index=False)["grand_total"].sum().to_excel(
            xl, sheet_name="By Vendor", index=False)
    flagged = (df["status"] != "OK").sum()
    print(f"{len(df)} invoices -> {dest} ({flagged} flagged for review)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
