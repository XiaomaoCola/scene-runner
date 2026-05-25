import subprocess

from scene_runner.actuation.actions import Action, TapAction, SwipeAction

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

    def execute(self, action: Action) -> None:
        if isinstance(action, TapAction):
            self._tap_center(action.region)
        elif isinstance(action, SwipeAction):
            self._swipe(action.from_pos, action.to_pos, action.duration_ms)

    def _tap_center(self, region: tuple[float, float, float, float]) -> None:
        x1, y1, x2, y2 = region
        cx = int(((x1 + x2) / 2) * self._w)
        cy = int(((y1 + y2) / 2) * self._h)
        subprocess.run(
            [self._adb, "-s", self._device, "shell", "input", "tap", str(cx), str(cy)],
            capture_output=True,
        )
        print(f"[executor] tap ({cx}, {cy})")

    def _swipe(
        self,
        from_pos: tuple[float, float],
        to_pos: tuple[float, float],
        duration_ms: int,
    ) -> None:
        x1 = int(from_pos[0] * self._w)
        y1 = int(from_pos[1] * self._h)
        x2 = int(to_pos[0] * self._w)
        y2 = int(to_pos[1] * self._h)
        subprocess.run(
            [self._adb, "-s", self._device, "shell", "input", "swipe",
             str(x1), str(y1), str(x2), str(y2), str(duration_ms)],
            capture_output=True,
        )
        print(f"[executor] swipe ({x1},{y1}) → ({x2},{y2}) {duration_ms}ms")
