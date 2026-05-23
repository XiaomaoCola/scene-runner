from __future__ import annotations

import numpy as np

from scene_runner.perception.sources.capture import FrameSource


class CroppedSource(FrameSource):
    """
    对任意 FrameSource 的输出按标准化坐标裁剪。

    region: (x1, y1, x2, y2)，取值 [0.0, 1.0]
      x 对应宽（列），y 对应高（行）
      例：(0.0, 0.0, 0.5, 0.5) → 左上角四分之一
    """

    def __init__(
        self,
        source: FrameSource,
        *,
        region: tuple[float, float, float, float],
    ) -> None:
        x1, y1, x2, y2 = region
        if not (0.0 <= x1 < x2 <= 1.0 and 0.0 <= y1 < y2 <= 1.0):
            raise ValueError(f"Invalid region {region}: need 0 ≤ x1 < x2 ≤ 1 and 0 ≤ y1 < y2 ≤ 1")
        self._source = source
        self._region = region

    def read(self) -> np.ndarray | None:
        frame = self._source.read()
        if frame is None:
            return None

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = self._region
        cropped = frame[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)]
        return cropped.copy()
