from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DexQuote:
    venue: str
    chain: str
    sell_token: str
    buy_token: str
    sell_amount: float
    implied_price: float
    raw: Dict[str, Any]


@dataclass
class OrderIntent:
    venue: str
    symbol: str
    side: str
    size: float
    order_type: str = "market"
    price: Optional[float] = None


@dataclass
class OrderResult:
    ok: bool
    venue: str
    symbol: str
    side: str
    size: float
    order_type: str
    price: Optional[float]
    raw: Dict[str, Any]


@dataclass
class CexMid:
    exchange: str
    symbol: str
    bid: float
    ask: float
    mid: float
    raw: Dict[str, Any]