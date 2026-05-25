from __future__ import annotations

from pathlib import Path
from typing import Literal

import cv2
import numpy as np


class TemplateMatcher:
    """
    裁出指定区域与模板图片做相似度比对，返回是否匹配。

    mode="full"   : 将 crop 缩放至模板尺寸后整体比对（适合整区域截图模板）
    mode="search" : 在 crop 内滑窗搜索模板（适合在大区域里找小图标）
    """

    def __init__(
        self,
        template_path: Path,
        region: tuple[float, float, float, float],
        threshold: float = 0.8,
        mode: Literal["full", "search"] = "full",
    ) -> None:
        template = cv2.imread(str(template_path))
        if template is None:
            raise FileNotFoundError(f"模板图片不存在: {template_path}")
        self._template = template  # BGR
        self._region = region
        self._threshold = threshold
        self._mode = mode

    def score(self, frame_rgb: np.ndarray) -> float:
        h, w = frame_rgb.shape[:2]
        x1, y1, x2, y2 = self._region
        crop_bgr = frame_rgb[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w), ::-1]

        if self._mode == "full":
            crop_resized = cv2.resize(crop_bgr, (self._template.shape[1], self._template.shape[0]))
            result = cv2.matchTemplate(crop_resized, self._template, cv2.TM_CCOEFF_NORMED)
            return float(result[0][0])

        # search 模式：在 crop 内滑窗找模板
        if crop_bgr.shape[0] < self._template.shape[0] or crop_bgr.shape[1] < self._template.shape[1]:
            return 0.0
        result = cv2.matchTemplate(crop_bgr, self._template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return float(max_val)

    def is_match(self, frame_rgb: np.ndarray) -> bool:
        return self.score(frame_rgb) >= self._threshold
