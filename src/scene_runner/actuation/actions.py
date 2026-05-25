from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TapAction:
    region: tuple[float, float, float, float]


@dataclass
class SwipeAction:
    from_pos: tuple[float, float]   # 归一化起点 (x, y)
    to_pos: tuple[float, float]     # 归一化终点 (x, y)
    duration_ms: int = 1500


Action = TapAction | SwipeAction
