from __future__ import annotations

import numpy as np

from scene_runner.actuation.actions import Action
from scene_runner.world_model.builder_base import BuilderBase


class BuilderBaseCollectResourcesPlan:
    """BuilderBaseCollectResourcesIntent 的执行计划，待实现。"""

    def __init__(self, builder_base: BuilderBase) -> None:
        self._builder_base = builder_base

    def step(self, frame_rgb: np.ndarray) -> list[Action] | None:
        self._builder_base.loop_count += 1
        print(f"[bb_collect] 循环完成，累计 {self._builder_base.loop_count} 次")
        return None
