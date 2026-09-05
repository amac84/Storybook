from __future__ import annotations

from functools import lru_cache
from typing import Any

from .io import read_yaml
from .paths import STUDIO_CONFIG


@lru_cache(maxsize=1)
def load_studio() -> dict[str, Any]:
    data = read_yaml(STUDIO_CONFIG)
    if not data:
        raise FileNotFoundError(f"Missing studio config: {STUDIO_CONFIG}")
    return data


def quality_gates() -> dict[str, Any]:
    return dict(load_studio()["quality_gates"])


def studio_meta() -> dict[str, Any]:
    return dict(load_studio()["studio"])
