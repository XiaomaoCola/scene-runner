"""
Perception（感知层）
定义（教科书）
Transform raw sensory input into structured observations.

实现：
.pt 场景分类模型
predict(frame) -> SceneLabel

典型职责：
Screen capture
Scene / UI recognition
Confidence estimation
"""

from scene_runner.perception.sources.capture import FrameSource, ScreenCapture
from .scene_classifier import SceneClassifier

__all__ = [
    "FrameSource",
    "ScreenCapture",
    "SceneClassifier",
]
