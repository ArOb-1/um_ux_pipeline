import logging
from pathlib import Path


def setup_logger(name: str = "umux",
                 log_file: str = "logs/umux.log") -> logging.Logger:
    """Настройка логгера для записи в файл"""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.flush = lambda: (file_handler.stream.flush()
                                  if file_handler.stream else None)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()


def flush_logs():
    for handler in logger.handlers:
        if hasattr(handler, 'flush'):
            handler.flush()
