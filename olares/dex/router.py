from typing import Optional

from .base import DexQuote
from .dexscreener import DexScreenerAdapter
from .zerox import ZeroXAdapter


def to_base_units(amount: float, decimals: int) -> int:
    return int(round(amount * (10 ** decimals)))


class DexRouter:
    def __init__(self, chain: str):
        self.chain = chain
        self.ds = DexScreenerAdapter()
        self.zx = ZeroXAdapter(chain)

    def best_quote(
        self,
        sell_token: str,
        buy_token: str,
        sell_amount_human: float,
        sell_decimals: int = 18,
    ) -> DexQuote:
        try:
            sell_base = to_base_units(sell_amount_human, sell_decimals)
            return self.zx.quote(sell_token, buy_token, sell_base, sell_amount_human)
        except Exception:
            return self.ds.implied_price(self.chain, sell_token, buy_token, sell_amount_human)