"""Write a deliberately messy lead list, like the ones clients actually send."""
import csv
from pathlib import Path

ROWS = [
    ["Name", "Phone", "Email", "City", "Company"],
    ["  rahul SHARMA ", "98765 43210", "Rahul.Sharma@Gmail.com ", "mumbai", "Sharma Traders"],
    ["Rahul Sharma", "+91-9876543210", "rahul.sharma@gmail.com", "Bombay", "Sharma Traders Pvt Ltd"],
    ["priya nair", "09812345678", "priya@nairdesigns", "Bengaluru", "Nair Designs"],
    ["Amit Patel", "022 2345 6789", "amit.patel@patelco.in", "Ahmedabad ", "Patel & Co"],
    ["", "", "", "", ""],
    ["Sneha Iyer", "919988776655", "SNEHA.IYER@OUTLOOK.COM", "chennai", "Iyer Consulting"],
    ["Vikram Singh", "12345", "vikram@singh", "Delhi", ""],
    ["vikram singh", "+91 99001 22334", "vikram.singh@gmail.com", "New Delhi", "Singh Motors"],
    ["Anjali Gupta", "8800112233", "anjali.gupta@guptaexports.com", "Gurgaon", "Gupta Exports"],
]

if __name__ == "__main__":
    out = Path(__file__).parent / "samples" / "messy_leads.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(ROWS)
    print(f"Wrote {len(ROWS) - 1} rows to {out}")
