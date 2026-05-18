# Scene Runner

基于计算机视觉的自动化框架，采用分层架构实现智能决策和执行。

## 架构概览

系统准备采用经典的五层架构：

```
感知层 → 决策层 → 意图层 → 规划层 → 执行层
Perception → Decision → Intent → Planning → Actuation
```

## 系统架构

### 📸 感知层 (Perception Layer)
- **职责**: 获取和理解游戏画面
- **功能**: 
  - 屏幕截图和窗口管理
  - 场景识别和分类
  - 目标检测和定位
- **输出**: 结构化的观察数据 (Observation)

### 🧠 决策层 (Decision Layer)
- **职责**: 基于当前观察做出决策
- **功能**:
  - 有限状态机 (FSM) 驱动
  - 场景驱动的状态转换
  - 超时和错误恢复机制
- **输出**: 抽象意图 (Intent)

### 💭 意图层 (Intent Layer)
- **职责**: 定义抽象的行为意图
- **输出**: 标准化意图对象

### 🗺️ 规划层 (Planning Layer)
- **职责**: 将抽象意图转换为具体执行计划
- **输出**: 可执行的动作计划 (ActionPlan)

### ⚡ 执行层 (Actuation Layer)
- **职责**: 执行具体的硬件操作
- **功能**:
  - 鼠标点击和移动
  - 键盘输入
  - 时序控制和同步
- **输出**: 物理设备操作

## 项目结构

```
src/scene-runner/
├── perception/          # 感知层
├── decision/           # 决策层 (规划中)
├── intent/             # 意图层 (规划中)
├── planning/           # 规划层 (规划中)
├── actuation/          # 执行层 (规划中)
└── world_model/        # 世界模型 (规划中)
```