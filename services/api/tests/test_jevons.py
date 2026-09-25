"""Unit tests for Jevons elementary price index and geometric aggregation."""

import math
import unittest
from app.engine.jevons import JevonsCalculator


class TestJevonsCalculator(unittest.TestCase):
    def test_geometric_mean_basic(self):
        prices = [100.0, 400.0]
        # sqrt(100 * 400) = sqrt(40000) = 200.0
        gm = JevonsCalculator.geometric_mean(prices)
        self.assertAlmostEqual(gm, 200.0, places=4)

    def test_geometric_mean_empty_or_zeros(self):
        self.assertEqual(JevonsCalculator.geometric_mean([]), 0.0)
        self.assertEqual(JevonsCalculator.geometric_mean([-50.0, 0.0]), 0.0)

    def test_time_reversal_property(self):
        """Verify axiomatic index requirement: I(0, t) * I(t, 0) == 1."""
        base_prices = [4000.0, 5000.0, 6000.0]
        current_prices = [4800.0, 5500.0, 6300.0]

        gm_base = JevonsCalculator.geometric_mean(base_prices)
        gm_curr = JevonsCalculator.geometric_mean(current_prices)

        i_0_t = gm_curr / gm_base
        i_t_0 = gm_base / gm_curr

        self.assertAlmostEqual(i_0_t * i_t_0, 1.0, places=6)

    def test_elementary_cell_index(self):
        prices = [4200.0, 4500.0, 4800.0]
        base_price = 4500.0
        idx_val, geom = JevonsCalculator.compute_elementary_cell_index(prices, base_price)

        self.assertGreater(idx_val, 95.0)
        self.assertLess(idx_val, 105.0)
        self.assertAlmostEqual(geom, JevonsCalculator.geometric_mean(prices), places=2)

    def test_basket_aggregation_coverage_guard(self):
        cell_indexes = {
            ("DEL-BOM", "L14"): 110.0,
            ("DEL-BLR", "L14"): 120.0,
        }
        route_weights = {"DEL-BOM": 0.5, "DEL-BLR": 0.5}
        bucket_weights = {"L14": 1.0}

        idx, coverage = JevonsCalculator.aggregate_basket_index(
            cell_indexes, route_weights, bucket_weights, min_coverage_pct=80.0
        )
        self.assertEqual(coverage, 100.0)
        self.assertEqual(idx, 115.0)

    def test_low_coverage_guard(self):
        cell_indexes = {("DEL-BOM", "L14"): 110.0}
        route_weights = {"DEL-BOM": 0.3}  # Only 30% coverage (< 80%)
        bucket_weights = {"L14": 1.0}

        idx, coverage = JevonsCalculator.aggregate_basket_index(
            cell_indexes, route_weights, bucket_weights, min_coverage_pct=80.0
        )
        self.assertEqual(coverage, 30.0)
        self.assertEqual(idx, 110.0)


if __name__ == "__main__":
    unittest.main()
