import os
import random
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd
from joblib import dump, load

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "_models")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def set_reproducible_seed(seed: int = 42) -> None:
	random.seed(seed)
	np.random.seed(seed)


def safe_read_csv(path: str) -> Optional[pd.DataFrame]:
	try:
		if os.path.exists(path):
			return pd.read_csv(path)
		return None
	except Exception:
		return None


def save_model(model, path: str) -> None:
	try:
		dump(model, path)
	except Exception:
		pass


def load_model(path: str):
	try:
		if os.path.exists(path):
			return load(path)
		return None
	except Exception:
		return None


@dataclass
class RouteOption:
	name: str
	cost_usd: float
	duration_days: float
	delay_probability: float
	risk_level: str


def generate_synthetic_customs_data(num_rows: int = 1000) -> pd.DataFrame:
	set_reproducible_seed()
	product_categories = [
		"Elektronik",
		"Elektronik-Bileşen",
		"Elektronik-Aksesuar",
		"Telefon",
		"Bilgisayar",
		"Tablet",
		"Kamera",
		"Kulaklık",
		"Şarj Cihazı",
		"Kablo",
	]
	countries = ["TR", "DE", "NL"]
	transport_modes = ["Deniz", "Hava", "Kara", "Demir"]
	
	# Türkçe ürün detayları
	product_details = {
		"Elektronik": {"risk_factor": 0.12, "duty_rate": 0.03, "weight_avg": 0.5},
		"Elektronik-Bileşen": {"risk_factor": 0.18, "duty_rate": 0.05, "weight_avg": 0.1},
		"Elektronik-Aksesuar": {"risk_factor": 0.15, "duty_rate": 0.04, "weight_avg": 0.2},
		"Telefon": {"risk_factor": 0.20, "duty_rate": 0.08, "weight_avg": 0.3},
		"Bilgisayar": {"risk_factor": 0.25, "duty_rate": 0.10, "weight_avg": 2.0},
		"Tablet": {"risk_factor": 0.22, "duty_rate": 0.08, "weight_avg": 0.6},
		"Kamera": {"risk_factor": 0.28, "duty_rate": 0.12, "weight_avg": 0.8},
		"Kulaklık": {"risk_factor": 0.15, "duty_rate": 0.05, "weight_avg": 0.2},
		"Şarj Cihazı": {"risk_factor": 0.10, "duty_rate": 0.02, "weight_avg": 0.1},
		"Kablo": {"risk_factor": 0.08, "duty_rate": 0.01, "weight_avg": 0.05},
	}
	
	# Gelişmiş risk hesaplama
	risk_factors = {
		"TR": {"DE": 0.05, "NL": 0.03},
		"DE": {"TR": 0.08, "NL": 0.02},
		"NL": {"TR": 0.06, "DE": 0.02},
	}

	rows = []
	for _ in range(num_rows):
		prod = random.choice(product_categories)
		exp = random.choice(countries)
		imp = random.choice([c for c in countries if c != exp])
		mode = random.choice(transport_modes)
		
		# Gelişmiş risk hesaplama
		base_risk = product_details[prod]["risk_factor"]
		route_risk = risk_factors.get(exp, {}).get(imp, 0.05)
		
		# Taşıma modu risk faktörleri
		mode_risk = {"Deniz": 0.15, "Hava": 0.05, "Kara": 0.20, "Demir": 0.10}[mode]
		
		# Mevsimsel risk (Q4 daha yüksek)
		month = np.random.randint(1, 13)
		seasonal_risk = 0.05 if month in [10, 11, 12] else 0.0
		
		total_risk = base_risk + route_risk + mode_risk + seasonal_risk
		penalty = int(np.random.rand() < min(0.95, total_risk + np.random.rand() * 0.03))
		
		# Ek bilgiler
		weight = np.random.normal(product_details[prod]["weight_avg"], 0.1)
		value = np.random.lognormal(3, 1) * 100  # USD
		
		rows.append({
			"product": prod,
			"exporter": exp,
			"importer": imp,
			"mode": mode,
			"penalty": penalty,
			"weight_kg": round(weight, 2),
			"value_usd": round(value, 2),
			"risk_score": round(total_risk, 3),
		})
	return pd.DataFrame(rows)


def generate_synthetic_trade_timeseries(products: List[str], countries: List[str], months: int = 36) -> pd.DataFrame:
	set_reproducible_seed()
	dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=months, freq="MS")
	records = []
	for product in products:
		for country in countries:
			# Daha gerçekçi trend ve mevsimsellik
			base_level = {"TR": 100, "DE": 300, "NL": 200}[country]
			product_multiplier = {"Elektronik": 1.0, "Telefon": 1.5, "Bilgisayar": 0.8}.get(product, 1.0)
			level = base_level * product_multiplier
			
			trend = np.random.uniform(-1, 3)  # Daha konservatif trend
			season_amp = np.random.uniform(10, 50)  # Daha belirgin mevsimsellik
			noise_sd = np.random.uniform(5, 25)
			
			# COVID etkisi simülasyonu (2020-2021)
			covid_impact = 0.0
			for i, date in enumerate(dates):
				if date.year == 2020:
					covid_impact = -0.3 + 0.1 * (i % 12)  # Yıl sonunda toparlanma
				elif date.year == 2021:
					covid_impact = 0.1 + 0.05 * (i % 12)  # Toparlanma
				else:
					covid_impact = 0.0
				
				seasonal = season_amp * np.sin(2 * np.pi * (i % 12) / 12)
				value = max(0.0, level + trend * i + seasonal + np.random.normal(0, noise_sd) + covid_impact * level)
				records.append({
					"ds": date,
					"y": value,
					"country": country,
					"product": product,
				})
	return pd.DataFrame(records)


def naive_forecast_next_months(series: pd.Series, months: int = 6) -> List[float]:
	if len(series) < 2:
		return [float(series.iloc[-1] if len(series) else 0.0)] * months
	diffs = series.diff().dropna()
	mean_change = float(diffs.mean()) if len(diffs) else 0.0
	last_val = float(series.iloc[-1])
	return [max(0.0, last_val + mean_change * (i + 1)) for i in range(months)]


def compute_expected_cost(cost_usd: float, delay_prob: float, extra_cost_usd: float) -> float:
	return cost_usd + delay_prob * extra_cost_usd


def compute_expected_duration(days: float, delay_prob: float, extra_days: float) -> float:
	return days + delay_prob * extra_days


def score_route_for_profitability_margin(price_usd: float, expected_cost_usd: float, expected_days: float) -> float:
	if expected_days <= 0:
		return float("-inf")
	return (price_usd - expected_cost_usd) / expected_days
