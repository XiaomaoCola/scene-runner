"""
识别 Builder Base 右上角资源：截一张 ADB 截图，识别当前金币和圣水，打印结果。
"""

import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from scene_runner.perception.sources.captures.adb_capture import AdbCapture
from scene_runner.perception.processors.resource_extractor import ResourceExtractor

YAML_PATH = ROOT / "configs/intents/BuilderBaseAttack/stage1_builder_base.yaml"
THRESHOLD = 0.75


def main() -> None:
    with open(YAML_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print("截图中...")
    frame = AdbCapture().read()
    if frame is None:
        print("ERROR: ADB 截图失败，请检查连接")
        sys.exit(1)

    extractor = ResourceExtractor()
    if not extractor._templates:
        print("ERROR: 没找到模板，请确认 data/resource/30_templates/ 里有 0-9.png")
        sys.exit(1)

    resources, scores = extractor.extract_verbose(frame, config)

    for region, label in (("gold_resource", "金币"), ("elixir_resource", "圣水")):
        print(f"\n{label}:")
        for i, (digit, score) in enumerate(scores[region]):
            flag = "" if score >= THRESHOLD else "  ← 低分丢弃"
            print(f"  轮廓{i}: '{digit}'  score={score:.3f}{flag}")

    print(f"\n{'─'*30}")
    print(f"金币:  {resources.gold}")
    print(f"圣水:  {resources.elixir}")


if __name__ == "__main__":
    main()