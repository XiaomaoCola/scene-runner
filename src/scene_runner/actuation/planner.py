from __future__ import annotations

import numpy as np

from scene_runner.decision.template_matcher import TemplateMatcher


class Planner:
    """
    接收 Intent 和当前帧，做模板匹配确认目标 UI 元素可见，
    返回点击区域；未找到则返回 None。
    """

    def plan(
        self,
        frame_rgb: np.ndarray,
        intent,
    ) -> tuple[float, float, float, float] | None:
        if not hasattr(intent, "template_path") or not hasattr(intent, "region"):
            return None
        matcher = TemplateMatcher(
            template_path=intent.template_path,
            region=intent.region,
        )
        score = matcher.score(frame_rgb)
        print(f"[planner|{intent.name}] score={score:.3f}")
        if matcher.is_match(frame_rgb):
            return intent.region
        return None
