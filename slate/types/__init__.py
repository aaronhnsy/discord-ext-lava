# Future
from __future__ import annotations

# Standard Library
from collections.abc import Callable
from typing import Any


JSONDumps = Callable[..., str]
JSONLoads = Callable[..., dict[str, Any]]
