# 该工具根据 YAML 配置文件里定义的区域，从 ADB 截图中批量裁剪模板图片。
#
# 用法：
#   1. 修改 YAML_PATH，指向目标 intent 的配置文件（configs/intents/.../*.yaml）
#   2. 确保 ADB 设备已连接（adb devices 可见设备）
#   3. 将游戏画面切换到 YAML 对应的场景
#   4. 运行：python tools/captures/adb_capture_template.py
#   5. 裁剪结果输出到 data/scratch/templates/，文件名格式：<yaml文件名>_<region名>_region.png
#   6. 确认图片可用后，手动复制到 data/templates/ 归档
#
# 依赖：AdbCapture（需 adb 环境）、opencv-python、pyyaml

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
