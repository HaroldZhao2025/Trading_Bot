from freqtrade.strategy import IStrategy
from pandas import DataFrame
import numpy as np
import talib.abstract as ta


class RebalancePulse(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.01}
    stoploss = -0.20

    rebalance_every = 48
    vol_period = 48

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        r = ta.ROC(dataframe, timeperiod=1) / 100.0
        v = r.rolling(self.vol_period).std()
        v = v.replace(0, np.nan)
        dataframe["vol"] = v
        dataframe["rebalance_pulse"] = 0
        idx = np.arange(len(dataframe))
        dataframe.loc[idx % self.rebalance_every == 0, "rebalance_pulse"] = 1
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["rebalance_pulse"] == 1) & dataframe["vol"].notna(),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["rebalance_pulse"].shift(1) == 1),
            "exit_long",
        ] = 1
        return dataframe