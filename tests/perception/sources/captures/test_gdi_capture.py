# 注意：对 BlueStacks 此方案截图为黑屏，原因见 src/scene_runner/perception/sources/test_gdi_capture.py 顶部。

import os
import sys
import time
from pathlib import Path

import cv2

from scene_runner.perception.sources.captures.gdi_capture import GdiCapture

KEYWORD = "BlueStacks"
OUT_DIR = Path(__file__).parents[3] / "runs" / "gdi_capture"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "screenshot.png"

    print(f"[1/3] 搜索窗口关键词: {KEYWORD!r}  (包含最小化窗口)")
    capture = GdiCapture(window_keyword=KEYWORD, fps_limit=1.0)

    # fps_limit=1 时第一次 read() 会直接返回帧，不需要等待
    frame = capture.read()
    if frame is None:
        # 极端情况下 fps 节流触发，等一下再试
        time.sleep(1.1)
        frame = capture.read()

    if frame is None:
        print("ERROR: read() 返回 None，请检查 fps_limit 设置")
        sys.exit(1)

    print(f"[2/3] 截图成功，shape = {frame.shape}  (H x W x 3, RGB)")

    cv2.imwrite(str(out_path), frame[:, :, ::-1])  # RGB → BGR for cv2
    print(f"[3/3] 已保存: {out_path}")

    os.startfile(str(out_path))  # Windows：用默认图片查看器打开


if __name__ == "__main__":
    main()
