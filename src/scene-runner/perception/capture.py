# 设计原则 ：
# Capture ≠ classifier
# Capture 只负责：给我一帧图像
# 不关心游戏、不关心 FSM、不关心 clicker

# 为什么这样写？
# FrameSource 是教科书级抽象
# ScreenCapture 是具体实现
# 未来可以有：
# WindowCapture
# ADBScreenCapture
# ReplayCapture
# FSM / Classifier / Runner 永远不关心它怎么抓图

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


class FrameSource(ABC):
    """
    Abstract frame source.

    In industrial systems, this is often called:
    - Sensor
    - Observation source
    - Perception input
    """

    @abstractmethod
    def read(self) -> Optional[np.ndarray]:
        """
        Read a frame from the source.

        Returns:
            np.ndarray (H, W, C) in RGB order, or None if unavailable.
        """
        raise NotImplementedError


class ScreenCapture(FrameSource):
    """
    占位用的，随时可删。
    """

    def __init__(self, fps_limit: float = 30.0) -> None:
        self._min_interval = 1.0 / fps_limit
        self._last_ts = 0.0

    def read(self) -> Optional[np.ndarray]:
        now = time.time()
        if now - self._last_ts < self._min_interval:
            return None

        self._last_ts = now

        # NOTE:
        # Here we intentionally do NOT bind to a concrete backend.
        # In project, may plug in:
        # - mss
        # - win32 BitBlt
        # - dxcam
        #
        # For now, we raise to force explicit implementation.
        raise NotImplementedError(
            "ScreenCapture.read() backend not implemented yet."
        )
