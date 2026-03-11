import argparse
import json
import os
import time

import ccxt

from .dex.base import CexMid, OrderIntent
from .dex.router import DexRouter
from .dex.hyperliquid import HyperliquidAdapter


def fetch_cex_mid(exchange_id: str, symbol: str) -> CexMid:
    ex_cls = getattr(ccxt, exchange_id)
    ex = ex_cls({"enableRateLimit": True})
    t = ex.fetch_ticker(symbol)
    bid = float(t.get("bid") or 0.0)
    ask = float(t.get("ask") or 0.0)
    if bid > 0 and ask > 0:
        mid = 0.5 * (bid + ask)
    else:
        last = float(t.get("last") or 0.0)
        bid = bid or last
        ask = ask or last
        mid = last
    return CexMid(exchange=exchange_id, symbol=symbol, bid=bid, ask=ask, mid=mid, raw=t)


def cmd_dex_scan(args):
    router = DexRouter(args.chain)

    while True:
        try:
            cex = fetch_cex_mid(args.cex_exchange, args.cex_symbol)
            dq = router.best_quote(
                sell_token=args.sell_token,
                buy_token=args.buy_token,
                sell_amount_human=args.sell_amount,
                sell_decimals=args.sell_decimals,
            )
            edge_bps = 0.0
            if cex.mid > 0:
                edge_bps = (dq.implied_price - cex.mid) / cex.mid * 10000.0

            out = {
                "ts": time.time(),
                "cex": {"exchange": cex.exchange, "symbol": cex.symbol, "mid": cex.mid, "bid": cex.bid, "ask": cex.ask},
                "dex": {
                    "venue": dq.venue,
                    "chain": dq.chain,
                    "sell_token": dq.sell_token,
                    "buy_token": dq.buy_token,
                    "sell_amount": dq.sell_amount,
                    "implied": dq.implied_price,
                },
                "edge_bps": edge_bps,
                "trigger": abs(edge_bps) >= args.threshold_bps,
            }
            print(json.dumps(out, ensure_ascii=False), flush=True)
            time.sleep(args.poll_sec)
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(json.dumps({"ts": time.time(), "error": str(e)}), flush=True)
            time.sleep(max(args.poll_sec, 2.0))


def cmd_hl_paper(args):
    hl = HyperliquidAdapter(testnet=args.testnet)

    while True:
        try:
            px = hl.spot_mid(args.spot_pair)
            side = "buy" if px < args.anchor_price else "sell"
            intent = OrderIntent(venue="hyperliquid-paper", symbol=args.spot_pair, side=side, size=args.size, order_type="market")
            result = hl.paper_order(intent)
            out = {
                "ts": time.time(),
                "venue": "hyperliquid-paper",
                "pair": args.spot_pair,
                "mid": px,
                "anchor_price": args.anchor_price,
                "side": side,
                "size": args.size,
                "result": result.raw,
            }
            print(json.dumps(out, ensure_ascii=False), flush=True)
            time.sleep(args.poll_sec)
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(json.dumps({"ts": time.time(), "error": str(e)}), flush=True)
            time.sleep(max(args.poll_sec, 2.0))


def build_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("dex-scan")
    p1.add_argument("--chain", default=os.environ.get("DEX_CHAIN", "ethereum"))
    p1.add_argument("--sell-token", default=os.environ.get("DEX_SELL_TOKEN", "ETH"))
    p1.add_argument("--buy-token", default=os.environ.get("DEX_BUY_TOKEN", "USDC"))
    p1.add_argument("--sell-amount", type=float, default=float(os.environ.get("DEX_SELL_AMOUNT", "0.05")))
    p1.add_argument("--sell-decimals", type=int, default=int(os.environ.get("DEX_SELL_DECIMALS", "18")))
    p1.add_argument("--cex-exchange", default=os.environ.get("DEX_CEX_EXCHANGE", "kraken"))
    p1.add_argument("--cex-symbol", default=os.environ.get("DEX_CEX_SYMBOL", "ETH/USD"))
    p1.add_argument("--threshold-bps", type=float, default=float(os.environ.get("DEX_THRESHOLD_BPS", "30")))
    p1.add_argument("--poll-sec", type=float, default=float(os.environ.get("DEX_POLL_SEC", "5")))
    p1.set_defaults(func=cmd_dex_scan)

    p2 = sub.add_parser("hl-paper")
    p2.add_argument("--spot-pair", default=os.environ.get("HL_SPOT_PAIR", "PURR/USDC"))
    p2.add_argument("--anchor-price", type=float, default=float(os.environ.get("HL_ANCHOR_PRICE", "0.2")))
    p2.add_argument("--size", type=float, default=float(os.environ.get("HL_SIZE", "10")))
    p2.add_argument("--poll-sec", type=float, default=float(os.environ.get("HL_POLL_SEC", "5")))
    p2.add_argument("--testnet", action="store_true" if os.environ.get("HL_TESTNET", "0") == "1" else "store_false")
    p2.set_defaults(func=cmd_hl_paper)

    return p


def main():
    p = build_parser()
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()