from __future__ import annotations

import numpy as np

from scene_runner.decision.states.BuilderBaseFsm import BuilderBaseFsm


class Fsm:
    """
    顶层决策协调器：将当前帧 分析一下， 看看现在在 homevillage 还是在 builderbase 。

    后面的计划是，顶层状态机负责识别目前村庄状态，就是world model里面那些村庄属性，
    比如判断出现在在 homevillage 里 ，把村庄数据给 子fsm ， 让子 fsm 分析下面要干什么，
    也就是输出 intent 。
    """

    def __init__(self) -> None:
        self._builder_base_fsm = BuilderBaseFsm()

    def decide(self, frame_rgb: np.ndarray):
        # 留白：判定为在 BuilderBase，未来做模板匹配判断世界
        return self._builder_base_fsm.step()

