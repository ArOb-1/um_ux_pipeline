import pandas as pd
import logging
from typing import List, Tuple, Dict
from collections import defaultdict

from ..core.interfaces import IValidator
from ..core.enums import Platform, RejectionReason

logger = logging.getLogger(__name__)


class ValidationRule:
    """Базовый класс для правил валидации"""

    def __init__(self, name: str):
        self.name = name

    def validate(self, df: pd.DataFrame) -> Tuple[pd.Series, str]:
        raise NotImplementedError


class RequiredFieldsRule(ValidationRule):
    """Проверка обязательных полей"""

    def __init__(self, fields: List[str]):
        super().__init__("required_fields")
        self.fields = fields

    def validate(self, df: pd.DataFrame) -> Tuple[pd.Series, str]:
        logger.info('Валидация required field')
        mask = pd.Series([True] * len(df))
        for field in self.fields:
            if field in df.columns:
                mask &= df[field].notna()
        return mask, RejectionReason.MISSING_FIELD.value


class ScoreRangeRule(ValidationRule):
    """Проверка диапазона скора (1-5)"""

    def __init__(self, min_val: int = 1, max_val: int = 5):
        super().__init__("score_range")
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, df: pd.DataFrame) -> Tuple[pd.Series, str]:
        logger.info('Валидация Score Range (1-5)')
        mask = pd.Series([True] * len(df))
        if 'score1' in df.columns:
            mask &= df['score1'].between(self.min_val, self.max_val)
        if 'score2' in df.columns:
            mask &= df['score2'].between(self.min_val, self.max_val)
        return mask, RejectionReason.INVALID_SCORE.value


class PlatformValidationRule(ValidationRule):
    """Проверка платформы"""

    def __init__(self):
        super().__init__("platform_validation")

    def validate(self, df: pd.DataFrame) -> Tuple[pd.Series, str]:
        logger.info('Валидация платформы')
        mask = pd.Series([True] * len(df))
        if 'platform' in df.columns:
            normalized = df['platform'].astype(str).str.lower().str.strip()
            valid_platforms = [p.value for p in Platform]
            mask = normalized.isin(valid_platforms)
        return mask, RejectionReason.INVALID_PLATFORM.value


class DateValidationRule(ValidationRule):
    """Проверка даты (валидный формат и разумный диапазон)"""

    def __init__(self, min_year: int = 2020, max_year: int = 2026):
        super().__init__("date_validation")
        self.min_year = min_year
        self.max_year = max_year

    def validate(self, df: pd.DataFrame) -> Tuple[pd.Series, str]:
        logger.info('Валидация даты')
        mask = pd.Series([True] * len(df))

        if 'submitted_at' not in df.columns:
            return mask, RejectionReason.INVALID_DATE.value

        dates = pd.to_datetime(df['submitted_at'], errors='coerce')

        valid_date = dates.notna()

        if valid_date.any():
            years = dates.dt.year
            valid_year = years.between(self.min_year, self.max_year)
            valid_date = valid_date & valid_year

        mask = valid_date
        return mask, RejectionReason.INVALID_DATE.value


class DuplicateRule(ValidationRule):
    """Проверка дубликатов по response_id"""

    def __init__(self, key_field: str = 'response_id'):
        super().__init__("duplicate_check")
        self.key_field = key_field

    def validate(self, df: pd.DataFrame) -> Tuple[pd.Series, str]:
        logger.info('Валидация дубликатов по response_id')
        mask = pd.Series([True] * len(df))
        if self.key_field in df.columns:
            mask = ~df.duplicated(subset=[self.key_field], keep='first')
        return mask, RejectionReason.DUPLICATE.value


class EmptyStringRule(ValidationRule):
    """Проверка пустых строк"""

    def __init__(self, fields: List[str]):
        super().__init__("empty_string")
        self.fields = fields

    def validate(self, df: pd.DataFrame) -> Tuple[pd.Series, str]:
        logger.info('Проверка на пустые строки')
        mask = pd.Series([True] * len(df))
        for field in self.fields:
            if field in df.columns:
                mask &= df[field].astype(str).str.strip().ne('')
        return mask, RejectionReason.EMPTY_STRING.value


class UMUXValidator(IValidator):
    """Валидатор для UMUX-Lite данных"""

    def __init__(self, min_year: int = 2020, max_year: int = 2026):

        self.rules: List[ValidationRule] = []
        self._rejection_stats: Dict[str, int] = defaultdict(int)
        self.min_year = min_year
        self.max_year = max_year
        self._setup_rules()

    def _setup_rules(self):
        """Настройка правил валидации"""
        self.rules = [
            RequiredFieldsRule(['response_id', 'submitted_at', 'product', 
                               'product_version', 'score1', 'score2']),
            ScoreRangeRule(1, 5),
            PlatformValidationRule(),
            DateValidationRule(self.min_year, self.max_year),
            DuplicateRule('response_id'),
            EmptyStringRule(['product', 'product_version'])
        ]

    def add_rule(self, rule: ValidationRule) -> None:
        """Добавляет правило валидации"""
        self.rules.append(rule)

    def validate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Применяет все правила валидации"""
        if df.empty:
            return df, df

        df = df.copy()
        valid_mask = pd.Series([True] * len(df))
        rejection_reasons = []

        for rule in self.rules:
            mask, reason = rule.validate(df)
            if not mask.all():
                count = (~mask).sum()
                self._rejection_stats[reason] += count
                rejection_reasons.extend([reason] * count)
            valid_mask &= mask

        valid_df = df[valid_mask].copy()
        invalid_df = df[~valid_mask].copy()

        if not invalid_df.empty:
            invalid_df['rejection_reason'] = rejection_reasons[:len(invalid_df)]

        logger.info(f"Валидация: {len(valid_df)} валидных,"
                    "{len(invalid_df)} отбраковано")

        return valid_df, invalid_df

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Нормализация данных"""
        logger.info('Нормализация данных')
        if df.empty:
            return df

        df = df.copy()

        if 'product' in df.columns:
            df['product'] = df['product'].astype(str).str.strip().str.title()

        if 'product_version' in df.columns:
            df['product_version'] = (df['product_version'].
                                     astype(str).str.strip())

        if 'platform' in df.columns:
            df['platform'] = df['platform'].astype(str).str.lower().str.strip()
            df['platform'] = df['platform'].apply(
                lambda x: (Platform.normalize(x).value
                           if Platform.normalize(x) else 'unknown')
            )

        if 'submitted_at' in df.columns:
            df['submitted_at'] = pd.to_datetime(df['submitted_at'],
                                                errors='coerce')
            df['month'] = df['submitted_at'].dt.to_period('M').astype(str)

        for col in ['country', 'user_segment']:
            if col in df.columns:
                df[col] = df[col].fillna('unknown')

        return df

    def get_rejection_stats(self) -> Dict[str, int]:
        """Возвращает статистику отбраковки"""
        return dict(self._rejection_stats)
