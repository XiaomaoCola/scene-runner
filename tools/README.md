# tools/

开发辅助工具集，用于截图采集和坐标计算，不参与运行时逻辑。

---

## 工具导航

### captures/

| 工具 | 功能 | 输出 |
|------|------|------|
| [adb_capture_fullscreen.py](captures/adb_capture_fullscreen.py) | ADB 截取当前设备全屏 | `data/scratch/full_screen/screen_<时间戳>.png` |
| [adb_capture_template.py](captures/adb_capture_template.py) | 按 YAML 配置批量裁剪模板图片 | `data/scratch/templates/<yaml名>_<region名>_region.png` |

### calculate/

| 工具 | 功能 | 输出 |
|------|------|------|
| [normalize_coords.py](calculate/normalize_coords.py) | 像素坐标 → 归一化坐标（0.0~1.0） | 打印 left/top/right/bottom |

