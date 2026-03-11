from freqtrade.strategy import IStrategy
from pandas import DataFrame


class ZScoreMeanReversion(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.015}
    stoploss = -0.08

    lookback = 50
    z_entry = -2.0
    z_exit = 0.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        mean = dataframe["close"].rolling(self.lookback).mean()
        std = dataframe["close"].rolling(self.lookback).std()
        dataframe["zscore"] = (dataframe["close"] - mean) / std.replace(0, 1.0)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["zscore"] < self.z_entry) & dataframe["zscore"].notna(),
            "enter_long"
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["zscore"] > self.z_exit) & dataframe["zscore"].notna(),
            "exit_long"
        ] = 1
        return dataframe