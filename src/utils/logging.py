"""
src 工具模块 - logging

提供结构化日志管理
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum

import colorlog


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    """结构化日志管理器"""

    _instances: dict[str, logging.Logger] = {}
    _default_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

    def __init__(
        self,
        name: str = "src2",
        level: LogLevel = LogLevel.INFO,
        log_dir: Optional[Path] = None,
        console: bool = True,
        colored: bool = True,
    ):
        self.name = name
        self.level = level
        self.log_dir = log_dir
        self.console = console
        self.colored = colored
        self._logger: Optional[logging.Logger] = None

    @property
    def logger(self) -> logging.Logger:
        """获取logger实例"""
        if self._logger is not None:
            return self._logger

        if self.name in Logger._instances:
            self._logger = Logger._instances[self.name]
            return self._logger

        self._logger = self._create_logger()
        Logger._instances[self.name] = self._logger
        return self._logger

    def _create_logger(self) -> logging.Logger:
        """创建logger"""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.level.value))
        logger.handlers.clear()

        # 格式化器
        if self.colored and sys.stdout.isatty():
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        else:
            formatter = logging.Formatter(self._default_format, datefmt="%Y-%m-%d %H:%M:%S")

        # 控制台处理器
        if self.console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # 文件处理器
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            date_str = datetime.now().strftime("%Y%m%d")
            file_path = self.log_dir / f"{self.name}_{date_str}.log"

            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(self._default_format, datefmt="%Y-%m-%d %H:%M:%S")
            )
            logger.addHandler(file_handler)

        return logger

    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg, **kwargs)

    def info(self, msg: str, **kwargs):
        self.logger.info(msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self.logger.error(msg, **kwargs)

    def critical(self, msg: str, **kwargs):
        self.logger.critical(msg, **kwargs)

    def exception(self, msg: str, **kwargs):
        self.logger.exception(msg, **kwargs)


# 全局日志实例
_global_logger: Optional[Logger] = None


def get_logger(
    name: str = "src2",
    level: LogLevel = LogLevel.INFO,
    log_dir: Optional[Path] = None,
) -> Logger:
    """获取全局日志实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(name=name, level=level, log_dir=log_dir)
    return _global_logger


def set_logger(logger: Logger) -> None:
    """设置全局日志实例"""
    global _global_logger
    _global_logger = logger


def init_logger(
    name: str = "src2",
    level: str = "INFO",
    log_dir: Optional[Path] = None,
) -> Logger:
    """初始化日志"""
    log_level = LogLevel(level) if isinstance(level, str) else level
    logger = get_logger(name=name, level=log_level, log_dir=log_dir)
    set_logger(logger)
    return logger
