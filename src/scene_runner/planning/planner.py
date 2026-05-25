from __future__ import annotations

import numpy as np

from scene_runner.actuation.actions import Action
from scene_runner.intents.builder_base_attack import BuilderBaseAttackIntent
from scene_runner.planning.builder_base_attack import BuilderBaseAttackPlan


class Planner:
    """
    接收 Intent，路由到对应的执行计划，返回执行动作。
    """

    def __init__(self) -> None:
        self._bb_attack = BuilderBaseAttackPlan()

    def step(
        self,
        frame_rgb: np.ndarray,
        intent,
    ) -> Action | None:
        if isinstance(intent, BuilderBaseAttackIntent):
            return self._bb_attack.step(frame_rgb)
        return None
