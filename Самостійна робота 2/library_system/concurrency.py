"""Мультипоточне виконання запитів до системи (ThreadPoolExecutor)."""
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from .exceptions import LibraryError

logger = logging.getLogger("library.threads")


@dataclass
class RequestResult:
    name: str
    ok: bool
    value: Any
    error: str
    thread: str
    elapsed: float


class RequestProcessor:
    """Виконує набір запитів (name, func, args) паралельно.

    latency — імітація затримки (мережа/диск) на кожен запит, секунд."""

    def __init__(self, workers=8, latency=0.0):
        self.workers = workers
        self.latency = latency

    def _run(self, name, func, args):
        start = time.perf_counter()
        thread = threading.current_thread().name
        if self.latency:
            time.sleep(self.latency)
        try:
            value, ok, error = func(*args), True, ""
        except LibraryError as exc:
            value, ok, error = None, False, f"{type(exc).__name__}: {exc}"
        except Exception as exc:  # непередбачена помилка не має зупиняти пул
            logger.exception("Непередбачена помилка у запиті %s", name)
            value, ok, error = None, False, f"Unexpected {type(exc).__name__}: {exc}"
        return RequestResult(name, ok, value, error, thread, time.perf_counter() - start)

    def run_batch(self, requests):
        with ThreadPoolExecutor(max_workers=self.workers,
                                thread_name_prefix="worker") as pool:
            futures = [pool.submit(self._run, n, f, a) for n, f, a in requests]
            return [f.result() for f in futures]

    def run_sequential(self, requests):
        return [self._run(n, f, a) for n, f, a in requests]
