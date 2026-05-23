# Observation = 世界在“这一刻”的可观测事实

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import time


@dataclass(slots=True)
class Observation:
    """
    Observation produced by the perception layer.

    This is a textbook concept:
    - Robotics
    - POMDP
    - Game AI
    """

    scene: str                  # Scene label from classifier
    confidence: float            # Confidence of the scene prediction
    timestamp: float             # Time when observation is generated

    # Optional extensible fields
    features: Dict[str, Any] = None

    @classmethod
    def now(
        cls,
        *,
        scene: str,
        confidence: float,
        features: Dict[str, Any] | None = None,
    ) -> "Observation":
        return cls(
            scene=scene,
            confidence=confidence,
            timestamp=time.time(),
            features=features or {},
        )
