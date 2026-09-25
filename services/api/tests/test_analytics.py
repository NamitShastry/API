"""Unit tests for Tier 4 quantitative models and algorithms."""

import unittest
from app.analytics.advanced import AdvancedAnalyticsEngine


class TestAdvancedAnalytics(unittest.TestCase):
    def test_stl_anomaly_detection(self):
        # Create 28 days of series with one obvious spike
        series = [100.0 + (i % 7) * 2.0 for i in range(28)]
        series[14] += 25.0  # Big anomaly spike on day 14

        anomalies = AdvancedAnalyticsEngine.detect_anomalies_stl(series, seasonal_period=7, threshold_sigma=2.5)
        self.assertTrue(len(anomalies) > 0)
        self.assertEqual(anomalies[0]["index_point"], 14)

    def test_cross_carrier_agreement(self):
        # Tight parity test
        fares_tight = {"6E": 5000.0, "AI": 5050.0, "QP": 4980.0}
        res_tight = AdvancedAnalyticsEngine.calculate_cross_carrier_agreement(fares_tight)
        self.assertEqual(res_tight["clustering_category"], "TIGHT_PARITY")

        # Wide dispersion test
        fares_wide = {"6E": 4500.0, "AI": 7200.0, "SG": 3800.0}
        res_wide = AdvancedAnalyticsEngine.calculate_cross_carrier_agreement(fares_wide)
        self.assertEqual(res_wide["clustering_category"], "HIGH_COMPETITION")

    def test_policy_savings_simulator(self):
        res = AdvancedAnalyticsEngine.simulate_policy_savings(
            annual_air_spend_inr=10000000.0,  # 1 Crore INR
            current_l01_l03_share=0.40,
            target_l01_l03_share=0.10,
        )
        self.assertGreater(res.total_savings_inr, 0.0)
        self.assertGreater(res.savings_percentage, 5.0)

    def test_nowcast_forecast_ci_bounds(self):
        projections = AdvancedAnalyticsEngine.generate_nowcast_forecast(114.5, horizon_days=7)
        self.assertEqual(len(projections), 7)
        for p in projections:
            self.assertLess(p["lower_ci_95"], p["predicted_index"])
            self.assertGreater(p["upper_ci_95"], p["predicted_index"])


if __name__ == "__main__":
    unittest.main()
