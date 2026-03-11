from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class MacdTrendFollow(IStrategy):
    timeframe = "15m"
    minimal_roi = {"0": 0.025}
    stoploss = -0.10

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]
        dataframe["ema200"] = ta.EMA(dataframe, timeperiod=200)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["macd"] > dataframe["macdsignal"]) &
            (dataframe["macd"].shift(1) <= dataframe["macdsignal"].shift(1)) &
            (dataframe["close"] > dataframe["ema200"]),
            "enter_long"
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["macd"] < dataframe["macdsignal"]) |
            (dataframe["close"] < dataframe["ema200"]),
            "exit_long"
        ] = 1
        return dataframe