import pandas as pd
from pathlib import Path
from typing import Optional

from app.utils.logger import logger
from ..core.interfaces import IDataLoader


class CSVLoader(IDataLoader):
    """
    Загрузчик CSV файлов с автоматическим определением:
    - Разделителя (запятая, точка с запятой)
    - Наличия заголовков
    - Кодировки
    """

    EXPECTED_COLUMNS = ['response_id', 'submitted_at', 'product', 'product_version', 
                        'platform', 'country', 'user_segment', 'score1', 'score2']

    def __init__(self, encoding: str = 'utf-8', has_header: Optional[bool] = None):
        self.encoding = encoding
        self.has_header = has_header

    def load(self, file_path: str) -> Optional[pd.DataFrame]:
        """Загружает CSV файл"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"Файл не найден: {file_path}")
                return None

            sep = self._detect_separator(file_path)

            has_header = self._detect_header(file_path)

            if has_header:
                df = pd.read_csv(
                    file_path,
                    sep=sep,
                    encoding=self.encoding,
                    dtype=str,
                    keep_default_na=False,
                    na_values=['', 'NA', 'null', 'NULL', 'None', 'nan', 'NaN']
                )
                df.columns = df.columns.str.strip().str.lower()
            else:
                df = pd.read_csv(
                    file_path,
                    sep=sep,
                    encoding=self.encoding,
                    header=None,
                    dtype=str,
                    keep_default_na=False,
                    na_values=['', 'NA', 'null', 'NULL', 'None', 'nan', 'NaN']
                )
                if len(df.columns) == len(self.EXPECTED_COLUMNS):
                    df.columns = self.EXPECTED_COLUMNS
                else:
                    df.columns = [f'col_{i}' for i in range(len(df.columns))]
                    logger.warning(f"Не совпадает количество колонок: {len(df.columns)} vs {len(self.EXPECTED_COLUMNS)}")

            logger.info(f"Загружено {len(df)} строк, колонки: {list(df.columns)}")

            df = self._convert_types(df)

            return df

        except pd.errors.EmptyDataError:
            logger.error(f"Файл {file_path} пуст")
            return None
        except UnicodeDecodeError:
            logger.warning(f"Ошибка кодировки, пробуем cp1251")
            return self._load_with_encoding(file_path, 'cp1251')
        except Exception as e:
            logger.error(f"Ошибка загрузки файла {file_path}: {e}")
            return None

    def _load_with_encoding(self, file_path: str, encoding: str) -> Optional[pd.DataFrame]:
        """Пробует загрузить с другой кодировкой"""
        try:
            sep = self._detect_separator(file_path)
            has_header = self._detect_header(file_path)

            if has_header:
                df = pd.read_csv(
                    file_path,
                    sep=sep,
                    encoding=encoding,
                    dtype=str,
                    keep_default_na=False,
                    na_values=['', 'NA', 'null', 'NULL', 'None', 'nan', 'NaN']
                )
                df.columns = df.columns.str.strip().str.lower()
            else:
                df = pd.read_csv(
                    file_path,
                    sep=sep,
                    encoding=encoding,
                    header=None,
                    dtype=str,
                    keep_default_na=False,
                    na_values=['', 'NA', 'null', 'NULL', 'None', 'nan', 'NaN']
                )
                if len(df.columns) == len(self.EXPECTED_COLUMNS):
                    df.columns = self.EXPECTED_COLUMNS
                else:
                    df.columns = [f'col_{i}' for i in range(len(df.columns))]

            df = self._convert_types(df)
            logger.info(f"Файл загружен с кодировкой {encoding}")
            return df
        except Exception as e:
            logger.error(f"Не удалось загрузить с кодировкой {encoding}: {e}")
            return None

    def _detect_separator(self, file_path: str) -> str:
        """Определяет разделитель в CSV файле"""
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                first_line = f.readline()
                if '\t' in first_line:
                    return '\t'
                elif ';' in first_line:
                    return ';'
                else:
                    return ','
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='cp1251') as f:
                    first_line = f.readline()
                    if '\t' in first_line:
                        return '\t'
                    elif ';' in first_line:
                        return ';'
                    else:
                        return ','
            except:
                return ','
        except Exception:
            return ','

    def _detect_header(self, file_path: str) -> bool:
        """
        Определяет, есть ли в файле заголовок.
        Проверяет первую строку: если она содержит типичные названия колонок - есть заголовок.
        """
        if self.has_header is not None:
            return self.has_header

        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                first_line = f.readline().strip().lower()

                header_keywords = ['response_id', 'submitted_at', 'product', 'version', 
                                  'score', 'platform', 'country', 'segment', 'id']

                for keyword in header_keywords:
                    if keyword in first_line:
                        logger.debug("🔍 Определен заголовок в файле")
                        return True

                parts = first_line.split(',')
                if parts and (parts[0].startswith('R') or parts[0].startswith('r')):
                    logger.debug("🔍 Первая строка похожа на данные (начинается с R)")
                    return False

                return False

        except Exception as e:
            logger.debug(f"Не удалось определить наличие заголовка: {e}")
            return False

    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Конвертирует типы данных"""
        df = df.copy()

        for col in df.columns:
            if df[col].isnull().all():
                continue

            try:
                cleaned = df[col].astype(str).str.strip()
                cleaned = cleaned.str.replace(',', '.')
                cleaned = cleaned.replace('', pd.NA)

                numeric = pd.to_numeric(cleaned, errors='coerce')
                if numeric.notna().sum() > 0:
                    if numeric.dropna().apply(lambda x: float(x).is_integer()).all():
                        df[col] = numeric.astype('Int64')
                    else:
                        df[col] = numeric
                    continue
            except:
                pass

            if col not in ['product_version', 'version', 'ver']:
                try:
                    dates = pd.to_datetime(df[col],
                                           format='%Y-%m-%d %H:%M:%S',
                                           errors='coerce')
                    if dates.notna().sum() > 3:
                        df[col] = dates
                        continue
                except:
                    pass

            df[col] = df[col].astype(str).str.strip()

        return df

    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.csv', '.tsv', '.txt'))
