from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class InfinityGrid(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.015}
    stoploss = -0.12

    anchor_period = 100
    buy_band = 0.99
    sell_band = 1.01

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["anchor"] = ta.EMA(dataframe, timeperiod=self.anchor_period)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        p = dataframe["close"]
        a = dataframe["anchor"]
        dataframe.loc[(p < a * self.buy_band) & a.notna(), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        p = dataframe["close"]
        a = dataframe["anchor"]
        dataframe.loc[(p > a * self.sell_band) & a.notna(), "exit_long"] = 1
        return dataframe