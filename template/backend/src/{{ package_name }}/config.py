from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    debug: bool
    env: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            debug=os.environ.get("FLASK_DEBUG", "0") == "1",
            env=os.environ.get("FLASK_ENV", "production"),
        )
