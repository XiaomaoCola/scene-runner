from __future__ import annotations

from enum import Enum
from pathlib import Path

import yaml
import numpy as np
from transitions import Machine
from ultralytics import YOLO

from scene_runner.actuation.actions import Action, TapAction, SwipeAction, RandomSleepAction, RandomTapAction
from scene_runner.decision.template_matcher import TemplateMatcher
from scene_runner.world_model.builder_base import BuilderBase

_ROOT = Path(__file__).parents[3]
_MODEL_PATH = _ROOT / "data/models/builder_base/elixir_cart.pt"
_CONFIGS = _ROOT / "configs/intents/BuilderBaseCollectResources"
_TEMPLATES = _ROOT / "data/templates/builder_base/BuilderBaseCollectResourcesPlan"
_CONF_THRESHOLD = 0.7


def _load_regions(yaml_path: Path) -> dict[str, tuple[float, float, float, float]]:
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {
        key: (elem["left"], elem["top"], elem["right"], elem["bottom"])
        for key, elem in data.items()
    }


class Stage(Enum):
    SWIPE_TO_TOP_RIGHT      = "stage1_swipe_to_top_right"
    CLICK_ELIXIR_CART       = "stage2_click_elixir_cart"
    COLLECT_AND_RETURN_HOME = "stage3_collect_and_return_home"
    UNKNOWN                 = "unknown"


class BuilderBaseCollectResourcesPlan:
    """BuilderBaseCollectResourcesIntent 的执行计划：移动视角到右上角，点击所有圣水推车。"""

    def __init__(self, builder_base: BuilderBase) -> None:
        self._builder_base = builder_base
        self._model = YOLO(str(_MODEL_PATH))

        self._stage3_regions = _load_regions(_CONFIGS / "stage3_collect_and_return_home.yaml")

        self._stage3_matcher = TemplateMatcher(
            template_path=_TEMPLATES / "stage3_collect_and_return_home_collect_button_region.png",
            region=self._stage3_regions["collect_button"],
        )

        self.machine = Machine(
            model=self,
            states=Stage,
            initial=Stage.SWIPE_TO_TOP_RIGHT,
            ignore_invalid_triggers=True,
        )
        self.machine.add_transition("to_click_elixir_cart",       Stage.SWIPE_TO_TOP_RIGHT,      Stage.CLICK_ELIXIR_CART)
        self.machine.add_transition("to_collect_and_return_home", Stage.CLICK_ELIXIR_CART,       Stage.COLLECT_AND_RETURN_HOME)
        self.machine.add_transition("to_swipe_to_top_right",      Stage.COLLECT_AND_RETURN_HOME, Stage.SWIPE_TO_TOP_RIGHT)
        self.machine.add_transition("to_unknown",                 "*",                           Stage.UNKNOWN)

    def step(self, frame_rgb: np.ndarray) -> list[Action] | None:
        if self.state == Stage.SWIPE_TO_TOP_RIGHT:
            self.to_click_elixir_cart()
            return [
                SwipeAction(from_position=(0.5, 0.2), to_position=(0.05, 0.95), duration_milliseconds=1500),
                RandomSleepAction(minimum_seconds=1.0, maximum_seconds=2.0),
            ]

        if self.state == Stage.CLICK_ELIXIR_CART:
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

            print(f"[bb_collect|CLICK_ELIXIR_CART] 检测到 {cart_count} 个圣水推车")
            self.to_collect_and_return_home()
            return actions if actions else None

        if self.state == Stage.COLLECT_AND_RETURN_HOME:
            score = self._stage3_matcher.score(frame_rgb)
            print(f"[bb_collect|COLLECT_AND_RETURN_HOME] collect_button score={score:.3f}")
            if not self._stage3_matcher.is_match(frame_rgb):
                return None

            self._builder_base.loop_count += 1
            print(f"[bb_collect|COLLECT_AND_RETURN_HOME] 循环完成，累计 {self._builder_base.loop_count} 次")
            self.to_swipe_to_top_right()
            return [
                RandomTapAction(region=self._stage3_regions["collect_button"]),
                RandomSleepAction(minimum_seconds=0.75, maximum_seconds=1.5),
                RandomTapAction(region=self._stage3_regions["close_window_button"]),
            ]

        return None
