"""Unit tests for Cleaning Pipeline rules R01-R12 and deduplication."""

import datetime
import unittest
from app.collector.base import ObservedQuote
from app.pipeline.cleaner import CleaningPipeline


class TestCleaningPipeline(unittest.TestCase):
    def setUp(self):
        CleaningPipeline._SEEN_HASHES.clear()
        self.now = datetime.datetime.now(datetime.timezone.utc)
        self.future_dep = self.now + datetime.timedelta(days=7)

    def test_r01_minimum_fare_floor(self):
        """Test that fares below 1,200 INR are quarantined."""
        quote = ObservedQuote(
            source_id="SIMULATOR",
            route_id="DEL-BOM",
            airline_code="6E",
            flight_number="6E-204",
            departure_datetime=self.future_dep,
            arrival_datetime=self.future_dep + datetime.timedelta(hours=2),
            fare_amount=850.0,  # Below 1,200 INR
            currency="INR",
            tax_amount=100.0,
            fare_class="ECONOMY",
            is_direct=True,
            observed_at=self.now,
        )
        res = CleaningPipeline.clean_quote(quote)
        self.assertTrue(res.is_quarantined)
        self.assertFalse(res.is_valid)
        self.assertTrue(any(i["rule"] == "R01_MIN_FARE" for i in res.dq_issues))

    def test_r02_maximum_fare_ceiling(self):
        """Test that fares above 65,000 INR are quarantined."""
        quote = ObservedQuote(
            source_id="SIMULATOR",
            route_id="DEL-BOM",
            airline_code="6E",
            flight_number="6E-204",
            departure_datetime=self.future_dep,
            arrival_datetime=self.future_dep + datetime.timedelta(hours=2),
            fare_amount=78000.0,  # Above 65,000 INR
            currency="INR",
            tax_amount=5000.0,
            fare_class="ECONOMY",
            is_direct=True,
            observed_at=self.now,
        )
        res = CleaningPipeline.clean_quote(quote)
        self.assertTrue(res.is_quarantined)
        self.assertFalse(res.is_valid)
        self.assertTrue(any(i["rule"] == "R02_MAX_FARE" for i in res.dq_issues))

    def test_r06_deduplication(self):
        """Test that duplicate quote signatures are rejected."""
        quote = ObservedQuote(
            source_id="SIMULATOR",
            route_id="DEL-BLR",
            airline_code="AI",
            flight_number="AI-502",
            departure_datetime=self.future_dep,
            arrival_datetime=self.future_dep + datetime.timedelta(hours=2, minutes=30),
            fare_amount=5400.0,
            currency="INR",
            tax_amount=600.0,
            fare_class="ECONOMY",
            is_direct=True,
            observed_at=self.now,
        )
        first_res = CleaningPipeline.clean_quote(quote)
        self.assertTrue(first_res.is_valid)

        second_res = CleaningPipeline.clean_quote(quote)
        self.assertFalse(second_res.is_valid)
        self.assertTrue(any(i["rule"] == "R06_DEDUPLICATION" for i in second_res.dq_issues))

    def test_r07_mad_outlier_detection(self):
        """Test modified Z-score outlier flagging."""
        quote = ObservedQuote(
            source_id="SIMULATOR",
            route_id="DEL-BOM",
            airline_code="SG",
            flight_number="SG-101",
            departure_datetime=self.future_dep,
            arrival_datetime=self.future_dep + datetime.timedelta(hours=2),
            fare_amount=24000.0,
            currency="INR",
            tax_amount=2000.0,
            fare_class="ECONOMY",
            is_direct=True,
            observed_at=self.now,
        )
        # Median = 4800, MAD = 800 -> mod Z = 0.6745 * (24000 - 4800) / 800 = 16.18 > 3.5
        res = CleaningPipeline.clean_quote(quote, cell_median=4800.0, cell_mad=800.0)
        self.assertTrue(res.is_outlier)
        self.assertTrue(any(i["rule"] == "R07_MAD_OUTLIER" for i in res.dq_issues))


if __name__ == "__main__":
    unittest.main()
