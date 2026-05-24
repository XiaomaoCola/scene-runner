from __future__ import annotations

import numpy as np

from scene_runner.decision.states.builder_base_attack import BuilderBaseAttackFsm


class Fsm:
    """
    顶层决策协调器：将当前帧分发给各子状态机，返回第一个非 None 的 Intent。

    后面的计划是，顶层状态机负责判定目前村庄状态，就是world model里面那些村庄属性，
    比如判断出现在在homevillage里，并且资源不足，就开始打架，分发任务给子状态机。
    """

    def __init__(self) -> None:
        self._bb_attack = BuilderBaseAttackFsm()

    def decide(self, frame_rgb: np.ndarray):
        # 留白：判定为在 BuilderBase，未来做模板匹配判断世界
        return self._bb_attack.step()

    def advance(self) -> None:
        """执行层完成动作后调用，通知子状态机推进状态。"""
        self._bb_attack.advance()
