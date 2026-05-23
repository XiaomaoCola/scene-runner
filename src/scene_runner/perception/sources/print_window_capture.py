from __future__ import annotations

import ctypes
import time

import numpy as np
import win32gui
import win32ui

from scene_runner.perception.capture import FrameSource

# PrintWindow flags
_PW_CLIENTONLY = 1
_PW_RENDERFULLCONTENT = 2  # 捕获 DirectX/硬件加速内容（BlueStacks 必须）


class PrintWindowCapture(FrameSource):
    """
    通过 Win32 PrintWindow API 截取指定窗口的客户区。

    和 mss 方案的本质区别：
      - mss: 读取屏幕上某块区域的像素 → 窗口最小化/被遮挡时拿不到正确内容
      - PrintWindow: 让窗口自己把内容"画"到内存 DC → 不经过屏幕，最小化/后台均可用

    依赖：pywin32（window-finder 已传递依赖，无需单独安装）
    """

    def __init__(self, *, window_keyword: str, fps_limit: float = 30.0) -> None:
        self.window_keyword = window_keyword
        self._min_interval = 1.0 / float(fps_limit)
        self._last_ts = 0.0

    def _find_hwnd(self) -> int:
        """
        枚举所有窗口，按关键词匹配标题。
        故意不过滤 IsWindowVisible，以便找到最小化的窗口。
        """
        matches: list[int] = []
        low_kw = self.window_keyword.lower()

        def handler(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if title and low_kw in title.lower():
                matches.append(hwnd)

        win32gui.EnumWindows(handler, None)

        if not matches:
            raise RuntimeError(f"Window not found for keyword: {self.window_keyword!r}")
        return matches[0]

    def read(self) -> np.ndarray | None:
        now = time.time()
        if now - self._last_ts < self._min_interval:
            return None
        self._last_ts = now

        hwnd = self._find_hwnd()

        # GetClientRect 返回客户区自身坐标 (0, 0, w, h)，最小化时尺寸依然有效
        _, _, w, h = win32gui.GetClientRect(hwnd)
        if w <= 0 or h <= 0:
            raise RuntimeError(
                f"Invalid client rect for '{self.window_keyword}': {w}x{h}. "
                "Window may be fully minimized with no renderable surface."
            )

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bmp)

        try:
            ctypes.windll.user32.PrintWindow(
                hwnd,
                save_dc.GetSafeHdc(),
                _PW_CLIENTONLY | _PW_RENDERFULLCONTENT,
            )
            raw = bmp.GetBitmapBits(True)  # bytes, BGRA 格式，4 bytes/pixel
        finally:
            win32gui.DeleteObject(bmp.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

        # BGRA (h, w, 4) → RGB (h, w, 3)
        img = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)
        rgb = img[:, :, 2::-1].copy()  # 通道 [2,1,0] = [R,G,B]
        return rgb
