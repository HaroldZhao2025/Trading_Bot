import requests
from typing import Dict, Any, List

from .base import DexQuote
from .registry import chain_cfg, resolve_token


class DexScreenerAdapter:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "otomic-algo/dex"})

    def _best_pair(self, chain: str, token_addr: str) -> Dict[str, Any]:
        cfg = chain_cfg(chain)
        chain_id = cfg["dexscreener_id"]
        url = f"https://api.dexscreener.com/tokens/v1/{chain_id}/{token_addr}"
        r = self.s.get(url, timeout=15)
        r.raise_for_status()
        pairs: List[Dict[str, Any]] = r.json() or []
        if not pairs:
            raise RuntimeError(f"DexScreener no pairs for {token_addr} on {chain}")

        def liq_usd(p: Dict[str, Any]) -> float:
            try:
                return float((p.get("liquidity") or {}).get("usd") or 0.0)
            except Exception:
                return 0.0

        pairs.sort(key=liq_usd, reverse=True)
        return pairs[0]

    def token_price_usd(self, chain: str, token: str) -> float:
        addr = resolve_token(chain, token)
        pair = self._best_pair(chain, addr)
        px = pair.get("priceUsd")
        if px is None:
            raise RuntimeError(f"DexScreener missing priceUsd for {token}")
        return float(px)

    def implied_price(self, chain: str, sell_token: str, buy_token: str, sell_amount: float) -> DexQuote:
        sell_addr = resolve_token(chain, sell_token)
        buy_addr = resolve_token(chain, buy_token)
        sell_usd = self.token_price_usd(chain, sell_token)
        buy_usd = self.token_price_usd(chain, buy_token)
        if buy_usd <= 0:
            raise RuntimeError("Invalid buy token USD price")
        implied = sell_usd / buy_usd
        return DexQuote(
            venue="dexscreener",
            chain=chain,
            sell_token=sell_addr,
            buy_token=buy_addr,
            sell_amount=sell_amount,
            implied_price=implied,
            raw={"sell_usd": sell_usd, "buy_usd": buy_usd},
        )