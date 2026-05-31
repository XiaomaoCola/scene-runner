import time

from scene_runner.perception.sources.captures.adb_capture import AdbCapture
from scene_runner.decision.fsm import Fsm
from scene_runner.planning.planner import Planner
from scene_runner.actuation.executor import Executor
from scene_runner.world_model.builder_base import BuilderBase

_LOOP_INTERVAL = 1  # 每帧间隔（秒）


def main() -> None:
    builder_base = BuilderBase()
    capture = AdbCapture()
    fsm = Fsm(builder_base)
    planner = Planner(builder_base)

    # 先截一帧，用于初始化 Executor 的屏幕尺寸
    print("[init] 初始化截图...")
    frame = capture.read()
    if frame is None:
        time.sleep(1.1)
        frame = capture.read()
    if frame is None:
        print("ERROR: ADB 截图失败，退出")
        return

    h, w = frame.shape[:2]
    executor = Executor(screen_size=(w, h))
    print(f"[init] 屏幕尺寸 {w}x{h}，开始主循环")

    while True:
        frame = capture.read()
        if frame is None:
            print("WARN: 截图失败，跳过本此循环")
            time.sleep(_LOOP_INTERVAL)
            continue

        intent = fsm.decide(frame)
        if intent is None:
            print("WARN: INTENT 返回为空，跳过本次循环")
            time.sleep(_LOOP_INTERVAL)
            continue

        try:
            action_list = planner.step(frame, intent)
        except NotImplementedError as e:
            print(f"[main] {e}")
            break

        if action_list:
            executor.execute(action_list)

        time.sleep(_LOOP_INTERVAL)


if __name__ == "__main__":
    main()
