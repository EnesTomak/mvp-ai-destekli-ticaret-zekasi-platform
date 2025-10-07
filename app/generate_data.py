import os
import pandas as pd

try:
	from .utils import DATA_DIR, generate_synthetic_customs_data, generate_synthetic_trade_timeseries
except Exception:  # pragma: no cover
	from utils import DATA_DIR, generate_synthetic_customs_data, generate_synthetic_trade_timeseries


def main() -> None:
	os.makedirs(DATA_DIR, exist_ok=True)

	# Risk/customs dataset (Electronics-focused)
	risk_df = generate_synthetic_customs_data(2000)
	risk_path = os.path.join(DATA_DIR, "customs.csv")
	risk_df.to_csv(risk_path, index=False)

	# Trade time series (Electronics subsegments for TR, DE, NL)
	products = ["Elektronik", "Telefon", "Bilgisayar", "Tablet", "Kamera"]
	countries = ["TR", "DE", "NL"]
	trade_df = generate_synthetic_trade_timeseries(products, countries, months=36)
	trade_path = os.path.join(DATA_DIR, "trade_timeseries.csv")
	trade_df.to_csv(trade_path, index=False)

	print(f"Saved: {risk_path}")
	print(f"Saved: {trade_path}")


if __name__ == "__main__":
	main()


