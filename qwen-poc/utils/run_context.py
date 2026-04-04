"""
run_context.py
==============
Singleton that holds the output directory for the **current pipeline run**.

The directory is created the first time `init_run()` is called and has the form:

    outputs/run_YYYYMMDD_HHMMSS/

All images, videos, and the log file for this run are placed inside it.
Subsequent calls to `init_run()` are no-ops so the path stays stable for the
whole lifetime of a single `python pipeline.py` execution.
"""

import os
from datetime import datetime

_run_dir: str | None = None


def init_run(base_dir: str = "outputs") -> str:
    """
    Creates the timestamped run directory and returns its path.
    Safe to call multiple times — only the first call actually creates it.

    Also redirects the shared log FileHandler into the new directory so that
    every log line (including those written during module import) ends up in
    the timestamped folder.
    """
    global _run_dir
    if _run_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        _run_dir = os.path.join(base_dir, f"run_{timestamp}")
        os.makedirs(_run_dir, exist_ok=True)

        # Move the log file into the run directory (no-op if logger not yet used)
        from utils.logger import redirect_log_to_run_dir
        redirect_log_to_run_dir(_run_dir)

    return _run_dir


def get_run_dir() -> str:
    """
    Returns the current run directory.
    Raises RuntimeError if `init_run()` has not been called yet.
    """
    if _run_dir is None:
        raise RuntimeError(
            "Run directory not initialised. Call `init_run()` before using `get_run_dir()`."
        )
    return _run_dir
