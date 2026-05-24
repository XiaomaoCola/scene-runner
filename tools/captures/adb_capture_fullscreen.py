# 该工具通过 ADB 截取当前设备全屏，并以时间戳命名保存到 data/scratch/full_screen/。
#
# 用法：
#   1. 确保 ADB 设备已连接（adb devices 可见设备）
#   2. 运行：python tools/captures/adb_capture_fullscreen.py
#   3. 截图保存到 data/scratch/full_screen/screen_<YYYYMMDD_HHMMSS>.png
#
# 典型用途：为 normalize_coords.py 或 makesense.ai 提供原始截图素材
#
# 依赖：AdbCapture（需 adb 环境）、opencv-python

import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))

from scene_runner.perception.sources.captures.adb_capture import AdbCapture

OUT_DIR = ROOT / "data/scratch/full_screen"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    capture = AdbCapture()
    frame = capture.read()
    if frame is None:
        time.sleep(1.1)
        frame = capture.read()
    if frame is None:
        print("ERROR: ADB 截图失败，请检查连接")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"screen_{ts}.png"
    cv2.imwrite(str(out_path), frame[:, :, ::-1])
    print(f"saved: {out_path}  ({frame.shape[1]}x{frame.shape[0]})")


if __name__ == "__main__":
    main()
