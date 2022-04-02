# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
# --------------------------------
import numpy as np
from functools import reduce
# from tapy import Indicators

class Indicators:
    """
    **Blatantly copied from tapy indicator framework**
    Add technical indicators data to a pandas data frame
    """

    def __init__(
        self,
        df,
        open_col="Open",
        high_col="High",
        low_col="Low",
        close_col="Close",
        volume_col="Volume",
    ):
        """
        Initiate Indicators object
        :param pandas data frame df: Should contain OHLC columns and Volume column
        :param str open_col: Name of Open column in df
        :param str high_col: Name of High column in df
        :param str low_col: Name of Low column in df
        :param str close_col: Name of Close column in df
        :param str volume_col: Name of Volume column in df. This column is optional
            and require only if indicator use this data.
        """
        self.df = df
        self._columns = {
            "Open": open_col,
            "High": high_col,
            "Low": low_col,
            "Close": close_col,
            "Volume": volume_col,
        }

    def alligator(
        self,
        period_jaws=13,
        period_teeth=8,
        period_lips=5,
        shift_jaws=8,
        shift_teeth=5,
        shift_lips=3,
        column_name_jaws="alligator_jaws",
        column_name_teeth="alligator_teeth",
        column_name_lips="alligator_lips",
    ):
        """
        Alligator
        ------------------
            https://www.metatrader4.com/en/trading-platform/help/analytics/tech_indicators/alligator
            >>> Indicators.alligator(period_jaws=13, period_teeth=8, period_lips=5, shift_jaws=8, shift_teeth=5, shift_lips=3, column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth', column_name_lips='alligator_lips')
            :param int period_jaws: Period for Alligator' Jaws, default: 13
            :param int period_teeth: Period for Alligator' Teeth, default: 8
            :param int period_lips: Period for Alligator' Lips, default: 5
            :param int shift_jaws: Period for Alligator' Jaws, default: 8
            :param int shift_teeth: Period for Alligator' Teeth, default: 5
            :param int shift_lips: Period for Alligator' Lips, default: 3
            :param str column_name_jaws: Column Name for Alligator' Jaws, default: alligator_jaws
            :param str column_name_teeth: Column Name for Alligator' Teeth, default: alligator_teeth
            :param str column_name_lips: Column Name for Alligator' Lips, default: alligator_lips
            :return: None
        """
        df_median = self.df[[self._columns["High"], self._columns["Low"]]]
        median_col = "median_col"
        df_median = df_median.assign(
            median_col=lambda x: (x[self._columns["High"]] + x[self._columns["Low"]])
            / 2
        )
        df_j = self.calculate_smma(df_median, period_jaws, column_name_jaws, median_col)
        df_t = self.calculate_smma(df_median, period_teeth, column_name_teeth, median_col)
        df_l = self.calculate_smma(df_median, period_lips, column_name_lips, median_col)

        # Shift SMMAs
        df_j[column_name_jaws] = df_j[column_name_jaws].shift(shift_jaws)
        df_t[column_name_teeth] = df_t[column_name_teeth].shift(shift_teeth)
        df_l[column_name_lips] = df_l[column_name_lips].shift(shift_lips)

        self.df = self.df.merge(df_j, left_index=True, right_index=True)
        self.df = self.df.merge(df_t, left_index=True, right_index=True)
        self.df = self.df.merge(df_l, left_index=True, right_index=True)

    def calculate_smma(self, df, period, column_name, apply_to):
        """Calculate Smoothed Moving Average."""
        df_tmp = df[[apply_to]]
        first_val = df_tmp[apply_to].iloc[:period].mean()
        df_tmp = df_tmp.assign(column_name=None)
        df_tmp.at[period, column_name] = first_val
        for index, row in df_tmp.iterrows():
            if index > period:
                smma_val = (df_tmp.at[index - 1, column_name] *
                            (period - 1) + row[apply_to]) / period
                df_tmp.at[index, column_name] = smma_val
        df_tmp = df_tmp[[column_name]]
        return df_tmp


class SeeYouLater(IStrategy):
    """
        My first humble strategy using Williams Alligator Indicator and Fractals
        Changelog:
            0.9 Inital version, some improvements needed.

        https://github.com/cyberjunky/freqtrade-strategies
    """

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.2

    # Trailing stoploss
    trailing_stop = False
    trailing_only_offset_is_reached = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
    sell_profit_only = True
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 0.08,
        "36": 0.031,
        "50": 0.021,
        "60": 0.01,
        "70": 0
    }

    @property
    def plot_config(self):
        return {
            # Main plot indicators (Moving averages, ...)
            'main_plot': {
                'lips': {'color': 'green'},
                'teeth': {'color': 'red'},
                'jaw': {'color': 'blue'},
            },
            'subplots': {
                # Subplots - each dict defines one additional plot
                "sell": {
                    'bullish': {'color': 'orange'},
                },
                "buy": {
                    'bearish': {'color': 'lightgreen'},
                }
            }
        }

    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """

        # Initialize the tapy indicators, install with 'pip3 install tapy'
        # https://pandastechindicators.readthedocs.io/en/latest/#
        indicators = Indicators(dataframe,open_col='open', high_col='high', low_col='low', close_col='close', volume_col='volume')

        # Alligator
        indicators.alligator(column_name_jaws='jaw', column_name_teeth='teeth', column_name_lips='lips')
        dataframe['lips'] = indicators.df['lips']
        dataframe['jaw'] = indicators.df['jaw']
        dataframe['teeth'] = indicators.df['teeth']

        # Fractals
        dataframe['bearish'] = (
                        dataframe['high'].shift(4).lt(dataframe['high'].shift(2)) &
                        dataframe['high'].shift(3).lt(dataframe['high'].shift(2)) &
                        dataframe['high'].shift(1).lt(dataframe['high'].shift(2)) &
                        dataframe['high'].lt(dataframe['high'].shift(2))
                )

        dataframe['bullish'] = (
                dataframe['low'].shift(4).gt(dataframe['low'].shift(2)) &
                dataframe['low'].shift(3).gt(dataframe['low'].shift(2)) &
                dataframe['low'].shift(1).gt(dataframe['low'].shift(2)) &
                dataframe['low'].gt(dataframe['high'].shift(2))
        )

        return dataframe


    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        If the bullish fractal is active and below the teeth of the gator -> buy
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        conditions = []
        conditions.append(
            (
                (dataframe['bearish']) &
                (dataframe['close'] < dataframe['teeth'] ) &
                (dataframe['volume'] > 0)
            )
        )

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy']=1

        return dataframe


    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        If the bearish fractal is active and above the teeth of the gator -> sell
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        conditions = []
        conditions.append(
            (
                (dataframe['bullish']) &
                (dataframe['close'] > dataframe['teeth'] ) &
                (dataframe['volume'] > 0)
            )
        )

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'sell']=1

        return dataframe
