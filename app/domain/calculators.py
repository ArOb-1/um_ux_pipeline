import pandas as pd
import logging
from typing import Dict, Any

from ..core.interfaces import ICalculator


logger = logging.getLogger(__name__)


class UMUXCalculator(ICalculator):
    """
    Калькулятор UMUX-Lite скора

    Формула: ((score1 + score2) / 10) * 100
    """

    def __init__(self, formula: str = 'standard'):
        self.formula = formula
        self.metric_name = 'umux_score'

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Расчет UMUX-скора"""
        if df.empty:
            return df

        df = df.copy()

        if self.formula == 'standard':
            df['umux_score'] = ((df['score1'] + df['score2']) / 10) * 100
        elif self.formula == 'sum':
            df['umux_score'] = df['score1'] + df['score2']
        else:
            logger.error(f'Неизвестная формула {self.formula}')
            raise ValueError(f"Unknown formula: {self.formula}")

        df['umux_category'] = df['umux_score'].apply(self._get_category)

        return df

    def _get_category(self, score: float) -> str:
        """Определяет категорию по UMUX скору"""
        if score >= 80:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 60:
            return 'acceptable'
        else:
            return 'poor'

    def get_metric_name(self) -> str:
        return self.metric_name

    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Дополнительная статистика по метрике"""
        if df.empty or self.metric_name not in df.columns:
            return {}

        scores = df[self.metric_name]

        return {
            'mean': float(scores.mean()),
            'median': float(scores.median()),
            'std': float(scores.std()),
            'min': float(scores.min()),
            'max': float(scores.max()),
            'q25': float(scores.quantile(0.25)),
            'q75': float(scores.quantile(0.75)),
            'categories': {
                'excellent': int((scores >= 80).sum()),
                'good': int(((scores >= 70) & (scores < 80)).sum()),
                'acceptable': int(((scores >= 60) & (scores < 70)).sum()),
                'poor': int((scores < 60).sum())
            }
        }
