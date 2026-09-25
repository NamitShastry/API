"""Jevons elementary price index calculator and geometric aggregations."""

from __future__ import annotations

import math
from typing import Sequence


class JevonsCalculator:
    """Mathematical implementation of the Jevons elementary index.

    The Jevons index satisfies transitivity and time-reversal tests, avoiding
    the upward substitution bias inherent in arithmetic formulas (Dutot / Carli).
    """

    @staticmethod
    def geometric_mean(prices: Sequence[float]) -> float:
        """Compute geometric mean: exp( (1/n) * sum(ln(p_i)) )."""
        if not prices:
            return 0.0
        # Filter out zero or negative values
        valid_prices = [p for p in prices if p > 0]
        if not valid_prices:
            return 0.0

        log_sum = sum(math.log(p) for p in valid_prices)
        return math.exp(log_sum / len(valid_prices))

    @classmethod
    def compute_elementary_cell_index(
        cls,
        current_prices: Sequence[float],
        base_price: float,
    ) -> tuple[float, float]:
        """Calculate cell index value relative to base period: (geom_mean / base_price) * 100.

        Returns (cell_index_value, current_geometric_mean).
        """
        if not current_prices or base_price <= 0:
            return 100.0, base_price

        current_geom = cls.geometric_mean(current_prices)
        cell_index = (current_geom / base_price) * 100.0
        return round(cell_index, 2), round(current_geom, 2)

    @staticmethod
    def aggregate_basket_index(
        cell_indexes: dict[tuple[str, str], float],  # (route_id, bucket_id) -> cell_index
        route_weights: dict[str, float],             # route_id -> DGCA weight (sum = 1.0)
        bucket_weights: dict[str, float],            # bucket_id -> lead weight (sum = 1.0)
        min_coverage_pct: float = 80.0,
    ) -> tuple[float, float]:
        """Weighted two-tier aggregation of elementary cell indexes to the National Composite Index.

        Returns (composite_index_value, coverage_pct).
        """
        covered_weight = 0.0
        total_weighted_index = 0.0

        for (route_id, bucket_id), cell_idx in cell_indexes.items():
            r_wt = route_weights.get(route_id, 0.0)
            b_wt = bucket_weights.get(bucket_id, 0.0)
            joint_wt = r_wt * b_wt

            if joint_wt > 0:
                total_weighted_index += joint_wt * cell_idx
                covered_weight += joint_wt

        coverage_pct = round(covered_weight * 100.0, 1)

        # Normalize by covered weight if coverage exceeds threshold
        if covered_weight >= (min_coverage_pct / 100.0) and covered_weight > 0:
            normalized_index = total_weighted_index / covered_weight
            return round(normalized_index, 2), coverage_pct
        elif covered_weight > 0:
            # Low coverage: imputed estimate
            normalized_index = total_weighted_index / covered_weight
            return round(normalized_index, 2), coverage_pct
        else:
            return 100.0, 0.0
