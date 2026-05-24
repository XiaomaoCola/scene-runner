import sys
import time
from pathlib import Path

import cv2
import yaml

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))

from scene_runner.perception.sources.captures.adb_capture import AdbCapture

# ── 改这里 ──────────────────────────────────────────────────────────────────
YAML_PATH = ROOT / "configs/intents/BuilderBaseAttack/stage2_attack_menu.yaml"
OUT_DIR   = ROOT / "data/scratch/templates"
# ────────────────────────────────────────────────────────────────────────────
# 产出先进 scratch，确认图片可用后手动复制到 data/templates/ 归档


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(YAML_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print("[1/3] ADB 截取全屏...")
    capture = AdbCapture()
    frame = capture.read()
    if frame is None:
        time.sleep(1.1)
        frame = capture.read()
    if frame is None:
        print("ERROR: ADB 截图失败，请检查连接")
        sys.exit(1)

    h, w = frame.shape[:2]
    print(f"[2/3] 全屏尺寸 {w}x{h}，开始裁剪...")

    yaml_stem = YAML_PATH.stem
    for region_name, elem in config.items():
        x1, y1, x2, y2 = elem["left"], elem["top"], elem["right"], elem["bottom"]
        crop = frame[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)]
        out_path = OUT_DIR / f"{yaml_stem}_{region_name}_region.png"
        cv2.imwrite(str(out_path), crop[:, :, ::-1])
        print(f"  saved: {out_path}  ({crop.shape[1]}x{crop.shape[0]})")

    print(f"[3/3] 完成，共保存 {len(config)} 张")


if __name__ == "__main__":
    main()
