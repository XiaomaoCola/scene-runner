# scene-runner

基于视觉的 Clash of Clans Builder Base 自动化框架。通过 PyTorch 分类游戏场景，FSM 驱动决策，ADB 执行点击/滑动操作，支持多设备并行。

## 架构分层

项目严格按 5 层分离，修改时注意不要跨层直接调用：

```
perception → decision → intents → planning → actuation
```

| 层 | 目录 |
|----|------|
| Perception | `src/scene_runner/perception/` | 
| Decision | `src/scene_runner/decision/` |
| Intents | `src/scene_runner/intents/` |
| Planning | `src/scene_runner/planning/` |
| Actuation | `src/scene_runner/actuation/` |

### 共享状态

`src/scene_runner/world_model/` 存放运行时共享状态（资源量、工人状态等）。

### 区域配置

所有 UI 区域坐标写在 `configs/intents/` 下的 YAML 文件里，使用 0–1 归一化坐标，与分辨率无关。Planning 层在运行时加载，不要把坐标硬编码进 Python。

## 编码约定

代码注释统一使用中文。
