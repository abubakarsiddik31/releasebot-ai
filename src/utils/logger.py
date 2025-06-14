import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
import uuid
from datetime import datetime

from src.config.settings import settings

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "correlation_id"):
            record.correlation_id = str(uuid.uuid4())
        return True

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CorrelationFilter())
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path / log_file,
            maxBytes=10_000_000,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(CorrelationFilter())
        logger.addHandler(file_handler)

    return logger

def get_correlation_id() -> str:
    return str(uuid.uuid4())

def log_execution_time(logger: logging.Logger):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            correlation_id = get_correlation_id()
            
            logger.info(
                f"Starting {func.__name__}",
                extra={"correlation_id": correlation_id}
            )
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                logger.info(
                    f"Completed {func.__name__} in {duration:.2f}s",
                    extra={"correlation_id": correlation_id}
                )
                return result
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    extra={"correlation_id": correlation_id}
                )
                raise
                
        return wrapper
    return decorator 