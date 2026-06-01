from __future__ import annotations

from enum import Enum
from pathlib import Path

import random

import yaml
import numpy as np
from transitions import Machine

from scene_runner.actuation.actions import Action, TapAction, SwipeAction, RandomSleepAction, RandomTapAction
from scene_runner.decision.template_matcher import TemplateMatcher
from scene_runner.perception.processors.resource_extractor import ResourceExtractor
from scene_runner.world_model.builder_base import BuilderBase

_ROOT = Path(__file__).parents[3]
_CONFIGS = _ROOT / "configs/intents/BuilderBaseAttack"

_FAILURE_THRESHOLD = 8  # 连续失败超过此次数后进入 UNKNOWN 状态


def _load_regions(yaml_path: Path) -> dict[str, tuple[float, float, float, float]]:
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {
        key: (elem["left"], elem["top"], elem["right"], elem["bottom"])
        for key, elem in data.items()
    }


class Stage(Enum):
    VILLAGE           = "stage1_builder_base"
    ATTACK_MENU       = "stage2_attack_menu"
    BATTLE_SCENE      = "stage3_battle_scene"
    SURRENDER_CONFIRM = "stage4_surrender_confirm"
    RETURN_HOME       = "stage5_return_home"
    UNKNOWN           = "unknown"


# UNKNOWN 恢复到各 stage 的 trigger 名称映射
_RECOVERY_TRIGGERS: dict[Stage, str] = {
    Stage.VILLAGE:           "recover_to_village",
    Stage.ATTACK_MENU:       "recover_to_attack_menu",
    Stage.BATTLE_SCENE:      "recover_to_battle_scene",
    Stage.SURRENDER_CONFIRM: "recover_to_surrender_confirm",
    Stage.RETURN_HOME:       "recover_to_return_home",
}


