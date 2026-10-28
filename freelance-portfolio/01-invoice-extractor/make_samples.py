"""Generate sample GST-style invoice PDFs for demoing the extractor."""
import random
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT = Path(__file__).parent / "samples"
VENDORS = [
    ("Sharma Traders", "27AAPFS1234K1Z5"),
    ("Kaveri Office Supplies", "29AACCK5678L1Z2"),
    ("Ganga Electricals", "09AAGFG9012M1Z8"),
]
ITEMS = [("A4 Paper Ream", 260), ("Printer Toner", 1850), ("LED Bulb 9W", 95),
         ("Extension Board", 420), ("Stapler", 140), ("Whiteboard Marker", 35)]


def make_invoice(path: Path, n: int) -> None:
    vendor, gstin = random.choice(VENDORS)
    lines = random.sample(ITEMS, k=random.randint(2, 4))
    c = canvas.Canvas(str(path), pagesize=A4)
    y = 800
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, vendor)
    c.setFont("Helvetica", 10)
    c.drawString(50, y - 18, f"GSTIN: {gstin}")
    c.drawString(380, y, f"Invoice No: INV-2026-{n:04d}")
    c.drawString(380, y - 18, f"Invoice Date: {random.randint(1, 28):02d}/10/2026")
    y -= 70
    c.setFont("Helvetica-Bold", 10)
    for x, h in zip((50, 300, 380, 460), ("Description", "Qty", "Rate", "Amount")):
        c.drawString(x, y, h)
    c.setFont("Helvetica", 10)
    subtotal = 0
    for desc, rate in lines:
        y -= 18
        qty = random.randint(1, 10)
        amt = qty * rate
        subtotal += amt
        for x, v in zip((50, 300, 380, 460), (desc, qty, f"{rate:.2f}", f"{amt:,.2f}")):
            c.drawString(x, y, str(v))
    gst = round(subtotal * 0.18, 2)
    y -= 40
    c.drawString(380, y, f"Subtotal: {subtotal:,.2f}")
    c.drawString(380, y - 18, f"GST @18%: {gst:,.2f}")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(380, y - 38, f"Grand Total: Rs. {subtotal + gst:,.2f}")
    c.save()


if __name__ == "__main__":
    random.seed(7)
    OUT.mkdir(exist_ok=True)
    for i in range(1, 6):
        make_invoice(OUT / f"invoice_{i}.pdf", i)
    print(f"Wrote 5 invoices to {OUT}")
