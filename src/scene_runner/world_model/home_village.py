from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import time


@dataclass(slots=True)
class Resources:
    """
    目前描述 主村庄资源状态，
    不过这里是可以解耦的，因为未来进攻的时候，也是可以描述敌方村庄有多少资源。

    为了未来可以解耦 描述夜世界 的资源状态（夜世界村庄没有黑水）， 把黑水改成可以为 None 。
    """
    gold: int                           # 金币数量
    elixir: int                         # 圣水数量  
    dark_elixir: Optional[int] = None   # 黑水数量（夜世界没有黑水）


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


@dataclass(slots=True) 
class HomeVillage:
    """
    部落冲突家乡村庄状态
    
    包含家乡村庄的具体状态信息，区别于夜世界
    """
    # 场景
    scene: str
    
    # 游戏状态
    resources: Optional[Resources]
    workers: Optional[WorkersStatus]
    laboratory: Optional[LaboratoryStatus]
    
    # 元数据
    timestamp: float
    confidence: float = 1.0

    @classmethod
    def now(
        cls,
        *,
        scene: str,
        resources: Optional[Resources] = None,
        workers: Optional[WorkersStatus] = None,
        laboratory: Optional[LaboratoryStatus] = None,
        confidence: float = 1.0,
    ) -> "HomeVillage":
        """创建带当前时间戳的家乡村庄状态"""
        return cls(
            scene=scene,
            resources=resources,
            workers=workers,
            laboratory=laboratory,
            timestamp=time.time(),
            confidence=confidence,
        )

    @property
    def can_build(self) -> bool:
        """
        这只是个示例
        是否可以进行建造（有空闲工人且有金币）
        """
        return (
            self.workers is not None 
            and self.workers.has_idle 
            and self.resources is not None 
            and self.resources.gold > 0
        )
    
    @property
    def can_research(self) -> bool:
        """
        这只是个示例
        是否可以进行研发（实验室空闲且有资源）
        """
        return (
            self.laboratory is not None
            and self.laboratory.is_idle
            and self.resources is not None
            and (self.resources.elixir > 0 or (self.resources.dark_elixir or 0) > 0)
        )
    
    @property
    def need_collect_resources(self) -> bool:
        """
        这只是个示例
        是否需要收集资源（简单判断，可扩展）
        """
        # 这里可以加入更复杂的逻辑，比如资源建筑是否满了
        return True