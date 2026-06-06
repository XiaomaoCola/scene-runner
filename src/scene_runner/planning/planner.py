from __future__ import annotations

import numpy as np

from scene_runner.actuation.actions import Action
from scene_runner.intents.builder_base_attack import BuilderBaseAttackIntent
from scene_runner.intents.builder_base_collect_resources import BuilderBaseCollectResourcesIntent
from scene_runner.planning.builder_base_attack import BuilderBaseAttackPlan
from scene_runner.planning.builder_base_collect_resources import BuilderBaseCollectResourcesPlan
from scene_runner.world_model.builder_base import BuilderBase


class Planner:
    """
    接收 Intent，路由到对应的执行计划，返回执行动作。
    """

    def __init__(self, builder_base: BuilderBase) -> None:
        self._bb_attack = BuilderBaseAttackPlan(builder_base)
        self._bb_collect = BuilderBaseCollectResourcesPlan(builder_base)

    def step(
        self,
        frame_rgb: np.ndarray,
        intent,
    ) -> list[Action] | None:
        if isinstance(intent, BuilderBaseAttackIntent):
            return self._bb_attack.step(frame_rgb)
        if isinstance(intent, BuilderBaseCollectResourcesIntent):
            return self._bb_collect.step(frame_rgb)
        return None
