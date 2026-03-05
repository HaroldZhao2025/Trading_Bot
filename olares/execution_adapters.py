import os
import time
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

import requests
import ccxt


@dataclass
class CexPrice:
    exchange: str
    symbol: str
    bid: float
    ask: float
    mid: float
    ts: float


@dataclass
class DexQuote:
    chain: str
    sell_token: str
    buy_token: str
    sell_amount: int
    buy_amount: int
    implied_price: float
    source: str
    ts: float
    raw: Dict[str, Any]


class CexCcxtAdapter:
    def __init__(self, exchange_id: str):
        self.exchange_id = exchange_id
        ex_cls = getattr(ccxt, exchange_id)
        self.ex = ex_cls({"enableRateLimit": True})

    def fetch_mid(self, symbol: str) -> CexPrice:
        t = self.ex.fetch_ticker(symbol)
        bid = float(t.get("bid") or 0.0)
        ask = float(t.get("ask") or 0.0)
        if bid > 0 and ask > 0:
            mid = 0.5 * (bid + ask)
        else:
            last = float(t.get("last") or 0.0)
            mid = last
            bid = bid or last
            ask = ask or last
        return CexPrice(
            exchange=self.exchange_id,
            symbol=symbol,
            bid=bid,
            ask=ask,
            mid=mid,
            ts=time.time(),
        )


class Dex0xAdapter:
    def __init__(self, chain: str = "ethereum", api_base: Optional[str] = None, api_key: Optional[str] = None):
        self.chain = chain
        self.api_base = api_base or "https://api.0x.org"
        self.api_key = api_key or os.environ.get("ZEROX_API_KEY", "")
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "otomic-algo/arb-scan"})

    def quote(self, sell_token: str, buy_token: str, sell_amount: int, chain_id: int = 1) -> DexQuote:
        if not self.api_key:
            raise RuntimeError("Missing ZEROX_API_KEY (0x API v2 requires api key + 0x-version header).")

        url = f"{self.api_base}/swap/allowance-holder/quote"
        headers = {
            "0x-api-key": self.api_key,
            "0x-version": "v2",
        }
        params = {
            "chainId": str(chain_id),
            "sellToken": sell_token,
            "buyToken": buy_token,
            "sellAmount": str(sell_amount),
        }
        r = self.s.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        raw = r.json()
        buy_amount = int(raw["buyAmount"])
        implied = buy_amount / sell_amount if sell_amount > 0 else 0.0
        return DexQuote(self.chain, sell_token, buy_token, sell_amount, buy_amount, implied, "0x-v2", time.time(), raw)

class DexScreenerAdapter:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "otomic-algo/arb-scan"})

    def token_price_usd(self, token_address: str) -> float:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        r = self.s.get(url, timeout=15)
        r.raise_for_status()
        raw = r.json()
        pairs = raw.get("pairs") or []
        best = None
        best_liq = -1.0
        for p in pairs:
            liq = p.get("liquidity") or {}
            usd = liq.get("usd")
            try:
                v = float(usd) if usd is not None else -1.0
            except Exception:
                v = -1.0
            if v > best_liq:
                best_liq = v
                best = p
        if not best:
            raise RuntimeError("DexScreener: no pairs found for token")
        px = best.get("priceUsd")
        if px is None:
            raise RuntimeError("DexScreener: missing priceUsd")
        return float(px)

    def implied_price(self, sell_token_addr: str, buy_token_addr: str) -> float:
        sell_usd = self.token_price_usd(sell_token_addr)
        buy_usd = self.token_price_usd(buy_token_addr)
        if buy_usd <= 0:
            raise RuntimeError("DexScreener: invalid buy token usd price")
        return sell_usd / buy_usd

def token_map(chain: str) -> Dict[str, str]:
    c = chain.lower()
    if c in {"ethereum", "eth"}:
        return {
            "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "ETH":  "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "DAI":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        }
    return {
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "ETH":  "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "DAI":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    }
def to_base_units(amount: float, decimals: int) -> int:
    return int(round(amount * (10 ** decimals)))


def safe_write_jsonl(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")