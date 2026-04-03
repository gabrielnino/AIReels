import logging
import os
import sys
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")


def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger that writes structured step-by-step logs
    to both the console (INFO) and a rotating log file (DEBUG).

    Usage:
        from utils.logger import get_logger
        log = get_logger(__name__)
        log.step("function_name", "IN",  param1=value1, param2=value2)
        log.step("function_name", "OUT", result=value)
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)

    # ── Console handler: INFO and above ──────────────────────────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(_ColorFormatter())
    logger.addHandler(console)

    # ── File handler: DEBUG and above (full detail) ───────────────────────────
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(file_handler)
    logger.propagate = False

    # Attach .step() helper directly to the logger instance
    def step(fn: str, direction: str, **kwargs):
        """
        Logs a structured IN/OUT step.
        direction: "IN" | "OUT" | "ERR" | "INFO"
        """
        icon = {"IN": "→", "OUT": "←", "ERR": "✗", "INFO": "•"}.get(direction, "·")
        parts = ", ".join(f"{k}={_truncate(v)}" for k, v in kwargs.items())
        msg = f"{icon} {fn}() [{direction}]  {parts}"
        if direction == "ERR":
            logger.error(msg)
        elif direction == "OUT":
            logger.info(msg)
        else:
            logger.info(msg)
        # Always write full values to file at DEBUG level
        full = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
        logger.debug(f"{icon} {fn}() [{direction}] FULL  {full}")

    logger.step = step
    return logger


def _truncate(value, max_len: int = 120) -> str:
    """Truncates long values for console display."""
    s = repr(value)
    return s[:max_len] + "…" if len(s) > max_len else s


class _ColorFormatter(logging.Formatter):
    """Adds color and clean formatting to console output."""
    GREY   = "\x1b[38;5;245m"
    BLUE   = "\x1b[38;5;39m"
    GREEN  = "\x1b[38;5;82m"
    YELLOW = "\x1b[38;5;220m"
    RED    = "\x1b[38;5;196m"
    RESET  = "\x1b[0m"
    BOLD   = "\x1b[1m"

    LEVEL_COLORS = {
        logging.DEBUG:    GREY,
        logging.INFO:     GREEN,
        logging.WARNING:  YELLOW,
        logging.ERROR:    RED,
        logging.CRITICAL: RED + BOLD,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        name_short = record.name.split(".")[-1]
        ts = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        return f"{self.GREY}{ts}{self.RESET} {color}[{name_short}]{self.RESET} {record.getMessage()}"
