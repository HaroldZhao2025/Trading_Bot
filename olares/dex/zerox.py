import os
import requests

from .base import DexQuote
from .registry import chain_cfg, resolve_token


class ZeroXAdapter:
    def __init__(self, chain: str):
        cfg = chain_cfg(chain)
        self.chain = chain
        self.chain_id = cfg["chain_id"]
        self.base = cfg["zerox_base"]
        self.api_key = os.environ.get("ZEROX_API_KEY", "")
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "otomic-algo/dex"})

    def quote(self, sell_token: str, buy_token: str, sell_amount_base: int, sell_amount_human: float) -> DexQuote:
        sell_addr = resolve_token(self.chain, sell_token)
        buy_addr = resolve_token(self.chain, buy_token)

        headers = {"0x-version": "v2"}
        if self.api_key:
            headers["0x-api-key"] = self.api_key

        url = f"{self.base}/swap/allowance-holder/quote"
        params = {
            "chainId": str(self.chain_id),
            "sellToken": sell_addr,
            "buyToken": buy_addr,
            "sellAmount": str(sell_amount_base),
        }
        r = self.s.get(url, params=params, headers=headers, timeout=20)
        r.raise_for_status()
        raw = r.json()

        buy_amount = int(raw["buyAmount"])
        implied = buy_amount / sell_amount_base if sell_amount_base > 0 else 0.0

        return DexQuote(
            venue="0x",
            chain=self.chain,
            sell_token=sell_addr,
            buy_token=buy_addr,
            sell_amount=sell_amount_human,
            implied_price=implied,
            raw=raw,
        )