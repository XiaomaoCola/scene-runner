from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from scene_runner.world_model.common import Resources


@dataclass(slots=True)
class BuilderBase:
    """夜世界村庄的全局状态，整个运行时唯一实例。"""
    resources: Optional[Resources] = None

    loop_count: int = 0  # 累计完整循环次数（每次返回村庄 +1）
