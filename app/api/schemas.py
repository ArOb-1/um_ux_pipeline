"""
Pydantic схемы для API
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class UploadResponse(BaseModel):
    """Ответ на загрузку файлов"""
    status: str = Field(..., description="Статус операции")
    total_valid: int = Field(0, description="Количество валидных записей")
    total_rejected: int = Field(0, description="Количество отбракованных записей")
    rejection_stats: Dict[str, int] = Field(default_factory=dict, description="Статистика отбраковки")
    processing_time: float = Field(0.0, description="Время обработки в секундах")
    files_processed: List[str] = Field(default_factory=list, description="Обработанные файлы")


class OverallStats(BaseModel):
    """Общая статистика"""
    total_responses: int = Field(0, description="Всего ответов")
    avg_umux: float = Field(0.0, description="Средний UMUX")
    std_umux: float = Field(0.0, description="Стандартное отклонение")
    min_umux: float = Field(0.0, description="Минимальный UMUX")
    max_umux: float = Field(0.0, description="Максимальный UMUX")
    median_umux: float = Field(0.0, description="Медианный UMUX")


class ProductStats(BaseModel):
    """Статистика по продукту"""
    product: str = Field(..., description="Название продукта")
    avg_umux: float = Field(0.0, description="Средний UMUX")
    count: int = Field(0, description="Количество ответов")
    std_umux: Optional[float] = Field(0.0, description="Стандартное отклонение")


class ProductVersionStats(BaseModel):
    """Статистика по версии продукта"""
    product: str = Field(..., description="Название продукта")
    version: str = Field(..., description="Версия продукта")
    avg_umux: float = Field(0.0, description="Средний UMUX")
    count: int = Field(0, description="Количество ответов")


class MonthlyStats(BaseModel):
    """Статистика по месяцу"""
    month: str = Field(..., description="Месяц (YYYY-MM)")
    avg_umux: float = Field(0.0, description="Средний UMUX")
    count: int = Field(0, description="Количество ответов")


class PlatformStats(BaseModel):
    """Статистика по платформе"""
    platform: str = Field(..., description="Название платформы")
    avg_umux: float = Field(0.0, description="Средний UMUX")
    count: int = Field(0, description="Количество ответов")


class AggregationResponse(BaseModel):
    """Ответ с агрегированными данными"""
    status: str = Field(..., description="Статус операции")
    total: int = Field(0, description="Всего записей")
    overall: OverallStats = Field(default_factory=OverallStats, description="Общая статистика")
    by_product: List[ProductStats] = Field(default_factory=list, description="По продуктам")
    by_product_version: List[ProductVersionStats] = Field(default_factory=list, description="По версиям")
    by_month: List[MonthlyStats] = Field(default_factory=list, description="По месяцам")
    by_platform: List[PlatformStats] = Field(default_factory=list, description="По платформам")


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    status: str = Field("error", description="Статус")
    detail: str = Field(..., description="Описание ошибки")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время ошибки")
