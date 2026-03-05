from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class MartingaleGuarded(IStrategy):
    timeframe = "5m"
    minimal_roi = {"0": 0.01}
    stoploss = -0.08

    max_dca_steps = 2
    dca_trigger = -0.02

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["rsi"] < 30), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["rsi"] > 55), "exit_long"] = 1
        return dataframe

    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, min_stake, max_stake, **kwargs):
        if current_profit > self.dca_trigger:
            return None
        if trade.nr_of_successful_exits > 0:
            return None
        if trade.nr_of_successful_entries >= (1 + self.max_dca_steps):
            return None
        base = trade.stake_amount
        step = trade.nr_of_successful_entries
        add = base * (2 ** step)
        return add