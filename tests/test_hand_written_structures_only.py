"""The application code must use our own structures, not the ones that come with Python."""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"
NATIVE_QUEUES = re.compile(r"(from collections import .*deque|import deque|^import queue|^from queue import|import heapq|from heapq import)", re.M)


def test_the_app_imports_no_native_queue_or_heap():
    for path in APP.rglob("*.py"):
        assert not NATIVE_QUEUES.search(path.read_text()), f"{path.relative_to(APP)} imports a native queue"
