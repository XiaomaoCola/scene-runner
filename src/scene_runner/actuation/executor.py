import random
import subprocess
import time

from scene_runner.actuation.actions import Action, TapAction, SwipeAction, SleepAction, RandomSleepAction, RandomTapAction

_DEFAULT_ADB = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"
_DEFAULT_DEVICE = "127.0.0.1:5555"


class Executor:
    def __init__(
        self,
        screen_size: tuple[int, int],  # (width, height) 从 AdbCapture 第一帧读取
        adb_path: str = _DEFAULT_ADB,
        device: str = _DEFAULT_DEVICE,
    ) -> None:
        self._w, self._h = screen_size
        self._adb = adb_path
        self._device = device

    def execute(self, actions: list[Action]) -> None:
        for action in actions:
            if isinstance(action, TapAction):
                self._tap_center(action.region)
            elif isinstance(action, SwipeAction):
                self._swipe(action.from_position, action.to_position, action.duration_milliseconds)
            elif isinstance(action, SleepAction):
                print(f"[executor] sleep {action.duration_seconds}s")
                time.sleep(action.duration_seconds)
            elif isinstance(action, RandomSleepAction):
                duration = random.uniform(action.minimum_seconds, action.maximum_seconds)
                print(f"[executor] random sleep {duration:.2f}s (range {action.minimum_seconds}~{action.maximum_seconds}s)")
                time.sleep(duration)
            elif isinstance(action, RandomTapAction):
                self._random_tap(action.region)

    def _tap_center(self, region: tuple[float, float, float, float]) -> None:
        x1, y1, x2, y2 = region
        cx = int(((x1 + x2) / 2) * self._w)
        cy = int(((y1 + y2) / 2) * self._h)
        subprocess.run(
            [self._adb, "-s", self._device, "shell", "input", "tap", str(cx), str(cy)],
            capture_output=True,
        )
        print(f"[executor] tap ({cx}, {cy})")

    def _random_tap(self, region: tuple[float, float, float, float]) -> None:
        x1, y1, x2, y2 = region
        cx = int(random.uniform(x1, x2) * self._w)
        cy = int(random.uniform(y1, y2) * self._h)
        subprocess.run(
            [self._adb, "-s", self._device, "shell", "input", "tap", str(cx), str(cy)],
            capture_output=True,
        )
        print(f"[executor] random tap ({cx}, {cy})")

    def _swipe(
        self,
        from_position: tuple[float, float],
        to_position: tuple[float, float],
        duration_milliseconds: int,
    ) -> None:
        x1 = int(from_position[0] * self._w)
        y1 = int(from_position[1] * self._h)
        x2 = int(to_position[0] * self._w)
        y2 = int(to_position[1] * self._h)
        subprocess.run(
            [self._adb, "-s", self._device, "shell", "input", "swipe",
             str(x1), str(y1), str(x2), str(y2), str(duration_milliseconds)],
            capture_output=True,
        )
        print(f"[executor] swipe ({x1},{y1}) → ({x2},{y2}) {duration_milliseconds}ms")
