import pandas as pd

from app.domain.aggregators import UMUXAggregator


class TestAggregator:
    """Тесты агрегатора"""

    def test_aggregate_valid_data(self):
        aggregator = UMUXAggregator()
        df = pd.DataFrame({
            'product': ['A', 'A', 'B', 'B', 'C'],
            'product_version': ['1.0', '1.0', '2.0', '2.0', '3.0'],
            'umux_score': [80, 90, 70, 60, 100],
            'month': ['2024-01', '2024-01', '2024-02', '2024-02', '2024-03'],
            'platform': ['web', 'android', 'web', 'ios', 'web']
        })
        result = aggregator.aggregate(df)
        assert result['overall']['total_responses'] == 5
        assert result['overall']['avg_umux'] == 80.0
        assert len(result['by_product']) == 3
        assert len(result['by_month']) == 3
