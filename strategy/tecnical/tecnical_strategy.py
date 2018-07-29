# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
from enum import Enum

import talib.abstract as ta
from pandas import DataFrame

import strategy.tecnical.indicators as qtpylib
from .indicator_helpers import fishers_inverse


class SignalType(Enum):
    """
    Enum to distinguish between buy and sell signals
    """
    BUY = "buy"
    SELL = "sell"


class TecnicalAnalysisStrategy:
    """
    Default Strategy provided by freqtrade bot.
    You can override it with your own strategy
    """

    # Optimal ticker interval for the strategy
    ticker_interval = '5m'

    def populate_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame
        """

        # Momentum Indicator
        # ------------------------------------

        # ADX - trend and the strong of the trend, no direction
        dataframe['adx'] = ta.ADX(dataframe)

        # Awesome oscillator - distance between emas, it indicates if the price is going down or up
        # dataframe['ao'] = qtpylib.awesome_oscillator(dataframe)

        # Commodity Channel Index: values Oversold:<-100, Overbought:>100
        # dataframe['cci'] = ta.CCI(dataframe)

        # MACD
        # macd = ta.MACD(dataframe)
        # dataframe['macd'] = macd['macd']
        # dataframe['macdsignal'] = macd['macdsignal']
        # dataframe['macdhist'] = macd['macdhist']

        # MFI
        # dataframe['mfi'] = ta.MFI(dataframe)

        # Minus Directional Indicator / Movement - DMI - good way of get direction
        # dataframe['minus_dm'] = ta.MINUS_DM(dataframe)

        # # Plus Directional Indicator / Movement
        # dataframe['plus_dm'] = ta.PLUS_DM(dataframe)
        # dataframe['minus_di'] = ta.MINUS_DI(dataframe)

        # dataframe['minus_di'] = ta.MINUS_DI(dataframe)
        # dataframe['plus_di'] = ta.PLUS_DI(dataframe)

        """
        # ROC
        dataframe['roc'] = ta.ROC(dataframe)
        """
        # RSI
        # dataframe['rsi'] = ta.RSI(dataframe)
        #
        # # Inverse Fisher transform on RSI, values [-1.0, 1.0] (https://goo.gl/2JGGoy)
        # dataframe['fisher_rsi'] = fishers_inverse(dataframe['rsi'])
        #
        # # Inverse Fisher transform on RSI normalized, value [0.0, 100.0] (https://goo.gl/2JGGoy)
        # dataframe['fisher_rsi_norma'] = 50 * (dataframe['fisher_rsi'] + 1)

        # # Stoch
        # stoch = ta.STOCH(dataframe)
        # dataframe['slowd'] = stoch['slowd']
        # dataframe['slowk'] = stoch['slowk']
        #
        # # Stoch fast
        # stoch_fast = ta.STOCHF(dataframe)
        # dataframe['fastd'] = stoch_fast['fastd']
        # dataframe['fastk'] = stoch_fast['fastk']
        #
        # # Stoch RSI
        # stoch_rsi = ta.STOCHRSI(dataframe)
        # dataframe['fastd_rsi'] = stoch_rsi['fastd']
        # dataframe['fastk_rsi'] = stoch_rsi['fastk']

        # Overlap Studies
        # ------------------------------------

        # Previous Bollinger bands
        # Because ta.BBANDS implementation is broken with small numbers, it actually
        # returns middle band for all the three bands. Switch to qtpylib.bollinger_bands
        # and use middle band instead.
        dataframe['blower'] = ta.BBANDS(dataframe, nbdevup=2, nbdevdn=2)['lowerband']

        # Bollinger bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']

        # # EMA - Exponential Moving Average
        # dataframe['ema3'] = ta.EMA(dataframe, timeperiod=3)
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema10'] = ta.EMA(dataframe, timeperiod=10)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        # dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)
        #
        # # SAR Parabol
        dataframe['sar'] = ta.SAR(dataframe)
        #
        # # SMA - Simple Moving Average
        dataframe['sma'] = ta.SMA(dataframe, timeperiod=5)
        #
        # # TEMA - Triple Exponential Moving Average
        dataframe['tema'] = ta.TEMA(dataframe, timeperiod=9)
        #
        # # Cycle Indicator
        # # ------------------------------------
        # # Hilbert Transform Indicator - SineWave
        # hilbert = ta.HT_SINE(dataframe)
        # dataframe['htsine'] = hilbert['sine']
        # dataframe['htleadsine'] = hilbert['leadsine']
        #
        # # Pattern Recognition - Bullish candlestick patterns
        # # ------------------------------------
        #
        # # Hammer: values [0, 100]
        # dataframe['CDLHAMMER'] = ta.CDLHAMMER(dataframe)
        # # Inverted Hammer: values [0, 100]
        # dataframe['CDLINVERTEDHAMMER'] = ta.CDLINVERTEDHAMMER(dataframe)
        # # Dragonfly Doji: values [0, 100]
        # dataframe['CDLDRAGONFLYDOJI'] = ta.CDLDRAGONFLYDOJI(dataframe)
        # # Piercing Line: values [0, 100]
        # dataframe['CDLPIERCING'] = ta.CDLPIERCING(dataframe)  # values [0, 100]
        # # Morningstar: values [0, 100]
        # dataframe['CDLMORNINGSTAR'] = ta.CDLMORNINGSTAR(dataframe)  # values [0, 100]
        # # Three White Soldiers: values [0, 100]
        # dataframe['CDL3WHITESOLDIERS'] = ta.CDL3WHITESOLDIERS(dataframe)  # values [0, 100]
        #
        # # Pattern Recognition - Bearish candlestick patterns
        # # ------------------------------------
        #
        # # Hanging Man: values [0, 100]
        # dataframe['CDLHANGINGMAN'] = ta.CDLHANGINGMAN(dataframe)
        # # Shooting Star: values [0, 100]
        # dataframe['CDLSHOOTINGSTAR'] = ta.CDLSHOOTINGSTAR(dataframe)
        # # Gravestone Doji: values [0, 100]
        # dataframe['CDLGRAVESTONEDOJI'] = ta.CDLGRAVESTONEDOJI(dataframe)
        # # Dark Cloud Cover: values [0, 100]
        # dataframe['CDLDARKCLOUDCOVER'] = ta.CDLDARKCLOUDCOVER(dataframe)
        # # Evening Doji Star: values [0, 100]
        # dataframe['CDLEVENINGDOJISTAR'] = ta.CDLEVENINGDOJISTAR(dataframe)
        # # Evening Star: values [0, 100]
        # dataframe['CDLEVENINGSTAR'] = ta.CDLEVENINGSTAR(dataframe)

        # Pattern Recognition - Bullish/Bearish candlestick patterns
        # ------------------------------------

        # # Three Line Strike: values [0, -100, 100]
        # dataframe['CDL3LINESTRIKE'] = ta.CDL3LINESTRIKE(dataframe)
        # # Spinning Top: values [0, -100, 100]
        # dataframe['CDLSPINNINGTOP'] = ta.CDLSPINNINGTOP(dataframe)  # values [0, -100, 100]
        # # Engulfing: values [0, -100, 100]
        # dataframe['CDLENGULFING'] = ta.CDLENGULFING(dataframe)  # values [0, -100, 100]
        # # Harami: values [0, -100, 100]
        # dataframe['CDLHARAMI'] = ta.CDLHARAMI(dataframe)  # values [0, -100, 100]
        # # Three Outside Up/Down: values [0, -100, 100]
        # dataframe['CDL3OUTSIDE'] = ta.CDL3OUTSIDE(dataframe)  # values [0, -100, 100]
        # # Three Inside Up/Down: values [0, -100, 100]
        # dataframe['CDL3INSIDE'] = ta.CDL3INSIDE(dataframe)  # values [0, -100, 100]

        # Chart type
        # ------------------------------------
        # Heikinashi stategy
        # heikinashi = qtpylib.heikinashi(dataframe)
        # dataframe['ha_open'] = heikinashi['open']
        # dataframe['ha_close'] = heikinashi['close']
        # dataframe['ha_high'] = heikinashi['high']
        # dataframe['ha_low'] = heikinashi['low']

        dataframe['trailing_stop'] = dataframe['close'] * 0.90

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        shiftted = dataframe.shift(2)
        dataframe.loc[
            (
                    (
                            (dataframe['close'] > dataframe['bb_middleband'])
                            & (shiftted['close'] <= shiftted['bb_middleband'])
                    ) |
                    (
                            (dataframe['close'] > dataframe['bb_lowerband']) &
                            (shiftted['close'] < shiftted['bb_lowerband'])
                    )
                    | (
                            (dataframe['sma'] > dataframe['bb_middleband'])
                            & (shiftted['sma'] <= shiftted['bb_middleband'])
                    )
            ), 'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        shiftted = dataframe.shift(2)
        dataframe.loc[
            (
                    (dataframe['close'] < dataframe['bb_middleband']) &
                    (shiftted['close'] > shiftted['bb_middleband'])
            )
            | (
                    (dataframe['close'] < dataframe['bb_lowerband']) &
                    (shiftted['close'] > shiftted['bb_lowerband'])
            )
            , 'sell'] = 1
        return dataframe

    def analyze_ticker(self, ticker_history: list) -> DataFrame:
        """
        Parses the given ticker history and returns a populated DataFrame
        add several TA indicators and buy signal to it
        :return DataFrame with ticker data and indicator data
        """
        dataframe = self.populate_indicators(ticker_history)
        dataframe = self.populate_buy_trend(dataframe)
        dataframe = self.populate_sell_trend(dataframe)
        return dataframe

    def get_signal(self, ticker_hist: DataFrame):
        """
        Calculates current signal based several technical analysis indicators
        :param pair: pair in format ANT/BTC
        :param start:
        :param end:
        :return: (Buy, Sell) A bool-tuple indicating buy/sell signal
        """

        dataframe = self.get_historical_signals(ticker_hist)

        if dataframe.empty:
            print('Empty dataframe')
            return False, False

        latest = dataframe.iloc[-1]

        (buy, sell) = latest[SignalType.BUY.value] == 1, latest[SignalType.SELL.value] == 1
        print(
            'trigger: %s buy=%s sell=%s',
            latest['date'],
            str(buy),
            str(sell)
        )
        return buy, sell

    def get_historical_signals(self, ticker_hist: DataFrame):
        if ticker_hist.empty:
            print('Empty ticker history')
            return DataFrame()

        try:
            dataframe = self.analyze_ticker(ticker_hist)
        except ValueError as error:
            print(
                'Unable to analyze ticker %s',
                str(error)
            )
            return DataFrame()
        except Exception as error:
            print(
                'Unexpected error when analyzing ticker %s',
                str(error)
            )
            return DataFrame()
        return dataframe
