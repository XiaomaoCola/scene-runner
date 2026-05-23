# 运行方式（在 scene-runner 根目录）：
#     python tests/perception/sources/adb_capture.py
#
# 前置条件：BlueStacks 已启动，ADB 已连接：
#     "C:\Program Files\BlueStacks_nxt\HD-Adb.exe" connect 127.0.0.1:5555

import os
import sys
import time
from pathlib import Path

import cv2

from scene_runner.perception.sources.adb_capture import AdbCapture

OUT_DIR = Path(__file__).parents[3] / "runs" / "adb_capture"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "screenshot.png"

    print("[1/3] 通过 ADB 截图中...")
    capture = AdbCapture()

    frame = capture.read()
    if frame is None:
        time.sleep(1.1)
        frame = capture.read()

    if frame is None:
        print("ERROR: read() 返回 None，请检查 ADB 连接")
        sys.exit(1)

    print(f"[2/3] 截图成功，shape = {frame.shape}  (H x W x 3, RGB)")

    cv2.imwrite(str(out_path), frame[:, :, ::-1])  # RGB → BGR for cv2
    print(f"[3/3] 已保存: {out_path}")

    os.startfile(str(out_path))


if __name__ == "__main__":
    main()
