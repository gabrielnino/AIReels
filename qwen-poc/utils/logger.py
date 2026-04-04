import logging
import os
import shutil
import sys
from datetime import datetime

# _file_handler is shared across all loggers in the same process so every
# module writes to the *same* run log file.
_file_handler: logging.FileHandler | None = None

_LOG_FORMATTER = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_FALLBACK_LOG = os.path.join("outputs", "pipeline.log")


def _get_file_handler() -> logging.FileHandler:
    """
    Returns (and lazily creates) the single shared FileHandler for this run.
    The log file is placed inside the timestamped run directory managed by
    `utils.run_context`.  If the run directory is not initialised yet the
    handler falls back to `outputs/pipeline.log` so early bootstrap logs are
    never lost.  Call `redirect_log_to_run_dir()` later to move it.
    """
    global _file_handler
    if _file_handler is not None:
        return _file_handler

    try:
        from utils.run_context import get_run_dir
        log_path = os.path.join(get_run_dir(), "pipeline.log")
    except RuntimeError:
        os.makedirs("outputs", exist_ok=True)
        log_path = _FALLBACK_LOG

    _file_handler = logging.FileHandler(log_path, encoding="utf-8")
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(_LOG_FORMATTER)
    return _file_handler


def redirect_log_to_run_dir(run_dir: str) -> None:
    """
    Moves the active log file into *run_dir*/pipeline.log.

    Called by `run_context.init_run()` right after the run directory is
    created so that every log line — including those written during module
    import — ends up in the timestamped folder.

    Steps:
      1. Close the current FileHandler (flushes its buffer).
      2. Copy whatever was already written to the new path.
      3. Swap the handler's stream to the new file (append mode).
      4. Optionally remove the old fallback file.
    """
    global _file_handler
    if _file_handler is None:
        return  # Nothing to redirect yet

    old_path = _file_handler.baseFilename
    new_path = os.path.join(run_dir, "pipeline.log")

    if os.path.abspath(old_path) == os.path.abspath(new_path):
        return  # Already in the right place

    # 1. Close current stream so the file can be read/moved on all OS
    _file_handler.close()

    # 2. Copy accumulated content to the new location
    if os.path.isfile(old_path):
        shutil.copy2(old_path, new_path)

    # 3. Re-open the handler pointing at the new file (append)
    _file_handler.stream = open(new_path, "a", encoding="utf-8")  # noqa: WPS515
    _file_handler.baseFilename = os.path.abspath(new_path)

    # 4. Clean up the old fallback file if it was the placeholder
    if os.path.abspath(old_path) == os.path.abspath(_FALLBACK_LOG):
        try:
            os.remove(old_path)
        except OSError:
            pass


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
    logger.addHandler(_get_file_handler())
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
