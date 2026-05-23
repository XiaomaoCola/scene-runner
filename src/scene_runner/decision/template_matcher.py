from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


class TemplateMatcher:
    """
    裁出指定区域与模板图片做相似度比对，返回是否匹配。
    """

    def __init__(
        self,
        template_path: Path,
        region: tuple[float, float, float, float],
        threshold: float = 0.8,
    ) -> None:
        tamplate = cv2.imread(str(template_path))
        if tamplate is None:
            raise FileNotFoundError(f"模板图片不存在: {template_path}")
        self._template = tamplate  # BGR
        self._region = region
        self._threshold = threshold

    def score(self, frame_rgb: np.ndarray) -> float:
        h, w = frame_rgb.shape[:2]
        x1, y1, x2, y2 = self._region
        crop_bgr = frame_rgb[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w), ::-1]
        crop_resized = cv2.resize(crop_bgr, (self._template.shape[1], self._template.shape[0]))
        result = cv2.matchTemplate(crop_resized, self._template, cv2.TM_CCOEFF_NORMED)
        return float(result[0][0])

    def is_match(self, frame_rgb: np.ndarray) -> bool:
        return self.score(frame_rgb) >= self._threshold
