from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class CtaTrend(IStrategy):
    timeframe = "1h"
    minimal_roi = {"0": 0.05}
    stoploss = -0.12

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["fast"] = ta.SMA(dataframe, timeperiod=20)
        dataframe["slow"] = ta.SMA(dataframe, timeperiod=80)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["fast"] > dataframe["slow"]), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["fast"] < dataframe["slow"]), "exit_long"] = 1
        return dataframe