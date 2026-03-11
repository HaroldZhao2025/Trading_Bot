import os
import traceback
from importlib import import_module
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

MIN_CONFIG = {
    "dry_run": True,
    "stake_currency": "USDT",
    "stake_amount": "unlimited",
    "timeframe": "5m",
    "max_open_trades": 1,
    "exchange": {"name": "dummy"},
}


def normalize_freq(tf: str) -> str:
    tf = str(tf).strip().lower()
    if tf.endswith("m"):
        return tf[:-1] + "min"
    if tf.endswith("h"):
        return tf[:-1] + "h"
    if tf.endswith("d"):
        return tf[:-1] + "d"
    return "5min"


def make_df(n: int = 300, freq: str = "5min") -> DataFrame:
    ts = pd.date_range("2024-01-01", periods=n, freq=freq)
    price = 100 + np.cumsum(np.random.normal(0, 0.2, size=n))
    df = pd.DataFrame(
        {
            "date": ts,
            "open": price + np.random.normal(0, 0.05, size=n),
            "high": price + np.abs(np.random.normal(0.1, 0.05, size=n)),
            "low": price - np.abs(np.random.normal(0.1, 0.05, size=n)),
            "close": price,
            "volume": np.random.randint(100, 1000, size=n),
        }
    )
    return df


def list_strategy_modules(strategy_dir: str = "user_data/strategies") -> List[str]:
    mods = []
    for fn in os.listdir(strategy_dir):
        if not fn.endswith(".py"):
            continue
        if fn.startswith("_"):
            continue
        name = fn[:-3]
        if name.endswith(".py"):
            name = name[:-3]
        mods.append(name)
    mods.sort()
    return mods


def load_strategy_class(module_name: str):
    mod = import_module(f"user_data.strategies.{module_name}")
    cls = getattr(mod, module_name, None)
    if cls is not None:
        return cls
    for v in vars(mod).values():
        if isinstance(v, type) and v.__name__ == module_name:
            return v
    raise RuntimeError(f"Strategy class not found in module {module_name}")


def run_strategy(module_name: str) -> Tuple[bool, str]:
    try:
        cls = load_strategy_class(module_name)
        s = cls(MIN_CONFIG)

        tf = getattr(s, "timeframe", "5m")
        df = make_df(freq=normalize_freq(tf))
        md = {"pair": "BTC/USDT"}

        df = s.populate_indicators(df, md)
        df = s.populate_entry_trend(df, md)
        df = s.populate_exit_trend(df, md)

        has_entry = any(c in df.columns for c in ["enter_long", "enter_short", "entry"])
        has_exit = any(c in df.columns for c in ["exit_long", "exit_short", "exit"])

        msg = f"[OK] {module_name} class={cls.__name__} entry={has_entry} exit={has_exit} cols={len(df.columns)} rows={len(df)}"
        return True, msg
    except Exception as e:
        tb = traceback.format_exc(limit=4)
        return False, f"[FAIL] {module_name}: {type(e).__name__}: {e}\n{tb}"


def main():
    mods = list_strategy_modules()
    ok = 0
    fail = 0

    for m in mods:
        good, msg = run_strategy(m)
        print(msg, flush=True)
        if good:
            ok += 1
        else:
            fail += 1

    print(f"\nSummary: OK={ok} FAIL={fail} TOTAL={ok+fail}", flush=True)
    if fail > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()