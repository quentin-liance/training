#!/usr/bin/env python3
"""Log monitoring and analysis script for the bank operations application."""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click


class LogAnalyzer:
    """Analyze application logs for insights and issues."""

    def __init__(self, logs_dir: Optional[Path] = None):
        self.logs_dir = logs_dir or Path(__file__).parent.parent / "logs"
        self.patterns = {
            "error": re.compile(r"ERROR.*"),
            "warning": re.compile(r"WARNING.*"),
            "upload": re.compile(r"File uploaded: (.+) \((\d+) bytes\)"),
            "processing": re.compile(r"Data processing completed in ([\d.]+)s"),
            "app_start": re.compile(r"Application started.*"),
        }

    def get_log_files(self, days: int = 7) -> list[Path]:
        """Get log files from the last N days."""
        files = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            log_file = self.logs_dir / f"app_{date.strftime('%Y-%m-%d')}.log"
            if log_file.exists():
                files.append(log_file)
        return files

    def analyze_logs(self, days: int = 7) -> dict:
        """Analyze logs and return summary."""
        log_files = self.get_log_files(days)
        analysis = {
            "period": f"Last {days} days",
            "files_analyzed": len(log_files),
            "total_lines": 0,
            "errors": [],
            "warnings": [],
            "uploads": [],
            "processing_times": [],
            "app_starts": 0,
            "summary": {},
        }

        for log_file in log_files:
            try:
                with open(log_file, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        analysis["total_lines"] += 1

                        # Check for errors
                        if self.patterns["error"].search(line):
                            analysis["errors"].append(
                                {"file": log_file.name, "line": line_num, "message": line.strip()}
                            )

                        # Check for warnings
                        elif self.patterns["warning"].search(line):
                            analysis["warnings"].append(
                                {"file": log_file.name, "line": line_num, "message": line.strip()}
                            )

                        # Check for file uploads
                        upload_match = self.patterns["upload"].search(line)
                        if upload_match:
                            analysis["uploads"].append(
                                {
                                    "filename": upload_match.group(1),
                                    "size": int(upload_match.group(2)),
                                    "timestamp": self._extract_timestamp(line),
                                }
                            )

                        # Check for processing times
                        proc_match = self.patterns["processing"].search(line)
                        if proc_match:
                            analysis["processing_times"].append(float(proc_match.group(1)))

                        # Check for app starts
                        if self.patterns["app_start"].search(line):
                            analysis["app_starts"] += 1

            except Exception as e:
                print(f"Error reading {log_file}: {e}")

        # Generate summary
        analysis["summary"] = {
            "error_count": len(analysis["errors"]),
            "warning_count": len(analysis["warnings"]),
            "upload_count": len(analysis["uploads"]),
            "avg_processing_time": (
                sum(analysis["processing_times"]) / len(analysis["processing_times"])
                if analysis["processing_times"]
                else 0
            ),
            "max_processing_time": max(analysis["processing_times"], default=0),
            "total_app_starts": analysis["app_starts"],
        }

        return analysis

    def _extract_timestamp(self, line: str) -> Optional[str]:
        """Extract timestamp from log line."""
        timestamp_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        match = timestamp_pattern.search(line)
        return match.group(1) if match else None


class LogMonitor:
    """Real-time log monitoring."""

    def __init__(self, logs_dir: Optional[Path] = None):
        self.logs_dir = logs_dir or Path(__file__).parent.parent / "logs"
        self.running = False

    def tail_logs(self, follow: bool = True):
        """Tail application logs."""
        today_log = self.logs_dir / f"app_{datetime.now().strftime('%Y-%m-%d')}.log"

        if not today_log.exists():
            print(f"No log file found: {today_log}")
            return

        if follow:
            # Use tail -f to follow the log file
            try:
                process = subprocess.Popen(
                    ["tail", "-f", str(today_log)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                print(f"Following log file: {today_log}")
                print("Press Ctrl+C to stop...")

                for line in iter(process.stdout.readline, ""):
                    if line:
                        # Color code different log levels
                        if "ERROR" in line:
                            print(f"\033[91m{line.strip()}\033[0m")  # Red
                        elif "WARNING" in line:
                            print(f"\033[93m{line.strip()}\033[0m")  # Yellow
                        elif "INFO" in line:
                            print(f"\033[92m{line.strip()}\033[0m")  # Green
                        else:
                            print(line.strip())

            except KeyboardInterrupt:
                process.terminate()
                print("\nStopped monitoring logs")
            except Exception as e:
                print(f"Error monitoring logs: {e}")
        else:
            # Just show last N lines
            try:
                with open(today_log) as f:
                    lines = f.readlines()
                    for line in lines[-50:]:  # Show last 50 lines
                        print(line.strip())
            except Exception as e:
                print(f"Error reading logs: {e}")


@click.group()
def cli():
    """Bank Operations Application Log Monitoring Tool."""
    pass


@cli.command()
@click.option("--days", default=7, help="Number of days to analyze (default: 7)")
@click.option(
    "--format",
    "output_format",
    default="text",
    type=click.Choice(["text", "json"]),
    help="Output format",
)
def analyze(days: int, output_format: str):
    """Analyze application logs."""
    analyzer = LogAnalyzer()
    analysis = analyzer.analyze_logs(days)

    if output_format == "json":
        print(json.dumps(analysis, indent=2, default=str))
    else:
        print(f"📊 Log Analysis - {analysis['period']}")
        print("=" * 50)
        print(f"Files analyzed: {analysis['files_analyzed']}")
        print(f"Total log lines: {analysis['total_lines']:,}")
        print(f"App starts: {analysis['summary']['total_app_starts']}")
        print(f"File uploads: {analysis['summary']['upload_count']}")
        print(f"Errors: {analysis['summary']['error_count']}")
        print(f"Warnings: {analysis['summary']['warning_count']}")
        print(f"Avg processing time: {analysis['summary']['avg_processing_time']:.2f}s")
        print(f"Max processing time: {analysis['summary']['max_processing_time']:.2f}s")

        if analysis["errors"]:
            print("\n🔴 Recent Errors:")
            for error in analysis["errors"][-5:]:  # Show last 5 errors
                print(f"  • {error['file']}:{error['line']} - {error['message']}")


@cli.command()
@click.option("--follow/--no-follow", default=True, help="Follow log file in real-time")
def monitor(follow: bool):
    """Monitor application logs in real-time."""
    monitor = LogMonitor()
    monitor.tail_logs(follow)


@cli.command()
def health():
    """Check application health status."""
    from src.monitoring import HealthChecker, metrics

    health_status = HealthChecker.check_system_health()
    perf_summary = metrics.get_performance_summary()

    print("🏥 Application Health Check")
    print("=" * 30)
    print(f"Status: {health_status['status'].upper()}")
    print(f"Timestamp: {health_status['timestamp']}")

    print("\n📈 Performance Metrics:")
    print(f"  Total app starts: {perf_summary['total_app_starts']}")
    print(f"  Total files uploaded: {perf_summary['total_files_uploaded']}")
    print(f"  Total errors: {perf_summary['total_errors']}")
    print(f"  Avg processing time: {perf_summary['avg_processing_time']:.2f}s")

    print("\n🔍 System Checks:")
    for check_name, check_data in health_status["checks"].items():
        status_icon = (
            "✅"
            if check_data["status"] == "ok"
            else "⚠️"
            if check_data["status"] == "warning"
            else "❌"
        )
        print(f"  {status_icon} {check_name}: {check_data['status']}")


if __name__ == "__main__":
    cli()
