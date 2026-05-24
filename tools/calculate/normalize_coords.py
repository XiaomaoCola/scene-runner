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
