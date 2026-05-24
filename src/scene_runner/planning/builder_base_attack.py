from __future__ import annotations

from enum import Enum
from pathlib import Path

import numpy as np
from transitions import Machine

from scene_runner.decision.template_matcher import TemplateMatcher

_ROOT = Path(__file__).parents[3]


class Stage(Enum):
    VILLAGE      = "stage1_builder_base"
    ATTACK_MENU  = "stage2_attack_menu"
    BATTLE_SCENE = "stage3_battle_scene"


class BuilderBaseAttackPlan:
    """
    BuilderBaseAttackIntent 的 UI 执行计划。
    追踪当前处于哪个 UI 阶段，做模板匹配，返回需要点击的区域。
    """

    def __init__(self) -> None:
        self.machine = Machine(
            model=self,
            states=Stage,
            initial=Stage.VILLAGE,
            ignore_invalid_triggers=True,
        )
        self.machine.add_transition("to_attack_menu",  Stage.VILLAGE,      Stage.ATTACK_MENU)
        self.machine.add_transition("to_battle_scene", Stage.ATTACK_MENU,  Stage.BATTLE_SCENE)
        self.machine.add_transition("to_village",      Stage.BATTLE_SCENE, Stage.VILLAGE)

        self._matchers: dict[Stage, TemplateMatcher] = {
            Stage.VILLAGE: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/base/attack.png",
                region=(0.00, 0.75, 0.15, 1.00),
            ),
            Stage.ATTACK_MENU: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/attack_menu/stage2_attack_menu_find_match_region.png",
                region=(0.6385, 0.587, 0.8438, 0.7296),
            ),
        }

    def step(self, frame_rgb: np.ndarray) -> tuple[float, float, float, float] | None:
        matcher = self._matchers.get(self.state)
        if matcher is None:
            raise NotImplementedError(f"[bb_plan|{self.state.name}] 暂无模板，终止循环")

        score = matcher.score(frame_rgb)
        print(f"[bb_plan|{self.state.name}] score={score:.3f}")

        if not matcher.is_match(frame_rgb):
            return None

        if self.state == Stage.VILLAGE:
            self.to_attack_menu()
            return (0.00, 0.75, 0.15, 1.00)

        if self.state == Stage.ATTACK_MENU:
            self.to_battle_scene()
            return (0.6385, 0.587, 0.8438, 0.7296)

        return None
