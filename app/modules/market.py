import os
import importlib
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

try:
	from ..utils import (
		DATA_DIR,
		generate_synthetic_trade_timeseries,
		naive_forecast_next_months,
	)
except Exception:  # pragma: no cover
	from app.utils import DATA_DIR, generate_synthetic_trade_timeseries, naive_forecast_next_months  # type: ignore


ROOT_TRADE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "trade_data.csv")
TRADE_PATH = os.path.join(DATA_DIR, "trade_timeseries.csv")


_TURKISH_TO_INTERNAL = {
	"urun": "product",
	"ulke": "country",
	"tarih": "ds",
	"ithalat_hacmi": "y",
}


def _load_or_generate() -> pd.DataFrame:
	if os.path.exists(ROOT_TRADE_PATH):
		try:
			df = pd.read_csv(ROOT_TRADE_PATH)
			lower = {c: c.strip().lower() for c in df.columns}
			df.rename(columns=lower, inplace=True)
			rename_map = {k: v for k, v in _TURKISH_TO_INTERNAL.items() if k in df.columns}
			if rename_map:
				df = df.rename(columns=rename_map)
			required = ["product", "country", "ds", "y"]
			if all(c in df.columns for c in required):
				df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
				df["y"] = pd.to_numeric(df["y"], errors="coerce")
				df = df.dropna(subset=["ds", "y"]).copy()
				return df[required]
		except Exception:
			pass
	if os.path.exists(TRADE_PATH):
		try:
			return pd.read_csv(TRADE_PATH, parse_dates=["ds"])
		except Exception:
			pass
	products = ["Electronics", "Electronics-Component", "Electronics-Accessory"]
	countries = ["TR", "DE", "NL"]
	df = generate_synthetic_trade_timeseries(products, countries, months=36)
	return df


def _cluster_countries(df: pd.DataFrame, product: str) -> pd.DataFrame:
	df_prod = df[df["product"] == product]
	pivot = df_prod.pivot_table(index="country", columns="ds", values="y", aggfunc="mean").fillna(0.0)
	k = min(4, max(2, pivot.shape[0] // 3))
	km = KMeans(n_clusters=k, random_state=42, n_init=10)
	labels = km.fit_predict(pivot)
	return pd.DataFrame({"country": pivot.index, "cluster": labels})


def _forecast_growth(df: pd.DataFrame, product: str) -> pd.DataFrame:
	df_prod = df[df["product"] == product].copy()
	countries = sorted(df_prod["country"].unique().tolist())
	use_prophet = importlib.util.find_spec("prophet") is not None
	if use_prophet:
		from prophet import Prophet  # type: ignore

	rows = []
	for country in countries:
		series = df_prod[df_prod["country"] == country].sort_values("ds")["y"].reset_index(drop=True)
		if use_prophet and len(series) >= 6:
			try:
				m = Prophet(seasonality_mode="additive")
				df_c = df_prod[df_prod["country"] == country][["ds", "y"]]
				m.fit(df_c)
				future = m.make_future_dataframe(periods=6, freq="MS")
				fcast = m.predict(future).tail(6)
				preds = fcast["yhat"].clip(lower=0.0).tolist()
			except Exception:
				preds = naive_forecast_next_months(series, months=6)
		else:
			preds = naive_forecast_next_months(series, months=6)

		last = float(series.iloc[-1]) if len(series) else 0.0
		mean_future = float(np.mean(preds)) if len(preds) else last
		growth = 0.0 if last <= 0 else (mean_future - last) / max(1e-6, last)
		rows.append({"country": country, "growth": growth, "last": last, "future_mean": mean_future})
	return pd.DataFrame(rows).sort_values("growth", ascending=False)


def render():
	st.header("📈 Modül 2 — Dinamik Pazar Analizi ve Talep Tahmini")
	st.caption("Gelişmiş zaman serisi analizi ile pazar fırsatları ve talep tahmini")

	df = _load_or_generate()
	products = sorted(df["product"].unique().tolist())
	product = st.selectbox("Ürün Seçin", products, index=0)

	col1, col2 = st.columns([2, 3])
	with col1:
		st.subheader("Pazar Kümeleri")
		clusters = _cluster_countries(df, product)
		st.dataframe(clusters, use_container_width=True)
	with col2:
		st.subheader("Talep Artışı Tahmini (Son 6 ay)")
		growth = _forecast_growth(df, product)
		top5 = growth.head(5).reset_index(drop=True)
		st.dataframe(top5, use_container_width=True)

	st.bar_chart(top5.set_index("country")["growth"])


