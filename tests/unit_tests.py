import unittest

from mock import patch

from plutus import Pair


class TestPair(unittest.TestCase):
    def setUp(self):
        self.response = [
            [
                1633651200000,
                "53785.22000000",
                "54235.99000000",
                "53711.57000000",
                "54108.00000000",
                "1319.71058000",
                1633654799999,
                "71264674.76186690",
                43155,
                "683.00199000",
                "36883209.50240990",
                "0",
            ],
            [
                1633654800000,
                "54108.01000000",
                "54397.00000000",
                "54051.10000000",
                "54297.35000000",
                "1107.57340000",
                1633658399999,
                "60070447.19251220",
                37661,
                "541.42529000",
                "29367797.76780600",
                "0",
            ],
            [
                1633658400000,
                "54297.35000000",
                "54429.99000000",
                "53776.50000000",
                "53842.00000000",
                "1547.30709000",
                1633661999999,
                "83608849.89852760",
                47630,
                "716.12060000",
                "38700173.38302440",
                "0",
            ],
            [
                1633662000000,
                "53842.01000000",
                "53940.00000000",
                "53691.02000000",
                "53815.22000000",
                "1401.24886000",
                1633665599999,
                "75387268.39814890",
                39458,
                "594.29804000",
                "31973546.33675350",
                "0",
            ],
        ]

        self.patcher = patch("plutus.Client")
        mock_client = self.patcher.start()
        mock_client.get_historical_klines.return_value = self.response
        self.pair = Pair("BTCUSDT", "October 8, 2021", mock_client)
        self.interval = "1h"

    def test_get_candle_returns_expected_candle(self):
        self.assertEqual(self.pair.get_candle(self.interval, 0), self.response[-1])

    def test_get_candle_returns_none_given_invalid_index(self):
        self.assertIsNone(self.pair.get_candle(self.interval, 100))

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
        self.assertEqual(self.pair.get_highest_high(self.interval, 2), 2)

    def test_get_highest_high_returns_highest_candle_given_valid_count(self):
        self.assertEqual(self.pair.get_highest_high(self.interval, 0, 3), 1)

    def test_get_highest_high_returns_none_given_invalid_start_index(self):
        self.assertIsNone(self.pair.get_highest_high(self.interval, 100))

    def test_get_highest_high_returns_none_given_invalid_count(self):
        self.assertIsNone(self.pair.get_highest_high(self.interval, count=100))

    def test_get_lowest_low_returns_lowest_candle(self):
        self.assertEqual(self.pair.get_lowest_low(self.interval), 0)

    def test_get_lowest_low_returns_lowest_candle_given_valid_start_index(self):
        self.assertEqual(self.pair.get_lowest_low(self.interval, 2), 3)

    def test_get_lowest_low_returns_low_candle_given_valid_count(self):
        self.assertEqual(self.pair.get_lowest_low(self.interval, 0, 3), 0)

    def test_get_lowest_low_returns_none_given_invalid_start_index(self):
        self.assertIsNone(self.pair.get_lowest_low(self.interval, 100))

    def test_get_lowest_low_returns_none_given_invalid_count(self):
        self.assertIsNone(self.pair.get_lowest_low(self.interval, count=100))

    def tearDown(self):
        self.patcher.stop()


if __name__ == "__main__":
    unittest.main()
