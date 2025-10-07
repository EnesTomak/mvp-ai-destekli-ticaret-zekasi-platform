import os
import streamlit as st
import pandas as pd

try:
	from ..services import compute_landed_cost, monte_carlo_eta, service_level_probability
	from ..domain import Shipment, RouteEstimate
except Exception:  # pragma: no cover
	from app.services import compute_landed_cost, monte_carlo_eta, service_level_probability  # type: ignore
	from app.domain import Shipment, RouteEstimate  # type: ignore


ROOT_ROUTES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "routes_data.csv")


def _load_routes() -> pd.DataFrame:
	if os.path.exists(ROOT_ROUTES_PATH):
		try:
			df = pd.read_csv(ROOT_ROUTES_PATH)
			lower = {c: c.strip().lower() for c in df.columns}
			df.rename(columns=lower, inplace=True)
			df = df.rename(columns={
				"baslangic_limani": "start",
				"varis_limani": "end",
				"tasima_sekli": "mode",
				"navlun_ucreti": "freight_usd",
				"tahmini_sure_gun": "duration_days",
				"gecikme_olasiligi": "delay_prob",
			})
			for c in ["freight_usd", "duration_days", "delay_prob"]:
				df[c] = pd.to_numeric(df[c], errors="coerce")
			df = df.dropna(subset=["start", "end", "mode", "freight_usd", "duration_days", "delay_prob"]).copy()
			return df
		except Exception:
			pass
	return pd.DataFrame([
		{"start": "Istanbul", "end": "Hamburg", "mode": "Deniz", "freight_usd": 1600, "duration_days": 16, "delay_prob": 0.22},
		{"start": "Istanbul", "end": "Rotterdam", "mode": "Deniz", "freight_usd": 1800, "duration_days": 18, "delay_prob": 0.25},
		{"start": "Istanbul", "end": "Rotterdam", "mode": "Hava", "freight_usd": 3800, "duration_days": 4, "delay_prob": 0.05},
		{"start": "Istanbul", "end": "Rotterdam", "mode": "Kara", "freight_usd": 1100, "duration_days": 10, "delay_prob": 0.18},
	])


def render():
	st.header("🚛 Modül 3 — Gelişmiş Lojistik Optimizasyonu")
	st.caption("Profesyonel lojistik hesaplamaları ile rota ve maliyet optimizasyonu")

	routes = _load_routes()
	starts = sorted(routes["start"].unique().tolist())
	ends = sorted(routes["end"].unique().tolist())
	modes = sorted(routes["mode"].unique().tolist())

	col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
	with col1:
		start = st.selectbox("Başlangıç Limanı", starts, index=0)
	with col2:
		end = st.selectbox("Varış Limanı", ends, index=0)
	with col3:
		mode_filter = st.multiselect("Taşıma Şekli (opsiyonel filtre)", modes, default=modes)
	with col4:
		price_usd = st.number_input("Birim Satış Fiyatı (USD)", value=150.0, min_value=0.0)

	subset = routes[(routes["start"] == start) & (routes["end"] == end) & (routes["mode"].isin(mode_filter))]
	if subset.empty:
		st.warning("Seçime uygun rota bulunamadı.")
		return

	st.subheader("Gönderi Bilgileri")
	q1, q2 = st.columns(2)
	with q1:
		quantity = st.number_input("Adet", value=200, min_value=1)
	with q2:
		weight = st.number_input("Birim Ağırlık (kg)", value=0.2, min_value=0.0)

	if end.lower().startswith("hamburg"):
		dest_country = "DE"
	elif end.lower().startswith("rotterdam"):
		dest_country = "NL"
	else:
		dest_country = "DE"

	shipment = Shipment(
		product_sku="ELEC-001",
		origin_country="TR",
		destination_country=dest_country,
		transport_mode="",
		unit_price_usd=float(price_usd),
		unit_weight_kg=float(weight),
		quantity=int(quantity),
	)

	rows = []
	for _, r in subset.iterrows():
		route = RouteEstimate(
			mode=str(r["mode"]),
			base_freight_usd=float(r["freight_usd"]),
			duration_days=float(r["duration_days"]),
			delay_probability=float(r["delay_prob"]),
			extra_delay_days=3.0,
			extra_delay_cost_usd=400.0,
		)
		breakdown = compute_landed_cost(shipment, route)
		eta_mean, eta_p95 = monte_carlo_eta(route)
		sl95 = service_level_probability(route, promised_days=eta_p95)
		rows.append({
			"Taşıma Modu": route.mode,
			"Navlun (USD)": round(breakdown.freight_usd, 2),
			"Sigorta (USD)": round(breakdown.insurance_usd, 2),
			"Gümrük Vergisi (USD)": round(breakdown.customs_duty_usd, 2),
			"KDV (USD)": round(breakdown.vat_usd, 2),
			"Elleçleme (USD)": round(breakdown.handling_usd, 2),
			"Toplam İniş Maliyeti (USD)": round(breakdown.total_usd, 2),
			"ETA Ortalama (gün)": round(eta_mean, 1),
			"ETA P95 (gün)": round(eta_p95, 1),
			"Servis Düzeyi": f"{sl95:.1%}",
		})

	df = pd.DataFrame(rows).sort_values("Toplam İniş Maliyeti (USD)", ascending=True)
	
	# Gelişmiş tablo gösterimi
	st.subheader("📊 Rota Karşılaştırma Analizi")
	st.dataframe(df, use_container_width=True)
	
	best = df.iloc[0]
	st.success(f"🏆 Önerilen Rota: {best['Taşıma Modu']} — Toplam Maliyet: ${best['Toplam İniş Maliyeti (USD)']:,.2f}, ETA: {best['ETA Ortalama (gün)']} gün")
	
	# Ek analizler
	col1, col2 = st.columns(2)
	with col1:
		st.subheader("💰 Maliyet Dağılımı")
		cost_data = {
			"Navlun": best["Navlun (USD)"],
			"Sigorta": best["Sigorta (USD)"],
			"Gümrük": best["Gümrük Vergisi (USD)"],
			"KDV": best["KDV (USD)"],
			"Elleçleme": best["Elleçleme (USD)"]
		}
		st.bar_chart(pd.DataFrame(list(cost_data.items()), columns=["Maliyet", "USD"]).set_index("Maliyet"))
	
	with col2:
		st.subheader("⏱️ Süre Analizi")
		time_data = {
			"Ortalama ETA": best["ETA Ortalama (gün)"],
			"P95 ETA": best["ETA P95 (gün)"],
			"Servis Düzeyi": float(best["Servis Düzeyi"].replace("%", ""))
		}
		st.metric("En İyi Servis Düzeyi", f"{time_data['Servis Düzeyi']:.1f}%")
		st.metric("Güvenilir Teslimat", f"{time_data['P95 ETA']:.0f} gün")


