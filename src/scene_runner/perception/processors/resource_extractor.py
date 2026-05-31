from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from scene_runner.world_model.home_village import Resources

ROOT = Path(__file__).resolve().parents[4]
TMPL_DIR = ROOT / "data" / "resource" / "30_templates"
DIGIT_SIZE = (32, 48)
LEFT_CROP_RATIO = 0.05


class ResourceExtractor:
    """从完整帧中识别金币和圣水数量。"""

    def __init__(self) -> None:
        self._templates: dict[str, np.ndarray] = {}
        for p in TMPL_DIR.glob("?.png"):
            if p.stem.isdigit():
                self._templates[p.stem] = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)

    def extract(self, frame: np.ndarray, config: dict) -> Resources:
        """
        frame: HxWxC uint8 RGB
        config: dict with gold_resource / elixir_resource normalized coords
        """
        h, w = frame.shape[:2]
        gold   = self._read_region(frame, h, w, config["gold_resource"])
        elixir = self._read_region(frame, h, w, config["elixir_resource"])
        return Resources(gold=gold, elixir=elixir)

    # ------------------------------------------------------------------ #

    def _read_region(self, frame: np.ndarray, h: int, w: int, roi: dict) -> int:
        crop = frame[
            int(roi["top"] * h): int(roi["bottom"] * h),
            int(roi["left"] * w): int(roi["right"] * w),
        ]
        binary = self._preprocess(crop)
        boxes  = self._find_boxes(binary)
        return self._match_number(binary, boxes)

    def _preprocess(self, crop_rgb: np.ndarray) -> np.ndarray:
        cw = crop_rgb.shape[1]
        cropped = crop_rgb[:, int(cw * LEFT_CROP_RATIO):]
        min_ch = np.min(cropped, axis=2).astype(np.uint8)
        _, binary = cv2.threshold(min_ch, 170, 255, cv2.THRESH_BINARY)
        return binary

    def _find_boxes(self, binary: np.ndarray) -> list[tuple[int, int, int, int]]:
        h = binary.shape[0]
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            if ch > h * 0.3 and cw >= 8:
                boxes.append((x, y, cw, ch))
        boxes.sort(key=lambda b: b[0])
        # 去掉孤立的最左侧轮廓（进度条高光噪声）
        if len(boxes) >= 2 and boxes[1][0] - (boxes[0][0] + boxes[0][2]) > 20:
            boxes = boxes[1:]
        return boxes

    def _match_digits(self, binary: np.ndarray, boxes: list) -> list[tuple[str, float]]:
        """返回所有轮廓的 (最佳匹配数字, 分数)，不做过滤。"""
        results = []
        for x, y, cw, ch in boxes:
            crop    = binary[y: y + ch, x: x + cw]
            resized = cv2.resize(crop, DIGIT_SIZE)
            best_digit, best_score = "0", -1.0
            for digit, tmpl in self._templates.items():
                score = float(cv2.matchTemplate(resized, tmpl, cv2.TM_CCOEFF_NORMED).max())
                if score > best_score:
                    best_score = score
                    best_digit = digit
            results.append((best_digit, best_score))
        return results

    def _match_number(self, binary: np.ndarray, boxes: list) -> int:
        matches = self._match_digits(binary, boxes)
        valid = [d for d, s in matches if s >= 0.4]
        return int("".join(valid)) if valid else 0

    def extract_verbose(self, frame: np.ndarray, config: dict) -> tuple[Resources, dict]:
        """同 extract，额外返回每个区域所有轮廓的识别分数，供调试用。"""
        h, w = frame.shape[:2]
        scores: dict[str, list[tuple[str, float]]] = {}
        totals: dict[str, int] = {}
        for key in ("gold_resource", "elixir_resource"):
            roi    = config[key]
            crop   = frame[int(roi["top"]*h):int(roi["bottom"]*h),
                           int(roi["left"]*w):int(roi["right"]*w)]
            binary = self._preprocess(crop)
            boxes  = self._find_boxes(binary)
            scores[key] = self._match_digits(binary, boxes)
            totals[key] = int("".join(d for d, s in scores[key] if s >= 0.4)) if scores[key] else 0
        return Resources(gold=totals["gold_resource"], elixir=totals["elixir_resource"]), scores