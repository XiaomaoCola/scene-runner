from scene_runner.perception.geometry import WindowGeometryProvider
from scene_runner.perception.capture import FrameSource
import mss
import numpy as np
import time


class WindowCapture(FrameSource):
    def __init__(self, *, window_keyword: str, geometry: WindowGeometryProvider, fps_limit: float = 30.0) -> None:
        self.window_keyword = window_keyword
        self.geometry = geometry
        self._min_interval = 1.0 / float(fps_limit)
        self._last_ts = 0.0
        self._sct = mss.mss()

    def read(self):
        now = time.time()
        if now - self._last_ts < self._min_interval:
            return None
        self._last_ts = now

        rect = self.geometry.get_client_rect(self.window_keyword)
        shot = self._sct.grab(rect.to_mss_monitor())  # BGRA
        img = np.array(shot, dtype=np.uint8)
        # 这步是把 mss 对象变成 numpy，得到一个img.shape == (height, width, 4)，也就是img[y][x] = [B, G, R, A]。
        bgr = img[:, :, :3]
        # 只取前 3 个通道，即[B, G, R, A]  →  [B, G, R]，Alpha（透明度）被直接丢弃。
        rgb = bgr[:, :, ::-1].copy()
        # 首先看bgr[:, :, ::-1]，这个意思表示的是把最后一个维度反过来，即：[B, G, R]变成[R, G, B]。
        # .copy()是为了强制生成一块干净、连续、独立的 RGB ndarray。
        # .copy()，防止mss / numpy 的生命周期问题，下游模型 / opencv 有时要求连续内存等等原因，所以使用.copy()。
        return rgb
