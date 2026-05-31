from __future__ import annotations

from scene_runner.intents.builder_base_attack import BuilderBaseAttackIntent
from scene_runner.world_model.builder_base import BuilderBase


class BuilderBaseFsm:
    # 第二层 FSM：BuilderBase 游戏逻辑
    # 如果资源没满，就去进攻；如果工人闲置，就升级；如果升级没资源，就打架

    def __init__(self, builder_base: BuilderBase) -> None:
        self._builder_base = builder_base

    def step(self) -> BuilderBaseAttackIntent | None:
        resources = self._builder_base.resources

        # 任意一项资源后5位全是零，说明已打满金币或者圣水，暂时不需要进攻
        if resources is not None:
            if resources.gold % 100000 == 0 or resources.elixir % 100000 == 0:
                print(f"[bb_fsm] 资源已满，跳过进攻 金币={resources.gold} 圣水={resources.elixir}")
                return None

        return BuilderBaseAttackIntent()
