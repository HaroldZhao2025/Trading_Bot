from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class DcaAccumulator(IStrategy):
    timeframe = "15m"
    minimal_roi = {"0": 0.03}
    stoploss = -0.15

    dca_trigger = -0.03
    max_dca_steps = 2

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["rsi"] < 35), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["rsi"] > 55), "exit_long"] = 1
        return dataframe

    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, min_stake, max_stake, **kwargs):
        if current_profit > self.dca_trigger:
            return None
        if trade.nr_of_successful_entries >= (1 + self.max_dca_steps):
            return None
        base = trade.stake_amount
        step = trade.nr_of_successful_entries
        add = base * (0.8 ** step)
        return add