import asyncio
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, TypeVar, Optional
import re

T = TypeVar("T")

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise last_exception

                    delay = min(delay * backoff_factor, max_delay)
                    await asyncio.sleep(delay)

            raise last_exception

        return wrapper
    return decorator

def rate_limit(calls: int, period: float):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        last_reset = utc_now()
        calls_made = 0

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal last_reset, calls_made

            now = utc_now()
            if (now - last_reset).total_seconds() >= period:
                calls_made = 0
                last_reset = now

            if calls_made >= calls:
                wait_time = period - (now - last_reset).total_seconds()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                calls_made = 0
                last_reset = utc_now()

            calls_made += 1
            return await func(*args, **kwargs)

        return wrapper
    return decorator

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def sanitize_string(text: str) -> str:
    return re.sub(r"[^\w\s-]", "", text).strip()

def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def parse_version(version: str) -> tuple:
    return tuple(map(int, version.lstrip("v").split("."))) 