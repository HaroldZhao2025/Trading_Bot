import os
import time
from typing import Any, Dict, List, Optional

import requests

from .base import OrderIntent, OrderResult


class HyperliquidAdapter:
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.info_url = "https://api.hyperliquid-testnet.xyz/info" if testnet else "https://api.hyperliquid.xyz/info"
        self.s = requests.Session()
        self.s.headers.update({"Content-Type": "application/json", "User-Agent": "otomic-algo/hl"})

    def _post_info(self, body: Dict[str, Any]) -> Any:
        r = self.s.post(self.info_url, json=body, timeout=20)
        r.raise_for_status()
        return r.json()

    def spot_meta(self) -> Dict[str, Any]:
        return self._post_info({"type": "spotMeta"})

    def spot_meta_and_ctxs(self) -> Any:
        return self._post_info({"type": "spotMetaAndAssetCtxs"})

    def spot_balances(self, user: str) -> Any:
        return self._post_info({"type": "spotClearinghouseState", "user": user})

    def perp_all_mids(self) -> Dict[str, Any]:
        return self._post_info({"type": "allMids"})

    def spot_mid(self, pair_name: str) -> float:
        payload = self.spot_meta_and_ctxs()
        meta = payload[0]
        ctxs = payload[1]

        universe: List[Dict[str, Any]] = meta["universe"]
        name_to_idx = {u["name"]: u["index"] for u in universe}
        if pair_name not in name_to_idx:
            raise KeyError(f"Hyperliquid spot pair not found: {pair_name}")

        idx = name_to_idx[pair_name]
        ctx = ctxs[idx]
        px = ctx.get("midPx") or ctx.get("markPx")
        if px is None:
            raise RuntimeError(f"No mid price for {pair_name}")
        return float(px)

    def paper_order(self, intent: OrderIntent) -> OrderResult:
        return OrderResult(
            ok=True,
            venue="hyperliquid-paper",
            symbol=intent.symbol,
            side=intent.side,
            size=intent.size,
            order_type=intent.order_type,
            price=intent.price,
            raw={"ts": time.time(), "paper": True},
        )

    def require_sdk(self):
        try:
            import hyperliquid  # type: ignore
            return hyperliquid
        except Exception as e:
            raise RuntimeError(
                "Hyperliquid live mode requires the official SDK: pip install hyperliquid-python-sdk"
            ) from e