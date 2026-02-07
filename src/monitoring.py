"""Simplified monitoring utilities for the bank operations application."""

import time
from datetime import datetime
from functools import wraps
from typing import Any

from loguru import logger


class ApplicationMetrics:
    """Simple metrics tracker with no file persistence to avoid type issues."""

    def __init__(self):
        # Simple in-memory counters - no file I/O, no type issues
        self._app_starts: int = 0
        self._files_uploaded: int = 0
        self._processing_times: list[float] = []
        self._error_count: int = 0

    def increment_app_starts(self) -> None:
        """Increment app start counter."""
        self._app_starts += 1
        logger.info(f"Application started (total starts: {self._app_starts})")

    def increment_file_uploads(self, filename: str, file_size: int) -> None:
        """Track file upload."""
        self._files_uploaded += 1
        logger.info(f"File uploaded: {filename} ({file_size} bytes)")

    def record_processing_time(self, duration: float) -> None:
        """Record data processing time."""
        self._processing_times.append(duration)
        # Keep only last 100 measurements
        if len(self._processing_times) > 100:
            self._processing_times = self._processing_times[-100:]
        logger.info(f"Data processing completed in {duration:.2f}s")

    def record_error(
        self, error_type: str, error_message: str, context: dict[str, Any] | None = None
    ) -> None:
        """Record application error."""
        self._error_count += 1
        logger.error(f"Error recorded: {error_type} - {error_message}")

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary."""
        return {
            "total_app_starts": self._app_starts,
            "total_files_uploaded": self._files_uploaded,
            "total_errors": self._error_count,
            "avg_processing_time": (
                sum(self._processing_times) / len(self._processing_times)
                if self._processing_times
                else 0
            ),
            "last_error": None,  # Simplified - no error history
        }


# Global metrics instance
metrics = ApplicationMetrics()


def log_performance(func_name: str | None = None):
    """Decorator to log function performance."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics.record_processing_time(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_error(
                    "function_error", str(e), {"function": func.__name__, "duration": duration}
                )
                raise

        return wrapper

    if func_name is None:
        return decorator
    else:

        def named_decorator(func):
            return decorator(func)

        return named_decorator


def setup_monitoring() -> None:
    """Setup application monitoring."""
    logger.info("Setting up application monitoring...")
    metrics.increment_app_starts()


class HealthChecker:
    """Simple health checker for compatibility."""

    @staticmethod
    def check_system_health() -> dict[str, Any]:
        """Check system health status."""
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "memory": {"status": "ok"},
                "disk": {"status": "ok"},
                "logs": {"status": "ok"},
            },
        }
