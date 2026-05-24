from __future__ import annotations

from scene_runner.intents.builder_base_attack import BuilderBaseAttackIntent


class BuilderBaseFsm:
    # 第二层 FSM：BuilderBase 游戏逻辑
    # 如果资源没满，就去进攻；如果工人闲置，就升级；如果升级没资源，就打架

    def step(self) -> BuilderBaseAttackIntent | None:
        # 留白：资源未满，进攻
        return BuilderBaseAttackIntent()
