"""Step 1 (plan G.1): reproduce the dashboard revenue figure and test alternative definitions.

SYNTHETIC DATA. Run: python3 -m analysis.step1_revenue_definitions
Reads data/payments.csv and data/fx_rates.csv directly (not the warehouse), so it is an independent check.
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
Q = {"Q2": ("2026-04-01", "2026-06-30"), "Q3": ("2026-07-01", "2026-09-30")}


def main() -> None:
    p = pd.read_csv(DATA / "payments.csv", dtype={"failure_code": str, "refund_of": str})
    fx = pd.read_csv(DATA / "fx_rates.csv")
    p["month"] = p["created_at"].str[:7]
    p = p.merge(fx, on=["month", "currency"], how="left", validate="many_to_one")
    assert p["usd_per_unit"].notna().all(), "payments without an FX rate"
    p["usd"] = p["amount"] * p["usd_per_unit"]
    p["day"] = p["created_at"].str[:10]
    dup_rows = int(p.duplicated().sum())
    dup_ids = int(p["payment_id"].duplicated().sum())
    dedup = p.drop_duplicates()

    def quarter_sum(df):
        return {q: df[(df["day"] >= a) & (df["day"] <= b)]["usd"].sum() for q, (a, b) in Q.items()}

    def charges(df):
        return df[(df["type"] == "charge") & (df["status"] == "succeeded")]

    defs = {
        "A. dashboard: successful charges, duplicates kept": quarter_sum(charges(p)),
        "B. successful charges, duplicates removed": quarter_sum(charges(dedup)),
    }
    refunds = quarter_sum(dedup[dedup["type"] == "refund"])
    b = defs["B. successful charges, duplicates removed"]
    defs["C. net cash: B minus refunds"] = {q: b[q] - refunds[q] for q in Q}

    print("SYNTHETIC DATA - step 1: revenue definitions")
    print(f"duplicate payment rows (exact): {dup_rows}  | duplicate payment_id: {dup_ids}")
    for name, v in defs.items():
        print(f"{name:52s} Q2 {v['Q2']:>12,.0f}  Q3 {v['Q3']:>12,.0f}  change {100 * (v['Q3'] / v['Q2'] - 1):+.2f}%")


if __name__ == "__main__":
    main()
