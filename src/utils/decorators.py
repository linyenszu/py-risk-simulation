"""Reusable decorators for runtime observability."""

from __future__ import annotations

from functools import wraps
from time import perf_counter
from typing import Any, Callable, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def timed(func: F) -> F:
    """Attach elapsed seconds to stdout for lightweight local profiling."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        result = func(*args, **kwargs)
        elapsed = perf_counter() - start
        print(f"{func.__name__} completed in {elapsed:.4f}s")
        return result

    return cast(F, wrapper)
