"""
从 ADB 截图中裁取金币和圣水区域，生成 binary 图供 label_digits.py 标注。

用法：
  1. 确保 ADB 设备已连接（adb devices 可见设备）
  2. 将游戏切换到能看到金币/圣水数值的场景
  3. 运行本脚本：python tools/resource/capture_resource.py
  4. 原始截图存到 data/resource/10_raw_slices/，binary 图存到 data/resource/20_processed/
  5. 重复多次，直到覆盖 0-9 所有数字后，运行 label_digits.py 生成模板
"""


import re
import sys
from pathlib import Path
import cv2
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from scene_runner.perception.sources.captures.adb_capture import AdbCapture

YAML_PATH       = ROOT / "configs/intents/BuilderBaseAttack/stage1_builder_base.yaml"
RAW_DIR         = ROOT / "data" / "resource" / "10_raw_slices"
PROC_DIR        = ROOT / "data" / "resource" / "20_processed"
LEFT_CROP_RATIO = 0.05


def next_session_index(directory: Path) -> int:
    max_n = 0
    for p in directory.glob("*_raw.png"):
        m = re.search(r"_(\d+)_raw\.png$", p.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n + 1


# ── Phase 1: 截图 ─────────────────────────────────────────────────────────────

def capture(config: dict) -> int:
    """全屏只截一次，从同一帧裁出两个区域并保存，返回本次使用的编号。"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    idx = next_session_index(RAW_DIR)

    print("[capture] ADB 截取全屏...")
    frame = AdbCapture().read()
    if frame is None:
        print("[ERROR] ADB 截图失败")
        return idx

    h, w = frame.shape[:2]

    for target in ("gold_resource", "elixir_resource"):
        if target not in config:
            print(f"[WARN] 配置缺失 {target}，跳过")
            continue
        roi = config[target]
        x1 = int(roi["left"]   * w)
        y1 = int(roi["top"]    * h)
        x2 = int(roi["right"]  * w)
        y2 = int(roi["bottom"] * h)
        crop = frame[y1:y2, x1:x2]
        path = RAW_DIR / f"{target}_{idx:03d}_raw.png"
        cv2.imwrite(str(path), crop[:, :, ::-1])
        print(f"[capture] {path}")

    return idx


# ── Phase 2: 预处理 ───────────────────────────────────────────────────────────

def _crop_bar(img_rgb: np.ndarray) -> np.ndarray:
    w = img_rgb.shape[1]
    return img_rgb[:, int(w * LEFT_CROP_RATIO):]


def preprocess(crop_rgb: np.ndarray) -> np.ndarray:
    cropped = _crop_bar(crop_rgb)
    min_ch = np.min(cropped, axis=2).astype(np.uint8)
    _, binary = cv2.threshold(min_ch, 170, 255, cv2.THRESH_BINARY)
    return binary


def process(idx: int) -> None:
    PROC_DIR.mkdir(parents=True, exist_ok=True)

    for target in ("gold_resource", "elixir_resource"):
        raw_path = RAW_DIR / f"{target}_{idx:03d}_raw.png"
        if not raw_path.exists():
            print(f"[WARN] 找不到 {raw_path}")
            continue

        bgr = cv2.imread(str(raw_path))
        rgb = bgr[:, :, ::-1]
        binary = preprocess(rgb)

        out_path = PROC_DIR / f"{target}_{idx:03d}_binary.png"
        cv2.imwrite(str(out_path), binary)
        print(f"[process] {out_path}")


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main() -> None:
    with open(YAML_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print("=== Phase 1: ADB 截图 ===")
    idx = capture(config)

    print("\n=== Phase 2: 预处理 ===")
    process(idx)


if __name__ == "__main__":
    main()