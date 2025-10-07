from __future__ import annotations

import math
import numpy as np
import pandas as pd
from typing import Dict, Tuple

try:
	from .domain import Shipment, RouteEstimate, LandedCostBreakdown
except Exception:  # when run as top-level module (no package context)
	from domain import Shipment, RouteEstimate, LandedCostBreakdown  # type: ignore


# Gelişmiş gümrük ve vergi oranları
DUTY_RATES = {
	"Elektronik": 0.03,
	"Elektronik-Bileşen": 0.05,
	"Elektronik-Aksesuar": 0.04,
	"Telefon": 0.08,
	"Bilgisayar": 0.10,
	"Tablet": 0.08,
	"Kamera": 0.12,
	"Kulaklık": 0.05,
	"Şarj Cihazı": 0.02,
	"Kablo": 0.01,
}

VAT_RATES = {"DE": 0.19, "NL": 0.21, "TR": 0.20}
INSURANCE_RATE = 0.003  # 0.3% CIF
HANDLING_PER_SHIPMENT_USD = 120.0
DOCUMENTATION_FEE = 50.0  # Gümrük belgeleri
WAREHOUSE_FEE = 25.0  # Depo ücreti


def _get_vat_rate(country_code: str) -> float:
    return VAT_RATES.get(country_code, 0.20)


def calculate_cif_value(shipment: Shipment, freight_usd: float, insurance_rate: float = INSURANCE_RATE) -> float:
    goods_value = shipment.unit_price_usd * shipment.quantity
    insurance = (goods_value + freight_usd) * insurance_rate
    return goods_value + freight_usd + insurance


def compute_landed_cost(shipment: Shipment, route: RouteEstimate) -> LandedCostBreakdown:
    goods_value = shipment.unit_price_usd * shipment.quantity
    insurance_usd = (goods_value + route.base_freight_usd) * INSURANCE_RATE
    cif = goods_value + route.base_freight_usd + insurance_usd
    
    # Ürün bazlı gümrük vergisi
    duty_rate = DUTY_RATES.get(shipment.product_sku, 0.03)
    customs_duty = cif * duty_rate
    
    # KDV hesaplama
    vat_rate = _get_vat_rate(shipment.destination_country)
    vat = (cif + customs_duty) * vat_rate
    
    # Ek maliyetler
    handling = HANDLING_PER_SHIPMENT_USD
    documentation = DOCUMENTATION_FEE
    warehouse = WAREHOUSE_FEE
    
    # Toplam maliyet
    total = route.base_freight_usd + insurance_usd + customs_duty + vat + handling + documentation + warehouse
    
    return LandedCostBreakdown(
        freight_usd=route.base_freight_usd,
        insurance_usd=insurance_usd,
        customs_duty_usd=customs_duty,
        vat_usd=vat,
        handling_usd=handling + documentation + warehouse,
        total_usd=total,
    )


def monte_carlo_eta(route: RouteEstimate, num_sim: int = 3000) -> Tuple[float, float]:
    durations = []
    for _ in range(num_sim):
        delayed = np.random.rand() < route.delay_probability
        dur = route.duration_days + (route.extra_delay_days if delayed else 0.0)
        durations.append(dur)
    arr = np.array(durations)
    return float(np.mean(arr)), float(np.percentile(arr, 95))


def service_level_probability(route: RouteEstimate, promised_days: float) -> float:
    # Assume delay triggers an additive shift in mean; treat as two-point mixture
    on_time = 1.0 - route.delay_probability
    mean_on_time = route.duration_days
    mean_delayed = route.duration_days + route.extra_delay_days
    # Use Chebyshev-like conservative bound with stdev ~ 0.2 * mean
    std_on = 0.2 * mean_on_time
    std_del = 0.2 * mean_delayed
    p_on = 0.5 * (1.0 + math.erf((promised_days - mean_on_time) / (std_on * math.sqrt(2)))) if std_on > 0 else float(promised_days >= mean_on_time)
    p_del = 0.5 * (1.0 + math.erf((promised_days - mean_delayed) / (std_del * math.sqrt(2)))) if std_del > 0 else float(promised_days >= mean_delayed)
    return on_time * p_on + (1.0 - on_time) * p_del


