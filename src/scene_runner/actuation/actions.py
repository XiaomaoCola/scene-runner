from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TapAction:
    """点击 region 中心一次，对应 adb input tap。"""
    region: tuple[float, float, float, float]


@dataclass
class SwipeAction:
    """从 from_position 按住滑向 to_position，对应 adb input swipe，用于拖动地图或滚动列表。"""
    from_position: tuple[float, float]
    to_position: tuple[float, float]
    duration_milliseconds: int = 1500


@dataclass
class SleepAction:
    """在两个动作之间等待，给游戏动画或响应留出时间。"""
    duration_seconds: float


@dataclass
class RandomSleepAction:
    """在 minimum_seconds 到 maximum_seconds 之间随机等待，用于模拟人类操作节奏，降低封号风险。"""
    minimum_seconds: float
    maximum_seconds: float


@dataclass
class RandomTapAction:
    """在 region 内随机选取一点点击，避免每次点击同一位置被识别为机器行为。"""
    region: tuple[float, float, float, float]


Action = TapAction | SwipeAction | SleepAction | RandomSleepAction | RandomTapAction
