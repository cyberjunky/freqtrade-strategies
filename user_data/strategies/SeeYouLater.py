# --- Do not remove these libs ---
from functools import reduce

from pandas import DataFrame
from tapy import Indicators

from freqtrade.strategy.interface import IStrategy


# --------------------------------


class SeeYouLater(IStrategy):
    """
    My first humble strategy using Williams Alligator and Fractals
    Changelog:
        0.9 Inital version, some improvements needed.

    https://gthub.com/cyberjunky/freqtrade-strategies
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
    timeframe = "5m"

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {"0": 0.08, "36": 0.031, "50": 0.021, "60": 0.01, "70": 0}

    @property
    def plot_config(self):
        """Built-in plot."""
        return {
            # Main plot indicators (Moving averages, ...)
            "main_plot": {
                "lips": {"color": "green"},
                "teeth": {"color": "red"},
                "jaw": {"color": "blue"},
            },
            "subplots": {
                # Subplots - each dict defines one additional plot
                "sell": {
                    "bull_fractal": {"color": "orange"},
                },
                "buy": {
                    "bear_fractal": {"color": "royalblue"},
                },
            },
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

        # Initialize the tapy framework, install with 'pip3 install tapy'
        # https://pandastechindicators.readthedocs.io/en/latest/#
        indicators = Indicators(
            dataframe,
            open_col="open",
            high_col="high",
            low_col="low",
            close_col="close",
            volume_col="volume",
        )

        # Alligator
        indicators.alligator(
            column_name_jaws="jaw", column_name_teeth="teeth", column_name_lips="lips"
        )
        dataframe["lips"] = indicators.df["lips"]
        dataframe["jaw"] = indicators.df["jaw"]
        dataframe["teeth"] = indicators.df["teeth"]

        # Fractals
        indicators.fractals(column_name_high="bear", column_name_low="bull")
        dataframe["bear_fractal"] = indicators.df["bear"]
        dataframe["bull_fractal"] = indicators.df["bull"]

        # This one lags 1 candle and has less triggers (not sure with is the best yet, also both are different from TV indicator still)
        # dataframe['bull_fractal'] = (
        #                 dataframe['high'].shift(4).lt(dataframe['high'].shift(2)) &
        #                 dataframe['high'].shift(3).lt(dataframe['high'].shift(2)) &
        #                 dataframe['high'].shift(1).lt(dataframe['high'].shift(2)) &
        #                 dataframe['high'].lt(dataframe['high'].shift(2))
        #         )

        # dataframe['bear_fractal'] = (
        #         dataframe['low'].shift(4).gt(dataframe['low'].shift(2)) &
        #         dataframe['low'].shift(3).gt(dataframe['low'].shift(2)) &
        #         dataframe['low'].shift(1).gt(dataframe['low'].shift(2)) &
        #         dataframe['low'].gt(dataframe['high'].shift(2))
        # )

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        If the bearish fractal is active and below the teeth of the gator -> buy
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        conditions = []
        conditions.append(
            (
                (dataframe["bear_fractal"])
                & (dataframe["close"] < dataframe["teeth"])
                & (dataframe["volume"] > 0)
            )
        )

        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), "buy"] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        If the bullish fractal is active and above the teeth of the gator -> sell
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        conditions = []
        conditions.append(
            (
                (dataframe["bull_fractal"])
                & (dataframe["close"] > dataframe["teeth"])
                & (dataframe["volume"] > 0)
            )
        )

        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), "sell"] = 1

        return dataframe
