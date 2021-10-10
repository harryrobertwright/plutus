import unittest

from mock import patch

from plutus import Pair
from tests.constants import RESPONSE


class TestPair(unittest.TestCase):
    def setUp(self):
        self.response = RESPONSE

        self.patcher = patch("plutus.Client")
        mock_client = self.patcher.start()
        mock_client.get_historical_klines.return_value = self.response
        self.pair = Pair("BTCUSDT", "October 8, 2021", mock_client)
        self.interval = "1h"

    def test_get_candle_returns_expected_candle(self):
        self.assertEqual(self.pair.get_candle(self.interval, 0), self.response[-1])

    def test_get_candle_returns_none_given_invalid_index(self):
        self.assertIsNone(self.pair.get_candle(self.interval, 10000))

    def test_is_candle_bullish_returns_true_given_bullish_candle(self):
        self.assertTrue(self.pair.is_candle_bullish(self.interval, 2))

    def test_is_candle_bullish_returns_false_given_bearish_candle(self):
        self.assertFalse(self.pair.is_candle_bullish(self.interval, 0))

    def test_is_candle_bearish_returns_true_given_bearish_candle(self):
        self.assertTrue(self.pair.is_candle_bearish(self.interval, 0))

    def test_is_candle_bearish_returns_false_given_bullish_candle(self):
        self.assertFalse(self.pair.is_candle_bearish(self.interval, 2))

    def test_get_highest_high_returns_highest_candle(self):
        self.assertEqual(self.pair.get_highest_high(self.interval), 1)

    def test_get_highest_high_returns_highest_candle_given_valid_start_index(self):
        self.assertEqual(self.pair.get_highest_high(self.interval, 10), 61)

    def test_get_highest_high_returns_highest_candle_given_valid_count(self):
        self.assertEqual(self.pair.get_highest_high(self.interval, 0, 3), 1)

    def test_get_highest_high_returns_none_given_invalid_start_index(self):
        self.assertIsNone(self.pair.get_highest_high(self.interval, 10000))

    def test_get_highest_high_returns_none_given_invalid_count(self):
        self.assertIsNone(self.pair.get_highest_high(self.interval, count=10000))

    def test_get_lowest_low_returns_lowest_candle(self):
        self.assertEqual(self.pair.get_lowest_low(self.interval), 235)

    def test_get_lowest_low_returns_lowest_candle_given_valid_start_index(self):
        self.assertEqual(self.pair.get_lowest_low(self.interval, 20), 235)

    def test_get_lowest_low_returns_low_candle_given_valid_count(self):
        self.assertEqual(self.pair.get_lowest_low(self.interval, 0, 3), 0)

    def test_get_lowest_low_returns_none_given_invalid_start_index(self):
        self.assertIsNone(self.pair.get_lowest_low(self.interval, 10000))

    def test_get_lowest_low_returns_none_given_invalid_count(self):
        self.assertIsNone(self.pair.get_lowest_low(self.interval, count=10000))

    def test_is_up_fractal_returns_true_given_fractal(self):
        self.assertTrue(self.pair.is_up_fractal(self.interval, 19, count=3))

    def test_is_up_fractal_returns_false_given_non_fractal(self):
        self.assertFalse(self.pair.is_up_fractal(self.interval, 20, count=3))

    def test_is_down_fractal_returns_true_given_fractal(self):
        self.assertTrue(self.pair.is_down_fractal(self.interval, 16, count=3))

    def test_is_down_fractal_returns_false_given_non_fractal(self):
        self.assertFalse(self.pair.is_down_fractal(self.interval, 18, count=3))

    def tearDown(self):
        self.patcher.stop()


if __name__ == "__main__":
    unittest.main()
