import os

import pandas as pd

from strategy.tecnical.tecnical_strategy import TecnicalAnalysisStrategy
from ..price_parser import PriceParser
from .base import AbstractBarPriceHandler
from ..event import BarEvent


class YahooDailyCsvBarPriceHandler(AbstractBarPriceHandler):
    """
    YahooDailyBarPriceHandler is designed to read CSV files of
    Yahoo Finance daily Open-High-Low-Close-Volume (OHLCV) data
    for each requested financial instrument and stream those to
    the provided events queue as BarEvents.
    """
    def __init__(
        self, csv_dir, events_queue,
        init_tickers=None,
        start_date=None, end_date=None,
        calc_adj_returns=False
    ):
        """
        Takes the CSV directory, the events queue and a possible
        list of initial ticker symbols then creates an (optional)
        list of ticker subscriptions and associated prices.
        """
        self.csv_dir = csv_dir
        self.events_queue = events_queue
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)
        self.start_date = start_date
        self.end_date = end_date
        self.bar_stream = self._merge_sort_ticker_data()
        self._set_signals_from_price()
        self.calc_adj_returns = calc_adj_returns
        if self.calc_adj_returns:
            self.adj_close_returns = []

    def _open_ticker_price_csv(self, ticker):
        """
        Opens the CSV files containing the equities ticks from
        the specified CSV data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.
        """
        ticker_path = os.path.join(self.csv_dir, "%s.csv" % ticker)
        self.tickers_data[ticker] = pd.io.parsers.read_csv(
            ticker_path, header=0, parse_dates=True,
            index_col=0, names=(
                "Date", "Open", "High", "Low",
                "Close", "Volume", "Adj Close"
            )
        )
        self.tickers_data[ticker]["Ticker"] = ticker

    def _merge_sort_ticker_data(self):
        """
        Concatenates all of the separate equities DataFrames
        into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion.

        Note that this is an idealised situation, utilised solely for
        backtesting. In live trading ticks may arrive "out of order".
        """
        df = pd.concat(self.tickers_data.values()).sort_index()
        start = None
        end = None
        if self.start_date is not None:
            start = df.index.searchsorted(self.start_date)
        if self.end_date is not None:
            end = df.index.searchsorted(self.end_date)
        # This is added so that the ticker events are
        # always deterministic, otherwise unit test values
        # will differ
        df['colFromIndex'] = df.index
        df = df.sort_values(by=["colFromIndex", "Ticker"])
        if start is None and end is None:
            return df.iterrows()
        elif start is not None and end is None:
            return df.ix[start:].iterrows()
        elif start is None and end is not None:
            return df.ix[:end].iterrows()
        else:
            return df.ix[start:end]

    def subscribe_ticker(self, ticker):
        """
        Subscribes the price handler to a new ticker symbol.
        """
        if ticker not in self.tickers:
            try:
                self._open_ticker_price_csv(ticker)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]

                close = PriceParser.parse(row0["Close"])
                adj_close = PriceParser.parse(row0["Adj Close"])

                ticker_prices = {
                    "close": close,
                    "adj_close": adj_close,
                    "timestamp": dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    "Could not subscribe ticker %s "
                    "as no data CSV found for pricing." % ticker
                )
        else:
            print(
                "Could not subscribe ticker %s "
                "as is already subscribed." % ticker
            )

    def _create_event(self, index, period, ticker, row):
        """
        Obtain all elements of the bar from a row of dataframe
        and return a BarEvent
        """
        open_price = PriceParser.parse(row["Open"])
        high_price = PriceParser.parse(row["High"])
        low_price = PriceParser.parse(row["Low"])
        close_price = PriceParser.parse(row["Close"])
        adj_close_price = PriceParser.parse(row["Adj Close"])
        volume = int(row["Volume"]),
        signal = self.signals.loc[(self.signals['date'] == index) & (self.signals['symbol'] == ticker)]
        bev = BarEvent(
            ticker, index, period, open_price,
            high_price, low_price, close_price,
            volume, adj_close_price,signal
        )
        return bev

    def _store_event(self, event):
        """
        Store price event for closing price and adjusted closing price
        """
        ticker = event.ticker
        # If the calc_adj_returns flag is True, then calculate
        # and store the full list of adjusted closing price
        # percentage returns in a list
        # TODO: Make this faster
        if self.calc_adj_returns:
            prev_adj_close = self.tickers[ticker][
                "adj_close"
            ] / float(PriceParser.PRICE_MULTIPLIER)
            cur_adj_close = event.adj_close_price / float(
                PriceParser.PRICE_MULTIPLIER
            )
            self.tickers[ticker][
                "adj_close_ret"
            ] = cur_adj_close / prev_adj_close - 1.0
            self.adj_close_returns.append(self.tickers[ticker]["adj_close_ret"])
        self.tickers[ticker]["close"] = event.close_price
        self.tickers[ticker]["adj_close"] = event.adj_close_price
        self.tickers[ticker]["timestamp"] = event.time

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            index, row = next(self.bar_stream)
        except StopIteration:
            self.continue_backtest = False
            return
        # Obtain all elements of the bar from the dataframe
        ticker = row["Ticker"]
        period = 86400  # Seconds in a day
        # Create the tick event for the queue
        bev = self._create_event(index, period, ticker, row)
        # Store event
        self._store_event(bev)
        # Send event to queue
        self.events_queue.put(bev)

    def _set_signals_from_price(self):
        prices = []
        for row2 in self.bar_stream.iterrows():
            row = row2[1]
            time = row2[0]
            # Obtain all elements of the bar from the dataframe
            ticker = row["Ticker"]
            # Create the tick event for the queue
            open_price = row["Open"]
            high_price = row["High"]
            low_price = row["Low"]
            close_price = row["Close"]
            adj_close_price = row["Adj Close"]
            volume = row["Volume"]

            price = {
                'open': float(open_price),
                'close': float(close_price),
                'high': float(high_price),
                'low': float(low_price),
                'date': time,
                'symbol': ticker,
                'volume': float(volume)
            }
            prices.append(price)
        prices = pd.DataFrame.from_dict(prices)
        tecnical = TecnicalAnalysisStrategy()
        self.signals = tecnical.get_historical_signals(prices)
        self.signals['buy'].fillna(0, inplace=True)
        self.signals['sell'].fillna(0, inplace=True)
        self.signals['sma'].fillna(0, inplace=True)
        self.signals.set_index('date', drop=False, inplace=True)

        signals = self.signals[self.signals['symbol'] == 'AAPL']
        # signals['bb_lowerband'].plot()
        # signals['bb_middleband'].plot()
        # signals['bb_upperband'].plot()
        # signals['close'].plot()
        # signals['sma'].plot(label='sma 50')
        # signals['adx'].plot()

        # signals['ema5'].plot(label='ema 5')
        # signals['ema50'].plot(label='ema 50')
        # buys = signals[signals['buy'] ==1]
        # plt.show()
        print('')
        self.bar_stream = self.bar_stream.iterrows()

