from enum import Enum
from typing import Optional


class Platform(str, Enum):
    """Допустимые платформы"""
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"

    @classmethod
    def normalize(cls, value: str) -> Optional['Platform']:
        """Нормализует строку в Platform"""
        if not value:
            return None
        value = value.lower().strip()
        for platform in cls:
            if platform.value == value:
                return platform
        return None

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, является ли значение допустимой платформой"""
        return cls.normalize(value) is not None


class UserSegment(str, Enum):
    """Сегменты пользователей"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"
    UNKNOWN = "unknown"

    @classmethod
    def normalize(cls, value: str) -> 'UserSegment':
        """Нормализует строку в UserSegment"""
        if not value:
            return cls.UNKNOWN
        value = value.lower().strip()
        for segment in cls:
            if segment.value == value:
                return segment
        return cls.UNKNOWN


class RejectionReason(str, Enum):
    """Причины отбраковки записей"""
    DUPLICATE = "duplicate"
    MISSING_FIELD = "missing_field"
    INVALID_SCORE = "invalid_score"
    INVALID_DATE = "invalid_date"
    INVALID_PLATFORM = "invalid_platform"
    EMPTY_STRING = "empty_string"
    UNKNOWN = "unknown"


class MetricType(str, Enum):
    """Типы метрик"""
    UMUX = "umux"


class AggregationDimension(str, Enum):
    """Измерения для агрегации"""
    PRODUCT = "product"
    PRODUCT_VERSION = "product_version"
    PLATFORM = "platform"
    MONTH = "month"
    COUNTRY = "country"
    USER_SEGMENT = "user_segment"


class ExportFormat(str, Enum):
    """Форматы экспорта"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    HTML = "html"
    PDF = "pdf"
