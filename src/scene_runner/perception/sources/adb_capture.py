from __future__ import annotations

import subprocess
import time

import cv2
import numpy as np

from scene_runner.perception.sources.capture import FrameSource

_DEFAULT_ADB = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"
_DEFAULT_DEVICE = "127.0.0.1:5555"


class AdbCapture(FrameSource):
    """
    通过 ADB screencap 截取 Android 设备屏幕。

    在 Android 层面截图，完全不依赖 Windows 窗口状态，
    BlueStacks 最小化、后台、被遮挡均可正常工作。

    注意：adb screencap 每帧约 300-500ms，fps_limit 建议不超过 3。
    """

    def __init__(
        self,
        *,
        adb_path: str = _DEFAULT_ADB,
        device: str = _DEFAULT_DEVICE,
        fps_limit: float = 3.0,
    ) -> None:
        self._adb = adb_path
        self._device = device
        self._min_interval = 1.0 / float(fps_limit)
        self._last_ts = 0.0

    def read(self) -> np.ndarray | None:
        now = time.time()
        if now - self._last_ts < self._min_interval:
            return None
        self._last_ts = now

        result = subprocess.run(
            [self._adb, "-s", self._device, "exec-out", "screencap", "-p"],
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"adb screencap failed: {result.stderr.decode(errors='replace')}"
            )

        img_array = np.frombuffer(result.stdout, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # BGR
        if frame is None:
            raise RuntimeError("cv2.imdecode failed: adb 返回的 PNG 无效")

        return frame[:, :, ::-1].copy()  # BGR → RGB
