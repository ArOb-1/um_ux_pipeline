import pandas as pd

from app.domain.calculators import UMUXCalculator


class TestUMUXCalculator:
    """Тесты калькулятора UMUX"""

    def test_calculate_umux(self):
        calculator = UMUXCalculator()
        df = pd.DataFrame({
            'score1': [5, 4, 3, 2, 1],
            'score2': [5, 4, 3, 2, 1]
        })
        result = calculator.calculate(df)
        assert result['umux_score'].tolist() == [100.0, 80.0, 60.0, 40.0, 20.0]

    def test_calculate_umux_category(self):
        calculator = UMUXCalculator()
        df = pd.DataFrame({
            'score1': [5, 4, 3, 2, 1],
            'score2': [5, 4, 3, 2, 1]
        })
        result = calculator.calculate(df)
        expected = ['excellent', 'excellent', 'acceptable', 'poor', 'poor']
        assert result['umux_category'].tolist() == expected

    def test_empty_dataframe(self):
        calculator = UMUXCalculator()
        df = pd.DataFrame()
        result = calculator.calculate(df)
        assert result.empty
