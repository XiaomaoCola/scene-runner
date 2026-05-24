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
