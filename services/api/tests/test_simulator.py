"""Unit tests for Calibrated Airfare Simulator."""

import asyncio
import datetime
import unittest
from app.collector.simulator import CalibratedSimulatorAdapter


class TestSimulator(unittest.TestCase):
    def setUp(self):
        self.sim = CalibratedSimulatorAdapter(seed=20260922)

    def test_reproducibility(self):
        """Verify that identical seeds produce identical deterministic fares."""
        sim1 = CalibratedSimulatorAdapter(seed=42)
        sim2 = CalibratedSimulatorAdapter(seed=42)

        dep_d = datetime.date(2026, 10, 15)
        f1, _, _, _ = sim1.calculate_deterministic_fare("DEL-BOM", "L14", dep_d, "6E")
        f2, _, _, _ = sim2.calculate_deterministic_fare("DEL-BOM", "L14", dep_d, "6E")

        self.assertEqual(f1, f2)

    def test_lead_elasticity_monotonicity(self):
        """Verify that last-minute L01 fares are significantly higher than planned L14/L60 fares."""
        dep_d = datetime.date(2026, 11, 20)
        f_l01, _, _, _ = self.sim.calculate_deterministic_fare("DEL-BLR", "L01", dep_d, "6E")
        f_l14, _, _, _ = self.sim.calculate_deterministic_fare("DEL-BLR", "L14", dep_d, "6E")
        f_l60, _, _, _ = self.sim.calculate_deterministic_fare("DEL-BLR", "L60", dep_d, "6E")

        self.assertGreater(f_l01, f_l14)
        self.assertGreater(f_l14, f_l60)

    def test_defect_injection(self):
        """Verify that defect injector tags defects appropriately."""
        dep_d = datetime.date(2026, 10, 15)
        fare, tax, has_defect, reason = self.sim.calculate_deterministic_fare(
            "DEL-BOM", "L14", dep_d, "6E", inject_defect=True
        )
        self.assertTrue(has_defect)
        self.assertIsNotNone(reason)


if __name__ == "__main__":
    unittest.main()
