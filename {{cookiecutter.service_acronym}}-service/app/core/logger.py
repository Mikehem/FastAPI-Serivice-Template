#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import time
import sys

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from omegaconf import OmegaConf
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from app.core.config import cfg

log_level = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

def log_setup(cfg: OmegaConf, app_name: str, filelogging: bool = True, consolelogging: bool = False):
    LoggingInstrumentor().instrument(set_logging_format=True)
    logger = logging.getLogger()
    formatter = logging.Formatter(cfg.Logger[app_name].OTELFormat)
    formatter.converter = time.gmtime  # if you want UTC time
    if filelogging:
        handler = TimedRotatingFileHandler(
            cfg.Logger[app_name].Filename,
            when="midnight",
            backupCount=cfg.Logger[app_name].BackupCount
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    if consolelogging:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(log_level[cfg.Logger[app_name].Level])
    print("Logger Initialized ...")
    return logger
