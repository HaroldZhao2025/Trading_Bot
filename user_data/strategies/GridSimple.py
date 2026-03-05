from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class GridSimple(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.02}
    stoploss = -0.10

    grid_lower = 0.98
    grid_upper = 1.02

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sma"] = ta.SMA(dataframe, timeperiod=50)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        p = dataframe["close"]
        m = dataframe["sma"]
        dataframe.loc[(p < m * self.grid_lower), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        p = dataframe["close"]
        m = dataframe["sma"]
        dataframe.loc[(p > m * self.grid_upper), "exit_long"] = 1
        return dataframe