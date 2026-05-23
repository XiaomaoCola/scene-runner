import numpy as np
import pytest

from scene_runner.perception.sources.capture import FrameSource
from scene_runner.perception.sources.cropped.cropped_source import CroppedSource


class _FixedSource(FrameSource):
    """每次 read() 返回同一帧，用于测试。"""
    def __init__(self, frame: np.ndarray | None) -> None:
        self._frame = frame

    def read(self) -> np.ndarray | None:
        return self._frame


# ── 正常裁剪 ────────────────────────────────────────────────

def test_top_left_quarter_shape():
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    result = CroppedSource(_FixedSource(img), region=(0.0, 0.0, 0.5, 0.5)).read()
    assert result.shape == (50, 100, 3)


def test_top_left_quarter_pixels():
    # 左上角涂红，其余黑，裁剪后应全为红
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    img[0:50, 0:100] = [255, 0, 0]
    result = CroppedSource(_FixedSource(img), region=(0.0, 0.0, 0.5, 0.5)).read()
    assert np.all(result == [255, 0, 0])


def test_bottom_right_quarter_pixels():
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    img[50:100, 100:200] = [0, 255, 0]
    result = CroppedSource(_FixedSource(img), region=(0.5, 0.5, 1.0, 1.0)).read()
    assert np.all(result == [0, 255, 0])


def test_full_frame_region():
    img = np.random.randint(0, 256, (80, 120, 3), dtype=np.uint8)
    result = CroppedSource(_FixedSource(img), region=(0.0, 0.0, 1.0, 1.0)).read()
    assert result.shape == img.shape
    assert np.array_equal(result, img)


def test_returns_copy_not_view():
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    result = CroppedSource(_FixedSource(img), region=(0.0, 0.0, 0.5, 0.5)).read()
    result[:] = 99
    assert np.all(img == 0)  # 原帧不受影响


# ── 上游返回 None ────────────────────────────────────────────

def test_passthrough_none():
    result = CroppedSource(_FixedSource(None), region=(0.0, 0.0, 0.5, 0.5)).read()
    assert result is None


# ── 非法 region ──────────────────────────────────────────────

@pytest.mark.parametrize("region", [
    (0.5, 0.0, 0.2, 1.0),   # x1 > x2
    (0.0, 0.5, 1.0, 0.2),   # y1 > y2
    (-0.1, 0.0, 0.5, 1.0),  # x1 < 0
    (0.0, 0.0, 1.1, 1.0),   # x2 > 1
    (0.3, 0.3, 0.3, 0.8),   # x1 == x2
])
def test_invalid_region_raises(region):
    with pytest.raises(ValueError):
        CroppedSource(_FixedSource(np.zeros((100, 100, 3), dtype=np.uint8)), region=region)
