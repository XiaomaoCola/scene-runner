import subprocess

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

    def execute(self, intent) -> None:
        if not hasattr(intent, "region"):
            return
        self._tap_center(intent.region)

    def _tap_center(self, region: tuple[float, float, float, float]) -> None:
        x1, y1, x2, y2 = region
        cx = int(((x1 + x2) / 2) * self._w)
        cy = int(((y1 + y2) / 2) * self._h)
        subprocess.run(
            [self._adb, "-s", self._device, "shell", "input", "tap", str(cx), str(cy)],
            capture_output=True,
        )
        print(f"[executor] tap ({cx}, {cy})")
