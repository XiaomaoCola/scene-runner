from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).parents[3]

# 以后意图多了用枚举。

@dataclass
class BuilderBaseAttackIntent:
    name: str = "builder_base_attack"
    template_path: Path = field(default_factory=lambda: _ROOT / "configs/templates/builder_base/base/attack.png")
    region: tuple = field(default=(0.00, 0.75, 0.15, 1.00))
