from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Product:
    sku: str
    name: str
    category: str  # e.g., Electronics
    subcategory: str  # e.g., Component, Accessory


@dataclass
class Market:
    code: str  # e.g., DE, NL
    name: str


@dataclass
class Shipment:
    product_sku: str
    origin_country: str
    destination_country: str
    transport_mode: str  # Sea, Air, Road
    unit_price_usd: float
    unit_weight_kg: float
    quantity: int


@dataclass
class RouteEstimate:
    mode: str
    base_freight_usd: float
    duration_days: float
    delay_probability: float
    extra_delay_days: float
    extra_delay_cost_usd: float


@dataclass
class LandedCostBreakdown:
    freight_usd: float
    insurance_usd: float
    customs_duty_usd: float
    vat_usd: float
    handling_usd: float
    total_usd: float


@dataclass
class ForecastResult:
    country: str
    growth_ratio: float
    last_value: float
    future_mean: float


