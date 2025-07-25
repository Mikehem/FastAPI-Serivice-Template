#noqa
from app.core.logger import log_setup
from app.core.config import cfg

global logger
global logger_run
logger = log_setup(cfg, "app")
