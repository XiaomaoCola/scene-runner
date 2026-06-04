# 用任意 YOLO .pt 模型对当前设备截图做推理，打印检测结果并点击置信度最高的目标。
#
# 用法：
#   python tools/model/yolo_detect_and_click.py（直接run）
#   python tools/model/yolo_detect_and_click.py --conf 0.3
#   python tools/model/yolo_detect_and_click.py --no-click
#
# 流程：ADB 截图 → YOLO 推理 → 打印所有检测结果 → 点击置信度最高的 TARGET_CLASS
#
# 依赖：ultralytics（pip install ultralytics）、AdbCapture、Executor

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))

from ultralytics import YOLO

from scene_runner.actuation.actions import TapAction
from scene_runner.actuation.executor import Executor
from scene_runner.perception.sources.captures.adb_capture import AdbCapture

# ── 可调参数 ──────────────────────────────────────────────────────────────────
MODEL_PATH: Path = ROOT / "data/models/elixir_cart.pt"
TARGET_CLASS: str = "elixir_cart"   # 要点击的类别，留空则点击任意最高置信度目标
CONF_THRESHOLD: float = 0.7
# ─────────────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLO 检测推理工具")
    parser.add_argument("--conf", type=float, default=CONF_THRESHOLD, help=f"置信度阈值，默认 {CONF_THRESHOLD}")
    parser.add_argument("--no-click", action="store_true", help="只推理不点击")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("正在截图...")
    capture = AdbCapture()
    frame = capture.read()
    if frame is None:
        time.sleep(1.2)
        frame = capture.read()
    if frame is None:
        print("ERROR: ADB 截图失败，请检查连接")
        sys.exit(1)

    h, w = frame.shape[:2]
    print(f"截图尺寸：{w}x{h}")

    model = YOLO(str(MODEL_PATH))
    results = model(frame, conf=args.conf, verbose=False)
    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        print("未检测到任何目标")
        sys.exit(0)

    print(f"\n检测到 {len(boxes)} 个目标：")
    all_detections: list[tuple[float, str, float, float, float, float]] = []
    for box in boxes:
        cls_name = model.names[int(box.cls.item())]
        conf = float(box.conf.item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        print(f"  {cls_name:<22} conf={conf:.3f}  xyxy=({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")
        all_detections.append((conf, cls_name, x1, y1, x2, y2))

    if args.no_click:
        return

    # 优先点击 TARGET_CLASS，找不到则退而求其次点置信度最高的任意框
    targets = [d for d in all_detections if not TARGET_CLASS or d[1] == TARGET_CLASS]
    if not targets:
        print(f"\n未检测到 {TARGET_CLASS}，改为点击置信度最高的目标")
        targets = all_detections

    targets.sort(reverse=True)
    best_conf, label, x1, y1, x2, y2 = targets[0]
    print(f"\n点击：{label}  conf={best_conf:.3f}  xyxy=({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")

    region = (x1 / w, y1 / h, x2 / w, y2 / h)
    print(f"归一化区域：({region[0]:.4f}, {region[1]:.4f}, {region[2]:.4f}, {region[3]:.4f})")
    Executor(screen_size=(w, h)).execute([TapAction(region=region)])


if __name__ == "__main__":
    main()
