import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

try:
	from ..utils import DATA_DIR, generate_synthetic_customs_data, generate_synthetic_trade_timeseries
	from ..services import DUTY_RATES, VAT_RATES
except Exception:
	from app.utils import DATA_DIR, generate_synthetic_customs_data, generate_synthetic_trade_timeseries
	from app.services import DUTY_RATES, VAT_RATES


def _generate_comprehensive_report(product: str, market: str, risk_data: pd.DataFrame, trade_data: pd.DataFrame) -> dict:
	"""Kapsamlı rapor verilerini oluşturur"""
	
	# Risk analizi
	product_risk = risk_data[risk_data['product'] == product]
	market_risk = product_risk[product_risk['importer'] == market]
	risk_score = market_risk['risk_score'].mean() if not market_risk.empty else 0.3
	
	# Pazar analizi
	market_trade = trade_data[(trade_data['product'] == product) & (trade_data['country'] == market)]
	growth_trend = 0.0
	if len(market_trade) > 1:
		recent_avg = market_trade.tail(6)['y'].mean()
		older_avg = market_trade.head(6)['y'].mean()
		growth_trend = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
	
	# Maliyet analizi
	duty_rate = DUTY_RATES.get(product, 0.03)
	vat_rate = VAT_RATES.get(market, 0.20)
	
	# Öneriler
	recommendations = []
	if risk_score < 0.2:
		recommendations.append("✅ Düşük risk - İşlem güvenle devam edebilir")
	elif risk_score < 0.4:
		recommendations.append("⚠️ Orta risk - Ek belgeler ve önlemler alın")
	else:
		recommendations.append("🚨 Yüksek risk - Alternatif rotalar değerlendirin")
	
	if growth_trend > 10:
		recommendations.append("📈 Yüksek talep artışı - Pazar fırsatı değerlendirin")
	elif growth_trend < -5:
		recommendations.append("📉 Talep düşüşü - Pazar koşullarını gözden geçirin")
	
	return {
		"risk_score": risk_score,
		"growth_trend": growth_trend,
		"duty_rate": duty_rate,
		"vat_rate": vat_rate,
		"recommendations": recommendations,
		"data_points": len(market_risk),
		"market_volume": market_trade['y'].sum() if not market_trade.empty else 0
	}


def render():
	st.header("📋 Modül 4 — Akıllı Yönetici Raporu")
	st.caption("Entegre analiz ile kapsamlı iş zekası raporu ve stratejik öneriler")

	# Veri yükleme
	@st.cache_data
	def load_integrated_data():
		risk_data = generate_synthetic_customs_data(1000)
		products = ["Elektronik", "Telefon", "Bilgisayar", "Tablet", "Kamera"]
		countries = ["TR", "DE", "NL"]
		trade_data = generate_synthetic_trade_timeseries(products, countries, 36)
		return risk_data, trade_data
	
	risk_data, trade_data = load_integrated_data()
	
	# Ana seçimler
	st.subheader("🎯 Analiz Parametreleri")
	col1, col2, col3 = st.columns(3)
	with col1:
		product = st.selectbox("Ürün Kategorisi", 
			options=sorted(risk_data['product'].unique()),
			help="Analiz edilecek ürün kategorisi"
		)
	with col2:
		market = st.selectbox("Hedef Pazar", 
			options=["DE", "NL"], 
			help="Hedef pazar ülkesi"
		)
	with col3:
		analysis_type = st.selectbox("Analiz Türü", 
			options=["Kapsamlı Rapor", "Risk Analizi", "Pazar Analizi", "Maliyet Analizi"],
			help="Rapor türü seçin"
		)

	if st.button("🔍 Rapor Oluştur", type="primary"):
		# Entegre analiz
		report_data = _generate_comprehensive_report(product, market, risk_data, trade_data)
		
		# Rapor başlığı
		st.subheader(f"📊 {product} - {market} Pazarı Analiz Raporu")
		st.caption(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
		
		# Ana metrikler
		col1, col2, col3, col4 = st.columns(4)
		with col1:
			st.metric("Risk Skoru", f"{report_data['risk_score']:.2f}", 
				delta=f"{'Düşük' if report_data['risk_score'] < 0.3 else 'Orta' if report_data['risk_score'] < 0.6 else 'Yüksek'}")
		with col2:
			st.metric("Talep Trendi", f"{report_data['growth_trend']:+.1f}%", 
				delta="Artış" if report_data['growth_trend'] > 0 else "Azalış")
		with col3:
			st.metric("Gümrük Vergisi", f"{report_data['duty_rate']:.1%}")
		with col4:
			st.metric("KDV Oranı", f"{report_data['vat_rate']:.1%}")
		
		# Detaylı analiz
		if analysis_type == "Kapsamlı Rapor":
			st.subheader("📈 Pazar Durumu")
			market_trade = trade_data[(trade_data['product'] == product) & (trade_data['country'] == market)]
			if not market_trade.empty:
				st.line_chart(market_trade.set_index('ds')['y'])
			
			st.subheader("🎯 Stratejik Öneriler")
			for i, rec in enumerate(report_data['recommendations'], 1):
				st.write(f"{i}. {rec}")
			
			# Maliyet projeksiyonu
			st.subheader("💰 Maliyet Projeksiyonu")
			base_cost = 1000  # Örnek temel maliyet
			total_duty = base_cost * report_data['duty_rate']
			total_vat = (base_cost + total_duty) * report_data['vat_rate']
			total_cost = base_cost + total_duty + total_vat
			
			cost_breakdown = pd.DataFrame({
				"Maliyet Kalemi": ["Temel Maliyet", "Gümrük Vergisi", "KDV", "Toplam"],
				"Tutar (USD)": [base_cost, total_duty, total_vat, total_cost]
			})
			st.dataframe(cost_breakdown, use_container_width=True)
			
		elif analysis_type == "Risk Analizi":
			st.subheader("🚨 Risk Değerlendirmesi")
			risk_products = risk_data[risk_data['product'] == product]
			risk_by_country = risk_products.groupby('importer')['penalty'].mean()
			st.bar_chart(risk_by_country)
			
		elif analysis_type == "Pazar Analizi":
			st.subheader("📊 Pazar Performansı")
			market_performance = trade_data[trade_data['country'] == market].groupby('product')['y'].mean()
			st.bar_chart(market_performance)
			
		elif analysis_type == "Maliyet Analizi":
			st.subheader("💵 Maliyet Karşılaştırması")
			cost_comparison = pd.DataFrame({
				"Ülke": ["DE", "NL"],
				"Gümrük Vergisi": [DUTY_RATES.get(product, 0.03), DUTY_RATES.get(product, 0.03)],
				"KDV": [VAT_RATES["DE"], VAT_RATES["NL"]],
				"Toplam Vergi": [DUTY_RATES.get(product, 0.03) + VAT_RATES["DE"], 
								DUTY_RATES.get(product, 0.03) + VAT_RATES["NL"]]
			})
			st.dataframe(cost_comparison, use_container_width=True)
		
		# İndirme seçenekleri
		st.subheader("📥 Rapor İndirme")
		col1, col2 = st.columns(2)
		with col1:
			if st.button("📄 PDF Olarak İndir"):
				st.info("PDF rapor oluşturma özelliği geliştirilecek")
		with col2:
			if st.button("📊 Excel Olarak İndir"):
				st.info("Excel rapor oluşturma özelliği geliştirilecek")


