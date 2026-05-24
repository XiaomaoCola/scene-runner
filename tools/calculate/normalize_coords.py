# 将像素坐标转换为归一化坐标（0.0~1.0），供 YAML 配置文件使用。
#
# 用法：
#   1. 用 adb_capture_fullscreen.py 截取全屏图片
#   2. 将图片上传到 https://www.makesense.ai/ 框选目标区域，读取左上角(X1,Y1)和右下角(X2,Y2)像素坐标
#   3. 修改下方 WIDTH / HEIGHT 为截图实际分辨率，填入 X1 Y1 X2 Y2
#   4. 运行：python tools/calculate/normalize_coords.py
#   5. 将输出的 left/top/right/bottom 填入对应 YAML 配置文件

# ── 改这里 ──────────────────────────────────────────────────────────────────
WIDTH  = 1920 # 这是整张图的像素长度
HEIGHT = 1080 # 这是整张图的像素宽度

X1, Y1 = 1226, 634      # 左上角像素坐标
X2, Y2 = 1620, 788  # 右下角像素坐标
# ────────────────────────────────────────────────────────────────────────────

left   = round(X1 / WIDTH,  4)
top    = round(Y1 / HEIGHT, 4)
right  = round(X2 / WIDTH,  4)
bottom = round(Y2 / HEIGHT, 4)

print(f"left:   {left}")
print(f"top:    {top}")
print(f"right:  {right}")
print(f"bottom: {bottom}")
print()
print(f"region = ({left}, {top}, {right}, {bottom})")
