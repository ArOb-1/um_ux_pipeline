import pandas as pd

from app.domain.validators import UMUXValidator


class TestUMUXValidator:
    """Тесты валидатора"""

    def test_valid_data(self):
        validator = UMUXValidator()
        df = pd.DataFrame({
            'response_id': ['1', '2'],
            'submitted_at': ['2024-01-01 10:00:00', '2024-01-02 11:00:00'],
            'product': ['Product A', 'Product B'],
            'product_version': ['1.0.0', '2.0.0'],
            'platform': ['Web', 'Android'],
            'score1': [5, 4],
            'score2': [4, 3]
        })
        valid, invalid = validator.validate(df)
        assert len(valid) == 2
        assert len(invalid) == 0

    def test_invalid_score(self):
        validator = UMUXValidator()
        df = pd.DataFrame({
            'response_id': ['1', '2'],
            'submitted_at': ['2024-01-01 10:00:00', '2024-01-02 11:00:00'],
            'product': ['Product A', 'Product B'],
            'product_version': ['1.0.0', '2.0.0'],
            'platform': ['Web', 'Android'],
            'score1': [6, 4],
            'score2': [4, 0]
        })
        valid, invalid = validator.validate(df)
        assert len(valid) == 0
        assert len(invalid) == 2

    def test_duplicate_response_id(self):
        validator = UMUXValidator()
        df = pd.DataFrame({
            'response_id': ['1', '1', '2'],
            'submitted_at': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'product': ['A', 'B', 'C'],
            'product_version': ['1.0', '2.0', '3.0'],
            'platform': ['Web', 'Android', 'iOS'],
            'score1': [5, 4, 3],
            'score2': [4, 3, 2]
        })
        valid, invalid = validator.validate(df)
        assert len(valid) == 2
        assert len(invalid) == 1

    def test_invalid_platform(self):
        validator = UMUXValidator()
        df = pd.DataFrame({
            'response_id': ['1'],
            'submitted_at': ['2024-01-01 10:00:00'],
            'product': ['Product A'],
            'product_version': ['1.0.0'],
            'platform': ['Windows'],
            'score1': [5],
            'score2': [4]
        })
        valid, invalid = validator.validate(df)
        assert len(valid) == 0
        assert len(invalid) == 1
        assert 'invalid_platform' in invalid['rejection_reason'].values[0]
