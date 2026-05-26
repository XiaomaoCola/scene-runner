from __future__ import annotations

from enum import Enum
from pathlib import Path

import numpy as np
from transitions import Machine

from scene_runner.actuation.actions import Action, TapAction, SwipeAction, SleepAction
from scene_runner.decision.template_matcher import TemplateMatcher

_ROOT = Path(__file__).parents[3]


class Stage(Enum):
    VILLAGE      = "stage1_builder_base"
    ATTACK_MENU  = "stage2_attack_menu"
    BATTLE_SCENE = "stage3_battle_scene"
    SURRENDER_CONFIRM = "stage4_surrender_confirm"
    RETURN_HOME = "stage5_return_home"


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
        self.machine.add_transition("to_surrender_confirm", Stage.BATTLE_SCENE, Stage.SURRENDER_CONFIRM)
        self.machine.add_transition("to_return_home",  Stage.SURRENDER_CONFIRM, Stage.RETURN_HOME)
        self.machine.add_transition("to_village", Stage.RETURN_HOME, Stage.VILLAGE)

        self._matchers: dict[Stage, TemplateMatcher] = {
            Stage.VILLAGE: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage1_builder_base/attack.png",
                region=(0.00, 0.75, 0.15, 1.00),
            ),
            Stage.ATTACK_MENU: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage2_attack_menu/stage2_attack_menu_find_match_region.png",
                region=(0.6385, 0.587, 0.8438, 0.7296),
            ),
            Stage.BATTLE_SCENE: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage3_battle_scene/night_witch.png",
                region=(0.0, 0.8056, 1.0, 1.0),
                mode="search",
            ),
            Stage.SURRENDER_CONFIRM: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage4_surrender_confirm/stage4_surrender_confirm_surrender_confirm_ok_button_region.png",
                region=(0.526, 0.5833, 0.6927, 0.6944),
            ),
            Stage.RETURN_HOME: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage5_return_home/stage5_return_home_return_home_button_region.png",
                region=(0.4427, 0.8102, 0.5599, 0.8796),
            ),
        }

    def step(self, frame_rgb: np.ndarray) -> list[Action] | None:
        matcher = self._matchers.get(self.state)
        if matcher is None:
            raise NotImplementedError(f"[bb_plan|{self.state.name}] 暂无模板，终止循环")

        score = matcher.score(frame_rgb)
        print(f"[bb_plan|{self.state.name}] score={score:.3f}")

        if not matcher.is_match(frame_rgb):
            return None

        if self.state == Stage.VILLAGE:
            self.to_attack_menu()
            return [
                TapAction(region=(0.00, 0.75, 0.15, 1.00)),  # 点击左下角的 Attack 按钮
                SleepAction(duration_seconds=2.0),
            ]

        if self.state == Stage.ATTACK_MENU:
            self.to_battle_scene()
            return [
                TapAction(region=(0.6385, 0.587, 0.8438, 0.7296)),  # 点击 Find Now! 那个按钮
                SleepAction(duration_seconds=2.0),
            ]

        if self.state == Stage.BATTLE_SCENE:
            self.to_surrender_confirm()
            return [
                SwipeAction(from_position=(0.5, 0.8), to_position=(0.05, 0.05), duration_milliseconds=1500),
                SleepAction(duration_seconds=1.5),
                TapAction(region=(0.1578, 0.8657, 0.2214, 0.9204)),   # 选中 night_witch
                SleepAction(duration_seconds=0.5),
                TapAction(region=(0.3385, 0.6296, 0.3542, 0.6389)),   # 在 deployment_zone 里部署 night_witch
                SleepAction(duration_seconds=2.0),
                TapAction(region=(0.0208, 0.6667, 0.125, 0.7222)),    # 点击 surrender_button
                SleepAction(duration_seconds=2.0),
            ]

        if self.state == Stage.SURRENDER_CONFIRM:
            self.to_return_home()
            return [
                TapAction(region=(0.526, 0.5833, 0.6927, 0.6944)),    # 点击 surrender_confirm_ok_button
                SleepAction(duration_seconds=2.0),
            ]

        if self.state == Stage.RETURN_HOME:
            self.to_village()
            return [
                TapAction(region=(0.4427, 0.8102, 0.5599, 0.8796)),   # 点击 return_home_button
                SleepAction(duration_seconds=2.0),
            ]

        return None
