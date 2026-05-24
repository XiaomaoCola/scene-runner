from __future__ import annotations

from enum import Enum

from transitions import Machine

from scene_runner.intents.builder_base_attack import BuilderBaseAttackIntent


class Stage(Enum):
    VILLAGE     = "stage1_builder_base"
    ATTACK_MENU = "stage2_attack_menu"


class BuilderBaseAttackFsm:
    def __init__(self) -> None:
        self.machine = Machine(
            model=self,
            states=Stage,
            initial=Stage.VILLAGE,
            ignore_invalid_triggers=True,
        )
        self.machine.add_transition("to_attack_menu", Stage.VILLAGE,     Stage.ATTACK_MENU)
        self.machine.add_transition("to_village",     Stage.ATTACK_MENU, Stage.VILLAGE)

    def step(self) -> BuilderBaseAttackIntent | None:
        if self.state == Stage.VILLAGE:
            # 留白：资源未满，进攻
            return BuilderBaseAttackIntent()
        if self.state == Stage.ATTACK_MENU:
            # 待实现
            pass
        return None

    def advance(self) -> None:
        """执行层完成动作后调用，推进到下一阶段。"""
        if self.state == Stage.VILLAGE:
            self.to_attack_menu()
