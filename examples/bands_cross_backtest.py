from collections import deque
import datetime

import numpy as np
from pandas import DataFrame, to_datetime

from qstrader import settings
from qstrader.strategy.base import AbstractStrategy
from qstrader.event import SignalEvent, EventType
from qstrader.compat import queue
from qstrader.trading_session import TradingSession
from strategy.tecnical.tecnical_strategy import TecnicalAnalysisStrategy


class MovingAverageCrossStrategy(AbstractStrategy):
    """
    Requires:
    ticker - The ticker symbol being used for moving averages
    events_queue - A handle to the system events queue
    short_window - Lookback period for short moving average
    long_window - Lookback period for long moving average
    """

    def __init__(
            self, ticker,
            events_queue,
            short_window=100,
            long_window=300,
            base_quantity=100
    ):
        self.ticker = ticker
        self.events_queue = events_queue
        self.short_window = short_window
        self.long_window = long_window
        self.base_quantity = base_quantity
        self.bars = 0
        self.invested = False
        self.sw_bars = deque(maxlen=self.short_window)
        self.lw_bars = deque(maxlen=self.long_window)
        self.prices = DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        self.strategy = TecnicalAnalysisStrategy()
        self.entry_time = None
        self.signals = DataFrame()

    def calculate_signals(self, event):
        if (
                event.type == EventType.BAR and
                event.ticker == self.ticker
        ):
            exit_position = False
            signal = event.signal[event.signal['symbol'] == event.ticker]
            self.signals = self.signals.append(signal)

            if self.invested:
                # exit_position = self.expired_not_profit()
                if not exit_position and len(self.signals) > 2:
                    two_ago = self.signals.iloc[-2]
                    one_ago = self.signals.iloc[-1]

                    exit_position = (
                            (one_ago['sma'] < one_ago['bb_middleband']) and
                            (two_ago['sma'] > two_ago['bb_middleband'])
                            # and len(went_up) < 1
                    )
                    if exit_position:
                        print('SMA exit')
                if not exit_position:
                    entry = self.signals.loc[self.signals['date'] >= self.entry_time]
                    # if entry['close'][0] < signal['trailing_stop'][0] and signal['adx'][0] > 10:
                    if signal['close'][0] < entry['trailing_stop'].max() and signal['adx'][0] > 10:
                        exit_position = True
                        print('Trailing exit - ' + str(signal['adx'][0]))


            # Trading signals based on moving average cross
            if signal['buy'][0] == 1 and not self.invested:
                print("LONG %s: %s" % (self.ticker, event.time))
                self.entry_time = signal['date'][0]
                signal_event = SignalEvent(
                    self.ticker,
                    "BOT",
                    suggested_quantity=self.base_quantity
                )
                self.events_queue.put(signal_event)
                self.invested = True

            elif (signal['sell'][0] == 1 or exit_position) and self.invested:
                print("SHORT %s: %s" % (self.ticker, event.time))
                signal_event = SignalEvent(
                    self.ticker,
                    "SLD",
                    suggested_quantity=self.base_quantity
                )
                self.events_queue.put(signal_event)
                self.invested = False

    def expired_not_profit(self):
        past = self.signals[self.signals['date'] > self.entry_time]
        if not past.empty:
            went_up = past[past['close'] > past['bb_middleband']]
            if len(went_up) < 1 and len(past) > 25:
                exit_position = True
                print('Exit position')
        return exit_position


def run(config, testing, tickers, filename):
    # Backtest information
    title = ['BB strategy']
    initial_equity = 10000.0
    start_date = datetime.datetime(2000, 1, 1)
    end_date = datetime.datetime(2014, 1, 1)

    # Use the MAC Strategy
    events_queue = queue.Queue()
    strategy = MovingAverageCrossStrategy(
        tickers[0], events_queue,
        short_window=100,
        long_window=300
    )

    # Set up the backtest
    backtest = TradingSession(
        config, strategy, tickers,
        initial_equity, start_date, end_date,
        events_queue, title=title,
        benchmark=tickers[0],
    )
    results = backtest.start_trading(testing=testing)
    return results


if __name__ == "__main__":
    # Configuration data
    testing = False
    config = settings.from_file(
        settings.DEFAULT_CONFIG_FILENAME, testing
    )
    tickers = ["AAPL", "SPY"]
    filename = None
    run(config, testing, tickers, filename)
