#!/usr/bin/env python
"""
Flight data logger — saves telemetry + flight script for later analysis.
"""
from __future__ import division, absolute_import, print_function
import time
import os
import csv
import shutil
import threading

_logger_instance = None


class FlightLogger:
    """Records all drone telemetry to CSV + saves a copy of the flight script."""

    def __init__(self, save_dir="./flight_logs", script_path=None):
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._save_dir = save_dir
        self._script_path = script_path
        self._csv_file = None
        self._csv_writer = None
        self._start_time = None

    def start(self):
        """Begin recording. Creates a timestamped session directory."""
        if self._running:
            return

        session_ts = time.strftime("%Y%m%d_%H%M%S")
        self._session_dir = os.path.join(self._save_dir, f"flight_{session_ts}")
        os.makedirs(self._session_dir, exist_ok=True)

        # Save a copy of the flight script
        if self._script_path and os.path.exists(self._script_path):
            script_name = os.path.basename(self._script_path)
            shutil.copy2(self._script_path,
                         os.path.join(self._session_dir, script_name))
            print(f"[Logger] 脚本已保存: {self._session_dir}/{script_name}")

        # Open CSV for telemetry
        csv_path = os.path.join(self._session_dir, "telemetry.csv")
        self._csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
        self._csv_writer = csv.writer(self._csv_file)
        self._csv_writer.writerow([
            "timestamp", "elapsed_ms", "uavid",
            "x_cm", "y_cm", "z_cm", "yaw_cdeg",
            "battery_pct",
            "fcstatus", "flightmode", "gpsstatus"
        ])
        self._csv_file.flush()

        self._start_time = time.perf_counter()
        self._running = True
        self._thread = threading.Thread(target=self._logging_loop, daemon=True)
        self._thread.start()
        print(f"[Logger] 遥测记录开始 → {csv_path}")

    def stop(self):
        """Stop recording and close files."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        if self._csv_file:
            self._csv_file.close()
            self._csv_file = None
        file_count = len(os.listdir(self._session_dir)) if hasattr(self, '_session_dir') else 0
        print(f"[Logger] 记录已停止 → {self._session_dir} ({file_count} files)")

    def _logging_loop(self):
        """Poll heartbeat data and write to CSV every ~200ms."""
        from fwfii.fc.heartbeat import HeartBeat

        while self._running:
            try:
                with HeartBeat._lock:
                    flights_snapshot = list(HeartBeat.flights.items())
            except Exception:
                time.sleep(0.2)
                continue

            now = time.perf_counter()
            elapsed_ms = int((now - self._start_time) * 1000)
            ts = time.strftime("%H:%M:%S") + f".{int(time.time() * 1000) % 1000:03d}"

            for uavid, flight in flights_snapshot:
                x, y, z, yaw = flight.position
                bat_pct = flight.voltage if flight.voltage else 0

                try:
                    self._csv_writer.writerow([
                        ts, elapsed_ms, uavid,
                        f"{x:.1f}", f"{y:.1f}", f"{z:.1f}", f"{yaw:.1f}",
                        f"{bat_pct:.0f}",
                        flight.fcstatus, flight.flightmode, flight.gpsstatus
                    ])
                except Exception:
                    pass

            try:
                self._csv_file.flush()
            except Exception:
                pass

            time.sleep(0.2)

    @property
    def session_dir(self):
        return getattr(self, '_session_dir', None)


# ==========================================
# Quick API
# ==========================================

def start_log(save_dir="./flight_logs", script_path=None):
    """Start recording all flight telemetry to CSV."""
    global _logger_instance
    if _logger_instance is not None and _logger_instance._running:
        _logger_instance.stop()
    _logger_instance = FlightLogger(save_dir, script_path)
    _logger_instance.start()
    return _logger_instance


def stop_log():
    """Stop recording."""
    global _logger_instance
    if _logger_instance is not None:
        _logger_instance.stop()
        _logger_instance = None


def is_logging():
    """Check if logger is active."""
    return _logger_instance is not None and _logger_instance._running
