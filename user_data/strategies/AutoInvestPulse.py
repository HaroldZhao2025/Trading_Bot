from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import numpy as np


class AutoInvestPulse(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.01}
    stoploss = -0.25

    pulse_every = 24
    rsi_filter = 65

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["pulse"] = 0
        idx = np.arange(len(dataframe))
        dataframe.loc[idx % self.pulse_every == 0, "pulse"] = 1
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["pulse"] == 1) & (dataframe["rsi"] < self.rsi_filter),
            "enter_long"
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["rsi"] > 75),
            "exit_long"
        ] = 1
        return dataframe