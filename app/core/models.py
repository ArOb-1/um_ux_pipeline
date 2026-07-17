"""
Модели данных для системы
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from .enums import Platform, UserSegment, RejectionReason


@dataclass
class ResponseRecord:
    """Модель одного ответа"""
    response_id: str
    submitted_at: datetime
    product: str
    product_version: str
    score1: int
    score2: int
    platform: Optional[str] = None
    country: Optional[str] = None
    user_segment: Optional[str] = None
    umux_score: Optional[float] = None
    month: Optional[str] = None
    is_valid: bool = True
    rejection_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь"""
        return {
            'response_id': self.response_id,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'product': self.product,
            'product_version': self.product_version,
            'platform': self.platform,
            'country': self.country,
            'user_segment': self.user_segment,
            'score1': self.score1,
            'score2': self.score2,
            'umux_score': self.umux_score,
            'month': self.month,
            'is_valid': self.is_valid,
            'rejection_reason': self.rejection_reason
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseRecord':
        """Создает объект из словаря"""
        return cls(
            response_id=str(data.get('response_id', '')),
            submitted_at=data.get('submitted_at', datetime.now()),
            product=str(data.get('product', '')),
            product_version=str(data.get('product_version', '')),
            platform=str(data.get('platform', '')),
            country=str(data.get('country', '')),
            user_segment=str(data.get('user_segment', '')),
            score1=int(data.get('score1', 0)),
            score2=int(data.get('score2', 0)),
            umux_score=float(data.get('umux_score', 0)) if data.get('umux_score') else None,
            month=str(data.get('month', '')) if data.get('month') else None
        )


@dataclass
class AggregationResult:
    """Результат агрегации"""
    dimension: str
    value: str
    avg_umux: float
    count: int
    std_umux: Optional[float] = None
    min_umux: Optional[float] = None
    max_umux: Optional[float] = None
    percentile_25: Optional[float] = None
    percentile_75: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь"""
        return {
            'dimension': self.dimension,
            'value': self.value,
            'avg_umux': round(self.avg_umux, 2),
            'std_umux': round(self.std_umux, 2) if self.std_umux else None,
            'count': self.count,
            'min_umux': round(self.min_umux, 2) if self.min_umux else None,
            'max_umux': round(self.max_umux, 2) if self.max_umux else None,
            'percentile_25': round(self.percentile_25, 2) if self.percentile_25 else None,
            'percentile_75': round(self.percentile_75, 2) if self.percentile_75 else None
        }


@dataclass
class PipelineResult:
    """Результат работы пайплайна"""
    total_valid: int = 0
    total_rejected: int = 0
    rejection_stats: Dict[str, int] = field(default_factory=dict)
    aggregations: Dict[str, Any] = field(default_factory=dict)
    visualizations: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    files_processed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь"""
        return {
            'total_valid': self.total_valid,
            'total_rejected': self.total_rejected,
            'rejection_stats': self.rejection_stats,
            'aggregations': self.aggregations,
            'processing_time': round(self.processing_time, 2),
            'files_processed': self.files_processed,
            'errors': self.errors
        }

    def to_summary(self) -> str:
        """Формирует текстовое резюме"""
        lines = [
            "=" * 50,
            "📊 UMUX Pipeline Summary",
            "=" * 50,
            f"✅ Valid responses: {self.total_valid}",
            f"❌ Rejected responses: {self.total_rejected}",
            f"⏱️  Processing time: {self.processing_time:.2f}s",
            f"📁 Files processed: {len(self.files_processed)}",
            "",
            "Rejection reasons:"
        ]

        for reason, count in self.rejection_stats.items():
            lines.append(f"  • {reason}: {count}")

        if self.aggregations and 'overall' in self.aggregations:
            overall = self.aggregations['overall']
            lines.extend([
                "",
                "Overall UMUX Statistics:",
                f"  • Average: {overall.get('avg_umux', 0):.2f}",
                f"  • Median: {overall.get('median_umux', 0):.2f}",
                f"  • Std Dev: {overall.get('std_umux', 0):.2f}",
                f"  • Min: {overall.get('min_umux', 0):.2f}",
                f"  • Max: {overall.get('max_umux', 0):.2f}",
            ])

        lines.append("=" * 50)
        return "\n".join(lines)
