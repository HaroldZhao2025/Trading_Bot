from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class FundingArbSignal(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.005}
    stoploss = -0.30

    sma_period = 96
    threshold_bps = 8.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sma"] = ta.SMA(dataframe, timeperiod=self.sma_period)
        p = dataframe["close"]
        m = dataframe["sma"]
        proxy = (p - m) / m * 10000.0
        dataframe["funding_proxy_bps"] = proxy
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["funding_proxy_bps"] > self.threshold_bps) & dataframe["sma"].notna(),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["funding_proxy_bps"] < 0) & dataframe["sma"].notna(),
            "exit_long",
        ] = 1
        return dataframe