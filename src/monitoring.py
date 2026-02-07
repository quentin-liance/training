"""Advanced logging and monitoring utilities for the bank operations application."""

import json
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, TypedDict, cast

from loguru import logger


class MetricsData(TypedDict):
    """Type definition for metrics data structure."""

    app_starts: int
    files_uploaded: int
    data_processing_time: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    users_sessions: int


class ApplicationMetrics:
    """Track application metrics and performance."""

    def __init__(self):
        self.metrics: MetricsData = {
            "app_starts": 0,
            "files_uploaded": 0,
            "data_processing_time": [],
            "errors": [],
            "users_sessions": 0,
        }
        self.metrics_file = Path(__file__).parent.parent / "logs" / "metrics.json"
        self.load_metrics()

    def load_metrics(self):
        """Load existing metrics from file."""
        if self.metrics_file.exists():
            try:
                with self.metrics_file.open() as f:
                    saved_metrics = json.load(f)
                    # Validate and load only safe data with proper types
                    if isinstance(saved_metrics, dict):
                        # Safely update with type validation
                        if "app_starts" in saved_metrics and isinstance(
                            saved_metrics["app_starts"], int
                        ):
                            self.metrics["app_starts"] = saved_metrics["app_starts"]
                        if "files_uploaded" in saved_metrics and isinstance(
                            saved_metrics["files_uploaded"], int
                        ):
                            self.metrics["files_uploaded"] = saved_metrics["files_uploaded"]
                        if "data_processing_time" in saved_metrics and isinstance(
                            saved_metrics["data_processing_time"], list
                        ):
                            self.metrics["data_processing_time"] = saved_metrics[
                                "data_processing_time"
                            ]
                        if "errors" in saved_metrics and isinstance(saved_metrics["errors"], list):
                            self.metrics["errors"] = saved_metrics["errors"]
                        if "users_sessions" in saved_metrics and isinstance(
                            saved_metrics["users_sessions"], int
                        ):
                            self.metrics["users_sessions"] = saved_metrics["users_sessions"]
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")

    def save_metrics(self):
        """Save metrics to file."""
        try:
            self.metrics_file.parent.mkdir(exist_ok=True)
            with self.metrics_file.open("w") as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def increment_app_starts(self):
        """Increment app start counter."""
        app_starts = cast(int, self.metrics["app_starts"])
        self.metrics["app_starts"] = app_starts + 1
        self.save_metrics()
        logger.info(f"Application started (total starts: {self.metrics['app_starts']})")

    def increment_file_uploads(self, filename: str, file_size: int):
        """Track file upload."""
        files_uploaded = cast(int, self.metrics["files_uploaded"])
        self.metrics["files_uploaded"] = files_uploaded + 1
        self.save_metrics()
        logger.info(f"File uploaded: {filename} ({file_size} bytes)")

    def record_processing_time(self, duration: float):
        """Record data processing time."""
        processing_time_list = cast(list[dict[str, Any]], self.metrics["data_processing_time"])
        processing_time_list.append({"duration": duration, "timestamp": datetime.now().isoformat()})
        # Keep only last 100 measurements
        if len(processing_time_list) > 100:
            self.metrics["data_processing_time"] = processing_time_list[-100:]
        self.save_metrics()
        logger.info(f"Data processing completed in {duration:.2f}s")

    def record_error(
        self, error_type: str, error_message: str, context: dict[str, Any] | None = None
    ):
        """Record application error."""
        error_data = {
            "type": error_type,
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
        }
        errors_list = cast(list[dict[str, Any]], self.metrics["errors"])
        errors_list.append(error_data)
        # Keep only last 50 errors
        if len(errors_list) > 50:
            self.metrics["errors"] = errors_list[-50:]
        self.save_metrics()
        logger.error(f"Error recorded: {error_type} - {error_message}")

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary."""
        processing_time_list = cast(list[dict[str, Any]], self.metrics["data_processing_time"])
        processing_times = [item["duration"] for item in processing_time_list]
        errors_list = cast(list[dict[str, Any]], self.metrics["errors"])
        app_starts = cast(int, self.metrics["app_starts"])
        files_uploaded = cast(int, self.metrics["files_uploaded"])

        return {
            "total_app_starts": app_starts,
            "total_files_uploaded": files_uploaded,
            "total_errors": len(errors_list),
            "avg_processing_time": sum(processing_times) / len(processing_times)
            if processing_times
            else 0,
            "last_error": errors_list[-1] if errors_list else None,
        }


# Global metrics instance
metrics = ApplicationMetrics()


def log_performance(func_name: str | None = None):
    """Decorator to log function performance."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func_name or func.__name__

            try:
                logger.debug(f"Starting {function_name}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.info(f"Completed {function_name} in {duration:.2f}s")
                metrics.record_processing_time(duration)

                return result

            except Exception as e:
                duration = time.time() - start_time
                metrics.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context={
                        "function": function_name,
                        "duration": duration,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    },
                )
                raise

        return wrapper

    return decorator


class HealthChecker:
    """Health check utilities for monitoring."""

    @staticmethod
    def check_system_health() -> dict[str, Any]:
        """Check overall system health."""
        import os

        import psutil

        health_status: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {},
        }

        try:
            # Memory usage
            memory = psutil.virtual_memory()
            health_status["checks"]["memory"] = {
                "used_percent": memory.percent,
                "available_mb": memory.available / (1024 * 1024),
                "status": "ok" if memory.percent < 90 else "warning",
            }

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            health_status["checks"]["disk"] = {
                "used_percent": disk_percent,
                "free_gb": disk.free / (1024**3),
                "status": "ok" if disk_percent < 90 else "warning",
            }

            # Logs directory
            logs_dir = Path(__file__).parent.parent / "logs"
            health_status["checks"]["logs_directory"] = {
                "exists": logs_dir.exists(),
                "writable": os.access(logs_dir, os.W_OK) if logs_dir.exists() else False,
                "status": "ok" if logs_dir.exists() and os.access(logs_dir, os.W_OK) else "error",
            }

            # Overall status
            all_checks = [check["status"] for check in health_status["checks"].values()]
            if "error" in all_checks:
                health_status["status"] = "unhealthy"
            elif "warning" in all_checks:
                health_status["status"] = "degraded"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Health check failed: {e}")

        return health_status


def setup_monitoring():
    """Setup monitoring and health checks."""
    logger.info("Setting up application monitoring")
    metrics.increment_app_starts()

    # Log system info
    health = HealthChecker.check_system_health()
    logger.info(f"System health: {health['status']}")

    # Log performance summary
    perf_summary = metrics.get_performance_summary()
    logger.info(f"Performance summary: {perf_summary}")
