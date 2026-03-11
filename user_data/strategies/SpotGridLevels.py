from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class SpotGridLevels(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.02}
    stoploss = -0.12

    sma_period = 50
    grid_step_pct = 0.005
    grid_levels = 3

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sma"] = ta.SMA(dataframe, timeperiod=self.sma_period)
        p = dataframe["close"]
        m = dataframe["sma"]

        lower = m * (1.0 - self.grid_levels * self.grid_step_pct)
        upper = m * (1.0 + self.grid_levels * self.grid_step_pct)

        dataframe["grid_lower"] = lower
        dataframe["grid_upper"] = upper
        dataframe["grid_z"] = (p - m) / (m.replace(0, 1.0))

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] < dataframe["grid_lower"]) & dataframe["sma"].notna(),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] > dataframe["grid_upper"]) & dataframe["sma"].notna(),
            "exit_long",
        ] = 1
        return dataframe