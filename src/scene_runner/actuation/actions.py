from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TapAction:
    """点击 region 中心一次，对应 adb input tap。"""
    region: tuple[float, float, float, float]


@dataclass
class SwipeAction:
    """从 from_position 按住滑向 to_position，对应 adb input swipe，用于拖动地图或滚动列表。"""
    from_position: tuple[float, float]   # 归一化起点 (x, y)
    to_position: tuple[float, float]     # 归一化终点 (x, y)
    duration_ms: int = 1500


Action = TapAction | SwipeAction
