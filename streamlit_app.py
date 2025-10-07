"""
Tek giriş: Proje kökünde Streamlit uygulaması
"""
import streamlit as st

from app.modules import risk, market, logistics, summary


st.set_page_config(page_title="AI Ticaret Zekasi MVP", layout="wide")

st.sidebar.title("AI Ticaret Zekasi Platformu")
st.sidebar.caption("MVP - Modulleri deneyin")

MODULLER = {
	"Risk Modellemesi": risk,
	"Pazar Firsat Analizi": market,
	"Rota Optimizasyonu": logistics,
	"Yonetici Ozeti": summary,
}

secim = st.sidebar.radio("Urunlerimizi Kesfedin", list(MODULLER.keys()))
sayfa = MODULLER[secim]
sayfa.render()

st.sidebar.info("Bu platform, KOBI'lerin uluslararasi ticarette karar destek icin tasarlanmıs bir MVP'dir.")


