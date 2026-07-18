import pandas as pd
from typing import Dict, Any, List, Optional

from ..core.interfaces import IAggregator


class UMUXAggregator(IAggregator):
    """
    Агрегатор UMUX данных

    Группирует и считает статистики по:
    - Продуктам
    - Версиям продуктов
    - Платформам
    - Месяцам
    """

    def __init__(self):
        self._available_dimensions = ['product',
                                      'product_version',
                                      'platform',
                                      'month']

    def aggregate(self,
                  df: pd.DataFrame,
                  dimensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Агрегация данных по измерениям
        """
        if df.empty or 'umux_score' not in df.columns:
            return self._empty_result()

        if dimensions is None:
            dimensions = self._available_dimensions

        dims = [d for d in dimensions if d in df.columns]

        result = {
            'overall': self._calculate_overall(df),
        }

        if 'product' in dims:
            result['by_product'] = self._group_by_dimension(df, 'product')

        if 'product' in dims and 'product_version' in dims:
            result['by_product_version'] = self._group_by_product_version(df)

        if 'month' in dims:
            result['by_month'] = self._group_by_dimension(df, 'month')

        if 'platform' in dims:
            result['by_platform'] = self._group_by_dimension(df, 'platform')

        return result

    def _calculate_overall(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Общая статистика"""
        scores = df['umux_score'].dropna()

        if len(scores) == 0:
            return {
                'total_responses': 0,
                'avg_umux': 0,
                'std_umux': 0,
                'min_umux': 0,
                'max_umux': 0,
                'median_umux': 0
            }

        return {
            'total_responses': len(df),
            'avg_umux': float(scores.mean()),
            'std_umux': float(scores.std()),
            'min_umux': float(scores.min()),
            'max_umux': float(scores.max()),
            'median_umux': float(scores.median())
        }

    def _group_by_dimension(self,
                            df: pd.DataFrame,
                            dimension: str) -> List[Dict[str, Any]]:
        """Группировка по одному измерению"""
        agg = df.groupby(dimension).agg({
            'umux_score': ['mean', 'std', 'count', 'min', 'max']
        }).round(2)

        agg.columns = ['avg_umux', 'std_umux', 'count', 'min_umux', 'max_umux']
        agg = agg.reset_index()

        total_count = agg['count'].sum()
        if total_count > 0:
            agg['percentage'] = (agg['count'] / total_count * 100).round(1)
        else:
            agg['percentage'] = 0

        if dimension == 'month':
            agg = agg.sort_values('month', ascending=True)
        else:
            agg = agg.sort_values('avg_umux', ascending=False)

        return agg.to_dict('records')

    def _group_by_product_version(self,
                                  df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Группировка по продукту и версии"""
        agg = df.groupby(['product', 'product_version']).agg({
            'umux_score': ['mean', 'count']
        }).round(2)

        agg.columns = ['avg_umux', 'count']
        agg = agg.reset_index()
        agg = agg.sort_values(['product', 'product_version'])

        return agg.to_dict('records')

    def get_available_dimensions(self) -> List[str]:
        return self._available_dimensions.copy()

    def _empty_result(self) -> Dict[str, Any]:
        return {
            'overall': {
                'total_responses': 0,
                'avg_umux': 0,
                'std_umux': 0,
                'min_umux': 0,
                'max_umux': 0,
                'median_umux': 0
            },
            'by_product': [],
            'by_product_version': [],
            'by_month': [],
            'by_platform': []
        }
