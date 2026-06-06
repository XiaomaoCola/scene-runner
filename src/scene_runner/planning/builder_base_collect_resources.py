from __future__ import annotations

from enum import Enum
from pathlib import Path

import numpy as np
from ultralytics import YOLO

from scene_runner.actuation.actions import Action, TapAction, SwipeAction, RandomSleepAction
from scene_runner.world_model.builder_base import BuilderBase

_ROOT = Path(__file__).parents[3]
_MODEL_PATH = _ROOT / "data/models/builder_base/elixir_cart.pt"
_CONF_THRESHOLD = 0.7


class _Stage(Enum):
    PANNING     = "panning"
    COLLECTING  = "collecting"


class BuilderBaseCollectResourcesPlan:
    """BuilderBaseCollectResourcesIntent 的执行计划：移动视角到右上角，点击所有圣水推车。"""

    def __init__(self, builder_base: BuilderBase) -> None:
        self._builder_base = builder_base
        self._model = YOLO(str(_MODEL_PATH))
        self._stage = _Stage.PANNING

    def step(self, frame_rgb: np.ndarray) -> list[Action] | None:
        if self._stage == _Stage.PANNING:
            self._stage = _Stage.COLLECTING
            return [
                SwipeAction(from_position=(0.5, 0.2), to_position=(0.05, 0.95), duration_milliseconds=1500),
                RandomSleepAction(minimum_seconds=1.0, maximum_seconds=2.0),
            ]

        if self._stage == _Stage.COLLECTING:
            h, w = frame_rgb.shape[:2]
            results = self._model(frame_rgb, conf=_CONF_THRESHOLD, verbose=False)
            boxes = results[0].boxes

            actions: list[Action] = []
            cart_count = 0
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    cls_name = self._model.names[int(box.cls.item())]
                    if cls_name != "elixir_cart":
                        continue
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    region = (x1 / w, y1 / h, x2 / w, y2 / h)
                    actions.append(TapAction(region=region))
                    actions.append(RandomSleepAction(minimum_seconds=0.3, maximum_seconds=0.8))
                    cart_count += 1

            self._stage = _Stage.PANNING
            self._builder_base.loop_count += 1
            print(f"[bb_collect] 检测到 {cart_count} 个圣水推车，循环完成，累计 {self._builder_base.loop_count} 次")
            return actions if actions else None

        return None
