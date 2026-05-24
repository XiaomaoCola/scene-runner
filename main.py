import time

from scene_runner.perception.sources.captures.adb_capture import AdbCapture
from scene_runner.decision.fsm import Fsm
from scene_runner.planning.planner import Planner
from scene_runner.actuation.executor import Executor


def main() -> None:
    capture = AdbCapture()
    fsm = Fsm()
    planner = Planner()

    print("[1/3] 截图中...")
    frame = capture.read()
    if frame is None:
        time.sleep(1.1)
        frame = capture.read()
    if frame is None:
        print("ERROR: ADB 截图失败")
        return

    h, w = frame.shape[:2]
    executor = Executor(screen_size=(w, h))

    print("[2/3] 决策中...")
    intent = fsm.decide(frame)
    print(f"      intent = {intent}")

    print("[3/3] 执行中...")
    if intent:
        region = planner.step(frame, intent)
        if region:
            executor.execute(region)
        else:
            print("[planner] 未找到目标元素，跳过")


if __name__ == "__main__":
    main()
