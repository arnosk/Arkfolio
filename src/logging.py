"""
@author: Arno
@created: 2023-05-17
@modified: 2023-05-20

Logging module

"""
import datetime
import logging
import time
from logging.config import dictConfig
from pathlib import Path
from typing import Any

import config


class ISOFormatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""

    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.astimezone()

    def formatTime(self, record, datefmt=None) -> str:
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec="milliseconds")
            except TypeError:
                s = dt.isoformat()
        return s


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


def config_logging() -> None:
    logpath = config.LOG_PATH
    if logpath != "":
        logpath = f"{logpath}\\"
    logfile = f"{logpath}{config.LOG_FILE}"
    logfilepath = Path(logfile)
    logfilepath.parent.mkdir(parents=True, exist_ok=True)

    max_bytes = config.MAX_SIZE_LOGFILE_MB * 1024 * 1000
    num_logfiles = config.NUM_LOGFILES
    loglevel = config.LOG_LEVEL

    formatters = {
        "ISO": {
            "()": ISOFormatter,
            "format": "[%(asctime)s] %(levelname)-6s - %(name)s: %(message)s",
        },
        "UTC": {
            "()": UTCFormatter,
            "format": "[%(asctime)s.%(msecs)03d] %(levelname)-6s - %(name)s: %(message)s",
        },
        "default": {
            "format": "[%(asctime)s.%(msecs)03d] %(levelname)-6s - %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[%(asctime)s] %(levelname)-6s - %(message)s",
            "datefmt": "%H:%M:%S",
        },
    }
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": loglevel,
            "formatter": "ISO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logfile,
            "mode": "a",
            "maxBytes": max_bytes,
            "backupCount": num_logfiles,
            "level": loglevel,
            "formatter": "ISO",
            "encoding": "utf-8",
        },
    }
    filters = {}
    loggers: dict[str, Any] = {
        "": {  # root logger
            "level": loglevel,
            "handlers": handlers,
        },
    }
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": filters,
            "formatters": formatters,
            "handlers": handlers,
            "loggers": loggers,
        }
    )

    return
