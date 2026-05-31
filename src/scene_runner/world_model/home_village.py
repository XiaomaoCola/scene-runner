from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import time

from scene_runner.world_model.common import Resources, WorkersStatus, LaboratoryStatus


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