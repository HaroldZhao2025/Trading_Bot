from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class RsiMeanReversion(IStrategy):
    timeframe = "15m"
    minimal_roi = {"0": 0.02}
    stoploss = -0.10

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["rsi"] < 30), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["rsi"] > 55), "exit_long"] = 1
        return dataframe