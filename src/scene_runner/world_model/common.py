from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Resources:
    """
    通用资源状态，home_village 和 builder_base 共用。

    dark_elixir 对 builder base 而言始终为 None（夜世界没有黑水）。
    未来描述敌方村庄资源时同样适用。
    """
    gold: int
    elixir: int
    dark_elixir: Optional[int] = None


@dataclass(slots=True)
class WorkersStatus:
    """工人状态"""
    total: int          # 总工人数量
    idle: int           # 空闲工人数量

    @property
    # @property 会把一个"方法"伪装成"属性"，
    # 原来方法是obj.has_idle()，但是用了 @property 后 只要 obj.has_idle 就可以返回 True 或者 False。
    def has_idle(self) -> bool:
        """是否有空闲工人"""
        return self.idle > 0


@dataclass(slots=True)
class LaboratoryStatus:
    """实验室状态"""
    is_researching: bool    # 是否正在研发

    @property
    def is_idle(self) -> bool:
        """实验室是否空闲"""
        return not self.is_researching
