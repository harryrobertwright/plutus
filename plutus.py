from decimal import Decimal
from typing import Union

from binance import Client
from tqdm import tqdm

from constants import INTERVALS


class Pair:
    """A class representing a currency pair.

    Represents a Binance currency pair and acts as a wrapper for its data.
    Binance's historical kline data is loaded and is consumed by methods
    that seek to provide functionality for technical analysis and
    algorithmic trading.


    Attributes:
        ticker: A string representing the name of symbol pair.
        start: A string representing the date from the data should be fetched.
        client: An instance of a Binance Client used to interact with
        Binance's API.
        data: A dictionary containing the data for the given pair.
    """

    def __init__(self, ticker: str, start: str, client: Client):
        self._data = None
        self.ticker = ticker
        self.start = start
        self.client = client

    @property
    def data(self):
        if not self._data:
            self._data = {
                interval: list(
                    reversed(
                        self.client.get_historical_klines(
                            self.ticker, interval, self.start
                        )
                    )
                )
                for interval in tqdm(
                    INTERVALS, desc=f"Loading historical data for {self.ticker}"
                )
            }
        return self._data

    def _get_interval_data(self, interval):
        return self.data.get(interval, [])

    def get_candle(self, interval: str, index: int) -> Union[list, None]:
        """Retrieves a candle.

        Retrieves a candle for a given currency pair and interval.

        Args:
            interval: A Binance Kline interval.
            index: A number that represents the index of the candle to be
            checked.

        Returns:
            A list containing the OHLCV values for candle. IF the candle
            cannot be located, then None is returned.
        """
        data: list = self._get_interval_data(interval)
        try:
            candle = data[index]
        except IndexError:
            return None
        else:
            return candle

    def is_candle_bullish(self, interval: str, index: int) -> Union[bool, None]:
        """Checks whether a candle is bullish.

        Checks to see if the closing price of a candle is greater than the
        opening price of the same candle. If so, the candle is 'bullish'.

        Args:
            interval: A Binance Kline interval.
            index: A number that represents the index of the candle to be checked.

        Returns:
            A bool. True is returned if the candle is bullish, otherwise False is
            returned.
        """
        candle: Union[list, None] = self.get_candle(interval, index)

        if candle:
            return Decimal(candle[4]) > Decimal(candle[1])

        return None

    def is_candle_bearish(self, interval: str, index: int) -> Union[bool, None]:
        """Checks whether a candle is bearish.

        Checks to see if the closing of a candle is less than the opening price
        of the same candle. If so, the candle is 'bullish'.

        Args:
            interval: A Binance Kline interval.
            index: A number that represents the index of the candle to be checked.

        Returns:
            A boolean value set to True if the candle is bearish, otherwise False.
        """
        candle: Union[list, None] = self.get_candle(interval, index)

        if candle:
            return Decimal(candle[4]) < Decimal(candle[1])

        return None

    def get_highest_high(
        self,
        interval: str,
        start_index: Union[int, None] = None,
        count: Union[int, None] = None,
    ) -> Union[int, None]:
        """Gets highest high for a pair.

        Obtains the highest high price of a given currency pair and interval, and
        can be further filtered by starting index and count.

        Args:
            interval: A Binance Kline interval.
            start_index: A number that represents the index of the candle from which
            the search should start.
            count: A number of candles (in order of the start to the back one) that
            are searched.

        Returns:
            A number representing the index of the highest candle. If no data given
            the parameters if found, None is returned.
        """
        data: list = self._get_interval_data(interval)
        highs: list = [Decimal(datum[2]) for datum in data]

        if not start_index:
            start_index = 0

        if not count:
            count = len(data)

        if count > len(data):
            return None

        try:
            filtered_data = data[start_index : start_index + count]
        except IndexError:
            return None
        else:
            filtered_highs: list = [Decimal(datum[2]) for datum in filtered_data]

        if filtered_highs:
            return highs.index(max(filtered_highs))

        return None

    def get_lowest_low(
        self, interval: str, start_index: int = 0, count: Union[int, None] = None
    ) -> Union[int, None]:
        """Gets lowest low for a pair.

        Obtains the lowest low price of a given currency pair and interval, and
        can be further filtered by starting index and count.

        Args:
            interval: A Binance Kline interval.
            start_index: A number that represents the index of the candle from which
            the search should start.
            count: A number of candles (in order of the start to the back one) that
            are searched.

        Returns:
            A number representing the index of the lowest candle. If no data given
            the parameters if found, None is returned.
        """
        data: list = self._get_interval_data(interval)
        lows: list = [Decimal(datum[3]) for datum in data]

        if not start_index:
            start_index = 0

        if not count:
            count = len(data)

        if count > len(data):
            return None

        try:
            filtered_data = data[start_index : start_index + count]
        except IndexError:
            return None
        else:
            filtered_lows: list = [Decimal(datum[3]) for datum in filtered_data]

        if filtered_lows:
            return lows.index(min(filtered_lows))

        return None

    def is_up_fractal(
        self, interval: str, index: int, count: Union[int, None] = None
    ) -> Union[bool, None]:
        """Checks whether a candle is an up fractal.

        Checks to see if the low prices of a given candle's adjacent-left
        and adjacent-right neighbours are both greater than its own low
        price.

        Args:
            interval: A Binance Kline interval.
            index: A number that represents the index of the candle to be
            checked.
            count: A number of candles to be included in the fractal assement.
            This must be an even number and not be lower than three.

        Returns:
            A boolean value set to True if the candle is an up fractal,
            otherwise False. If any of the candles are unable to be found or
            an invalid count is given, it returns None.
        """
        candle: Union[list, None] = self.get_candle(interval, index)

        if not count:
            count = 3

        if count < 3 or (count % 2) == 0:
            return None

        candles_each_side_to_check = int((count - 1) / 2)

        for offset in range(1, candles_each_side_to_check + 1):
            adjacent_left: Union[list, None] = self.get_candle(interval, index + offset)
            adjacent_right: Union[list, None] = self.get_candle(
                interval, index - offset
            )

            if candle and adjacent_left and adjacent_right:
                if Decimal(candle[3]) >= Decimal(adjacent_left[3]) or Decimal(
                    candle[3]
                ) >= Decimal(adjacent_right[3]):
                    return False
                continue

            return None

        return True

    def is_down_fractal(
        self, interval: str, index: int, count: Union[int, None] = None
    ) -> Union[bool, None]:
        """Checks whether a candle is an up fractal.

        Checks to see if the low prices of a given candle's adjacent-left
        and adjacent-right neighbours are both greater than its own low
        price.

        Args:
            interval: A Binance Kline interval.
            index: A number that represents the index of the candle to be
            checked.
            count: A number of candles to be included in the fractal assement.
            This must be an even number and not be lower than three.

        Returns:
            A boolean value set to True if the candle is an up fractal,
            otherwise False. If any of the candles are unable to be found or
            an invalid count is given, it returns None.
        """
        candle: Union[list, None] = self.get_candle(interval, index)

        if not count:
            count = 3

        if count < 3 or (count % 2) == 0:
            return None

        candles_each_side_to_check = int((count - 1) / 2)

        for offset in range(1, candles_each_side_to_check + 1):
            adjacent_left: Union[list, None] = self.get_candle(interval, index + offset)
            adjacent_right: Union[list, None] = self.get_candle(
                interval, index - offset
            )

            if candle and adjacent_left and adjacent_right:
                if Decimal(candle[2]) <= Decimal(adjacent_left[2]) or Decimal(
                    candle[2]
                ) <= Decimal(adjacent_right[2]):
                    return False
                continue

            return None

        return True