class BuilderBaseAttackPlan:
    """
    BuilderBaseAttackIntent 的 UI 执行计划。
    追踪当前处于哪个 UI 阶段，做模板匹配，返回需要点击的区域。
    """

    def __init__(self, builder_base: BuilderBase) -> None:
        self._resource_extractor = ResourceExtractor()
        self._builder_base = builder_base

        with open(_CONFIGS / "stage1_builder_base.yaml", encoding="utf-8") as f:
            self._stage1_raw_config = yaml.safe_load(f)
        self._stage1_builder_base_regions = {
            key: (elem["left"], elem["top"], elem["right"], elem["bottom"])
            for key, elem in self._stage1_raw_config.items()
        }
        self._stage2_attack_menu_regions       = _load_regions(_CONFIGS / "stage2_attack_menu.yaml")
        self._stage3_battle_scene_regions      = _load_regions(_CONFIGS / "stage3_battle_scene.yaml")
        self._stage4_surrender_confirm_regions = _load_regions(_CONFIGS / "stage4_surrender_confirm.yaml")
        self._stage5_return_home_regions       = _load_regions(_CONFIGS / "stage5_return_home.yaml")

        self._consecutive_failures = 0

        self.machine = Machine(
            model=self,
            states=Stage,
            initial=Stage.VILLAGE,
            ignore_invalid_triggers=True,
        )
        self.machine.add_transition("to_attack_menu",       Stage.VILLAGE,           Stage.ATTACK_MENU)
        self.machine.add_transition("to_battle_scene",      Stage.ATTACK_MENU,       Stage.BATTLE_SCENE)
        self.machine.add_transition("to_surrender_confirm", Stage.BATTLE_SCENE,      Stage.SURRENDER_CONFIRM)
        self.machine.add_transition("to_return_home",       Stage.SURRENDER_CONFIRM, Stage.RETURN_HOME)
        self.machine.add_transition("to_village",           Stage.RETURN_HOME,       Stage.VILLAGE)
        self.machine.add_transition("to_unknown",           "*",                     Stage.UNKNOWN)
        self.machine.add_transition("recover_to_village",           Stage.UNKNOWN, Stage.VILLAGE)
        self.machine.add_transition("recover_to_attack_menu",       Stage.UNKNOWN, Stage.ATTACK_MENU)
        self.machine.add_transition("recover_to_battle_scene",      Stage.UNKNOWN, Stage.BATTLE_SCENE)
        self.machine.add_transition("recover_to_surrender_confirm", Stage.UNKNOWN, Stage.SURRENDER_CONFIRM)
        self.machine.add_transition("recover_to_return_home",       Stage.UNKNOWN, Stage.RETURN_HOME)

        self._matchers: dict[Stage, TemplateMatcher] = {
            Stage.VILLAGE: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage1_builder_base/stage1_builder_base_army_training_button_region.png",
                region=self._stage1_builder_base_regions["army_training_button"],
            ),
            Stage.ATTACK_MENU: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage2_attack_menu/stage2_attack_menu_find_match_region.png",
                region=self._stage2_attack_menu_regions["find_match"],
            ),
            Stage.BATTLE_SCENE: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage3_battle_scene/night_witch.png",
                region=self._stage3_battle_scene_regions["troop_bar"],
                mode="search",
            ),
            Stage.SURRENDER_CONFIRM: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage4_surrender_confirm/stage4_surrender_confirm_surrender_confirm_ok_button_region.png",
                region=self._stage4_surrender_confirm_regions["surrender_confirm_ok_button"],
            ),
            Stage.RETURN_HOME: TemplateMatcher(
                template_path=_ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage5_return_home/stage5_return_home_return_home_button_region.png",
                region=self._stage5_return_home_regions["return_home_button"],
            ),
        }

        _stage3_tmpl = _ROOT / "data/templates/builder_base/BuilderBaseAttackIntent/stage3_battle_scene"
        self._hero_matchers: list[TemplateMatcher] = [
            TemplateMatcher(
                template_path=_stage3_tmpl / "stage3_battle_scene_battle_machine_region.png",
                region=self._stage3_battle_scene_regions["hero"],
                threshold=0.65,
            ),
            TemplateMatcher(
                template_path=_stage3_tmpl / "stage3_battle_scene_battle_copter_region.png",
                region=self._stage3_battle_scene_regions["hero"],
                threshold=0.65,
            ),
        ]

    def _recover(self, frame_rgb: np.ndarray) -> None:
        best_stage: Stage | None = None
        best_score = 0.0
        for stage, matcher in self._matchers.items():
            score = matcher.score(frame_rgb)
            print(f"[bb_plan|UNKNOWN] scanning {stage.name}: score={score:.3f}")
            if score > best_score:
                best_score = score
                best_stage = stage

        if best_stage is not None and self._matchers[best_stage].is_match(frame_rgb):
            print(f"[bb_plan|UNKNOWN] → 恢复至 {best_stage.name}")
            getattr(self, _RECOVERY_TRIGGERS[best_stage])()
            self._consecutive_failures = 0
        else:
            print("[bb_plan|UNKNOWN] 无法识别当前界面，继续等待")

    def step(self, frame_rgb: np.ndarray) -> list[Action] | None:
        if self.state == Stage.UNKNOWN:
            self._recover(frame_rgb)
            return None

        matcher = self._matchers.get(self.state)
        if matcher is None:
            raise NotImplementedError(f"[bb_plan|{self.state.name}] 暂无模板，终止循环")

        score = matcher.score(frame_rgb)
        print(f"[bb_plan|{self.state.name}] score={score:.3f}")

        if not matcher.is_match(frame_rgb):
            self._consecutive_failures += 1
            if self._consecutive_failures >= _FAILURE_THRESHOLD:
                print(f"[bb_plan|{self.state.name}] 连续失败 {self._consecutive_failures} 次，进入 UNKNOWN")
                self.to_unknown()
                self._consecutive_failures = 0
            return None

        self._consecutive_failures = 0

        if self.state == Stage.VILLAGE:
            resources = self._resource_extractor.extract(frame_rgb, self._stage1_raw_config)
            if resources is not None:
                self._builder_base.resources = resources
                print(f"[bb_plan|VILLAGE] 金币={resources.gold}  圣水={resources.elixir}")
            else:
                print(f"[bb_plan|VILLAGE] 资源识别失败，保留上次值 金币={self._builder_base.resources and self._builder_base.resources.gold}  圣水={self._builder_base.resources and self._builder_base.resources.elixir}")
            self.to_attack_menu()
            return [
                TapAction(region=self._stage1_builder_base_regions["attack_button"]),  # 点击左下角的 Attack 按钮
                RandomSleepAction(minimum_seconds=1.5, maximum_seconds=2.5),
            ]

        if self.state == Stage.ATTACK_MENU:
            self.to_battle_scene()
            return [
                TapAction(region=self._stage2_attack_menu_regions["find_match"]),  # 点击 Find Now! 那个按钮
                RandomSleepAction(minimum_seconds=3.0, maximum_seconds=3.5),
            ]

        if self.state == Stage.BATTLE_SCENE:
            self.to_surrender_confirm()
            hero_scores = [m.score(frame_rgb) for m in self._hero_matchers]
            has_hero = any(m.is_match(frame_rgb) for m in self._hero_matchers)
            print(f"[bb_plan|BATTLE_SCENE] 英雄检测 battle_machine={hero_scores[0]:.3f} battle_copter={hero_scores[1]:.3f} → {'有' if has_hero else '无'}")

            actions: list[Action] = [
                SwipeAction(from_position=(0.5, 0.8), to_position=(0.05, 0.05), duration_milliseconds=1500),
                # 滑动到战斗界面的村庄的右下角，用于对齐坐标
                RandomSleepAction(minimum_seconds=1.0, maximum_seconds=2.0),
            ]

            # 如果 has_hero， 那么就点击英雄并部署到 2，3，4 区域里。
            if has_hero:
                actions.append(RandomTapAction(region=self._stage3_battle_scene_regions["hero"]))  # 选中英雄
                actions.append(RandomSleepAction(minimum_seconds=0.2, maximum_seconds=0.5))
                for zone_key in ["deployment_zone_2", "deployment_zone_3", "deployment_zone_4"]:
                    for _ in range(random.randint(1, 2)):
                        actions.append(RandomTapAction(region=self._stage3_battle_scene_regions[zone_key]))
                        actions.append(RandomSleepAction(minimum_seconds=0.1, maximum_seconds=0.3))
                actions.append(RandomSleepAction(minimum_seconds=0.5, maximum_seconds=1.0))

            actions += [
                TapAction(region=self._stage3_battle_scene_regions["night_witch"]),  # 选中 night_witch
                RandomSleepAction(minimum_seconds=0.2, maximum_seconds=1.0),
            ]

            for zone_key in ["deployment_zone_2", "deployment_zone_3", "deployment_zone_4"]:
                for _ in range(random.randint(2, 5)):
                    actions.append(RandomTapAction(region=self._stage3_battle_scene_regions[zone_key]))
                    actions.append(RandomSleepAction(minimum_seconds=0.1, maximum_seconds=0.3))

            actions += [
                RandomSleepAction(minimum_seconds=30, maximum_seconds=50),
                # 等待军队进攻的时间，时间到了之后会直接投降
                TapAction(region=self._stage3_battle_scene_regions["surrender_button"]),  # 点击 surrender_button
                RandomSleepAction(minimum_seconds=1.5, maximum_seconds=2.5),
            ]
            return actions

        if self.state == Stage.SURRENDER_CONFIRM:
            self.to_return_home()
            return [
                TapAction(region=self._stage4_surrender_confirm_regions["surrender_confirm_ok_button"]),  # 点击 surrender_confirm_ok_button
                RandomSleepAction(minimum_seconds=2.5, maximum_seconds=3.0),
            ]

        if self.state == Stage.RETURN_HOME:
            self.to_village()
            return [
                TapAction(region=self._stage5_return_home_regions["return_home_button"]),  # 点击 return_home_button
                RandomSleepAction(minimum_seconds=1.5, maximum_seconds=2.5),
            ]

        return None
