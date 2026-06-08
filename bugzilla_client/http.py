from __future__ import annotations

from typing import Any, Callable

import requests

Fetch = Callable[[str, int], Any]


def default_fetch(url: str, timeout: int = 30) -> Any:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()
