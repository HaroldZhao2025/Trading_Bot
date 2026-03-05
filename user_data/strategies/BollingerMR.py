from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class BollingerMR(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.015}
    stoploss = -0.08

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        bb = ta.BBANDS(dataframe["close"], timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)

        if isinstance(bb, (list, tuple)) and len(bb) == 3:
            upper, middle, lower = bb[0], bb[1], bb[2]
        else:
            upper, middle, lower = bb["upperband"], bb["middleband"], bb["lowerband"]

        dataframe["bb_upper"] = upper
        dataframe["bb_middle"] = middle
        dataframe["bb_lower"] = lower
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] < dataframe["bb_lower"]) & (dataframe["rsi"] < 40),
            "enter_long"
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] > dataframe["bb_middle"]) | (dataframe["rsi"] > 60),
            "exit_long"
        ] = 1
        return dataframe