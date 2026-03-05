from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class AtrBreakout(IStrategy):
    timeframe = "1h"
    minimal_roi = {"0": 0.05}
    stoploss = -0.12

    atr_mult = 1.5

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["sma"] = ta.SMA(dataframe, timeperiod=50)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] > dataframe["sma"] + dataframe["atr"] * self.atr_mult),
            "enter_long"
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] < dataframe["sma"]),
            "exit_long"
        ] = 1
        return dataframe