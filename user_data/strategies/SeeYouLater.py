# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
# --------------------------------
import numpy as np
from functools import reduce

def alligator(
    
    dataframe,
    period_jaw=13,
    period_teeth=8,
    period_lips=5,
    shift_jaw=8,
    shift_teeth=5,
    shift_lips=3,
):
    """Construct Williams Alligator."""
    data = dataframe.copy()
    
    df_tmp = data[["high", "low"]]
    col_tmp = "col_tmp"
    df_tmp = df_tmp.assign(
        col_tmp=lambda x: (x["high"] + x["low"])
        / 2
    )
    df_j = calculate_smma(df_tmp, period_jaw, 'jaw', col_tmp)
    df_t = calculate_smma(df_tmp, period_teeth, 'teeth', col_tmp)
    df_l = calculate_smma(df_tmp, period_lips, 'lips', col_tmp)

    # Shift SMMAs
    df_j['jaw'] = df_j['jaw'].shift(shift_jaw)
    df_t['teeth'] = df_t['teeth'].shift(shift_teeth)
    df_l['lips'] = df_l['lips'].shift(shift_lips)

    data = data.merge(df_j, left_index=True, right_index=True)
    data = data.merge(df_t, left_index=True, right_index=True)
    data = data.merge(df_l, left_index=True, right_index=True)

    return data


def calculate_smma(df, period, column_name, apply_to):
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
            0.9 Inital version, some improvements needed
            1.0 Code optimizations

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

        # Williams Alligator
        gator_df = alligator(dataframe)
        dataframe['lips'] = gator_df['lips']
        dataframe['jaw'] = gator_df['jaw']
        dataframe['teeth'] = gator_df['teeth']

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
