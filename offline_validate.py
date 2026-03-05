import os
import numpy as np
import pandas as pd
from importlib import import_module
from freqtrade.strategy import IStrategy

MIN_CONFIG = {
    "dry_run": True,
    "stake_currency": "USDT",
    "stake_amount": "unlimited",
    "timeframe": "5m",
    "max_open_trades": 1,
    "exchange": {"name": "dummy"},
}

def make_df(n=300, freq="5min"):
    ts = pd.date_range("2024-01-01", periods=n, freq=freq)
    price = 100 + np.cumsum(np.random.normal(0, 0.2, size=n))
    return pd.DataFrame({
        "date": ts,
        "open": price + np.random.normal(0, 0.05, size=n),
        "high": price + np.abs(np.random.normal(0.1, 0.05, size=n)),
        "low":  price - np.abs(np.random.normal(0.1, 0.05, size=n)),
        "close": price,
        "volume": np.random.randint(100, 1000, size=n),
    })

def normalize_freq(tf: str) -> str:
    tf = str(tf).strip()
    if tf.endswith("m"):
        return tf[:-1] + "min"
    if tf.endswith("h"):
        return tf[:-1] + "h"
    return "5min"

def iter_strategy_modules(base="/freqtrade/user_data/strategies"):
    for fn in os.listdir(base):
        if not fn.endswith(".py"):
            continue
        if fn.startswith("_"):
            continue
        mod = fn[:-3]
        if "." in mod:
            continue
        yield mod

def find_strategy_class(module_name: str):
    mod = import_module(f"user_data.strategies.{module_name}")

    candidates = []
    for v in mod.__dict__.values():
        if not isinstance(v, type):
            continue
        if v is IStrategy:
            continue
        if not issubclass(v, IStrategy):
            continue
        if getattr(v, "__abstractmethods__", None):
            if len(v.__abstractmethods__) > 0:
                continue
        candidates.append(v)

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    def score(cls):
        s = 0
        if cls.__name__.lower() == module_name.lower():
            s += 10
        if cls.__name__.lower().startswith(module_name.lower()):
            s += 5
        return s

    candidates.sort(key=score, reverse=True)
    return candidates[0]

def run_one(module_name: str):
    try:
        cls = find_strategy_class(module_name)
        if cls is None:
            print(f"[SKIP] {module_name}: no concrete IStrategy subclass")
            return

        s = cls(MIN_CONFIG)
        freq = normalize_freq(getattr(s, "timeframe", "5m"))
        df = make_df(freq=freq)
        md = {"pair": "BTC/USDT"}

        df = s.populate_indicators(df, md)
        df = s.populate_entry_trend(df, md)
        df = s.populate_exit_trend(df, md)

        has_entry = any(c in df.columns for c in ["enter_long", "enter_short", "entry"])
        has_exit = any(c in df.columns for c in ["exit_long", "exit_short", "exit"])
        print(f"[OK] {module_name} class={s.__class__.__name__} entry={has_entry} exit={has_exit} cols={len(df.columns)} rows={len(df)}")
    except Exception as e:
        print(f"[FAIL] {module_name}: {type(e).__name__}: {e}")

def main():
    for m in sorted(iter_strategy_modules()):
        run_one(m)

if __name__ == "__main__":
    main()