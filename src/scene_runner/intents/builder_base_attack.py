from dataclasses import dataclass, field

# 以后意图多了用枚举。

@dataclass
class BuilderBaseAttackIntent:
    name: str = "builder_base_attack"
    # 跳过 Plan 层时暂时由 Intent 携带点击区域，待 Planner 实现后移走
    region: tuple = field(default=(0.00, 0.75, 0.15, 1.00))
