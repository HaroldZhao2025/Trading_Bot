from freqtrade.strategy import IStrategy
from pandas import DataFrame

class DonchianBreakout(IStrategy):
    timeframe = "1h"
    minimal_roi = {"0": 0.06}
    stoploss = -0.12

    lookback = 20

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["dc_high"] = dataframe["high"].rolling(self.lookback).max()
        dataframe["dc_low"] = dataframe["low"].rolling(self.lookback).min()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["close"] > dataframe["dc_high"].shift(1)), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["close"] < dataframe["dc_low"].shift(1)), "exit_long"] = 1
        return dataframe