from __future__ import annotations

from pathlib import Path

import numpy as np

from scene_runner.decision.template_matcher import TemplateMatcher
from scene_runner.intents.builder_base_attack import BuilderBaseAttackIntent

_ROOT = Path(__file__).parents[3]  # scene-runner 项目根目录


class Fsm:
    """
    判断当前场景，决定输出哪个 Intent。
    """

    def __init__(self) -> None:
        self._builder_base_village = TemplateMatcher(
            template_path=_ROOT / "configs/templates/builder_base/base/attack.png",
            region=(0.00, 0.75, 0.15, 1.00),
        )

    def decide(self, frame_rgb: np.ndarray):
        score = self._builder_base_village.score(frame_rgb)
        print(f"[fsm] builder_base_village score = {score:.3f}")

        if self._builder_base_village.is_match(frame_rgb):
            return BuilderBaseAttackIntent()

        return None
