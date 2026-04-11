# src/utils/logger.py

import logging
import os
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Menginisialisasi dan mengembalikan logger dengan Console dan File handler.
    Menghindari duplikasi handler jika logger dengan nama yang sama dipanggil ulang.
    """
    logger = logging.getLogger(name)

    # Mencegah penambahan handler ganda jika logger sudah diinisialisasi sebelumnya
    if logger.hasHandlers():
        return logger

    # Menentukan level log dari environment variable (default: INFO)
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    # Membuat format log terstruktur: ISO 8601 Timestamp | LEVEL | logger_name | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    # 1. Handler untuk Console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Handler untuk File (logs/app.log)
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)  # Buat folder logs/ jika belum ada

    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger