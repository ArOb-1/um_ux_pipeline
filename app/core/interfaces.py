"""
Абстрактные интерфейсы для всех компонентов системы
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from .models import PipelineResult, AggregationResult


class IDataLoader(ABC):
    """Интерфейс загрузчика данных"""

    @abstractmethod
    def load(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Загружает данные из файла
        Args:
            file_path: путь к файлу
        Returns:
            DataFrame с данными или None при ошибке
        """
        pass

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """
        Проверяет, поддерживается ли тип файла

        Args:
            file_path: путь к файлу

        Returns:
            True если поддерживается
        """
        pass


class IValidator(ABC):
    """Интерфейс валидатора данных"""

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Валидация данных

        Args:
            df: входной DataFrame

        Returns:
            (валидные данные, невалидные данные)
        """
        pass

    @abstractmethod
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Нормализация данных

        Args:
            df: входной DataFrame

        Returns:
            Нормализованный DataFrame
        """
        pass

    @abstractmethod
    def get_rejection_stats(self) -> Dict[str, int]:
        """
        Получает статистику отбраковки

        Returns:
            Словарь {причина: количество}
        """
        pass


class ICalculator(ABC):
    """Интерфейс калькулятора метрик"""

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Расчет метрик для датафрейма

        Args:
            df: входной DataFrame

        Returns:
            DataFrame с добавленными метриками
        """
        pass

    @abstractmethod
    def get_metric_name(self) -> str:
        """
        Название метрики

        Returns:
            Строка с названием метрики
        """
        pass


class IAggregator(ABC):
    """Интерфейс агрегатора данных"""

    @abstractmethod
    def aggregate(self, df: pd.DataFrame, dimensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Агрегация данных по измерениям

        Args:
            df: входной DataFrame
            dimensions: список измерений для агрегации

        Returns:
            Словарь с агрегированными данными
        """
        pass

    @abstractmethod
    def get_available_dimensions(self) -> List[str]:
        """
        Доступные измерения для агрегации

        Returns:
            Список названий измерений
        """
        pass


class IRepository(ABC):
    """Интерфейс репозитория для работы с данными"""

    @abstractmethod
    def save_valid(self, df: pd.DataFrame) -> int:
        """
        Сохраняет валидные записи

        Args:
            df: DataFrame с валидными данными

        Returns:
            Количество сохраненных записей
        """
        pass

    @abstractmethod
    def save_rejected(self, df: pd.DataFrame) -> int:
        """
        Сохраняет отбракованные записи

        Args:
            df: DataFrame с невалидными данными

        Returns:
            Количество сохраненных записей
        """
        pass

    @abstractmethod
    def get_aggregations(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Получает агрегированные данные из БД

        Args:
            filters: фильтры для данных

        Returns:
            Словарь с агрегированными данными
        """
        pass

    @abstractmethod
    def get_rejection_stats(self) -> Dict[str, int]:
        """
        Получает статистику отбраковки из БД

        Returns:
            Словарь {причина: количество}
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Очищает все данные в репозитории"""
        pass


class IVisualizer(ABC):
    """Интерфейс визуализатора"""

    @abstractmethod
    def create_dashboard(self, df: pd.DataFrame, aggregations: Dict[str, Any]) -> Dict[str, str]:
        """
        Создает дашборд с графиками

        Args:
            df: данные для визуализации
            aggregations: агрегированные данные

        Returns:
            Словарь {название_графика: base64_строка}
        """
        pass

    @abstractmethod
    def save_dashboard(self, visualizations: Dict[str, str], filename: str) -> None:
        """
        Сохраняет дашборд в файл

        Args:
            visualizations: словарь с визуализациями
            filename: имя файла для сохранения
        """
        pass


class IPipeline(ABC):
    """Интерфейс пайплайна обработки данных"""

    @abstractmethod
    def process(self, file_paths: List[str]) -> PipelineResult:
        """
        Запускает обработку данных

        Args:
            file_paths: список путей к файлам

        Returns:
            Результат работы пайплайна
        """
        pass

    @abstractmethod
    def process_dataframe(self, df: pd.DataFrame) -> PipelineResult:
        """
        Обрабатывает DataFrame

        Args:
            df: данные для обработки

        Returns:
            Результат работы пайплайна
        """
        pass
