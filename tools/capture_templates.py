# 从 YAML 坐标文件批量截取模板图片，保存到指定目录。
#
# 运行方式（在 scene-runner 根目录）：
#   python tools/capture_templates.py <yaml路径> <输出目录>
#
# 示例：
#   python tools/capture_templates.py \
#     configs/intents/BuilderBaseAttack/stage1_builder_base.yaml \
#     configs/templates/builder_base/base

import sys
import time
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from scene_runner.perception.sources.captures.adb_capture import AdbCapture


def main(yaml_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(yaml_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"[1/3] ADB 截取全屏...")
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

    for name, elem in config.items():
        x1, y1 = elem["left"], elem["top"]
        x2, y2 = elem["right"], elem["bottom"]
        crop = frame[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)]

        out_path = out_dir / f"{name}.png"
        cv2.imwrite(str(out_path), crop[:, :, ::-1])  # RGB → BGR
        print(f"  saved: {out_path}  ({crop.shape[1]}x{crop.shape[0]})")

    print(f"[3/3] 完成，共保存 {len(config)} 张")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python tools/capture_templates.py <yaml路径> <输出目录>")
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
