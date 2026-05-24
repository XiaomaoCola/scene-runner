from dataclasses import dataclass

# 以后意图多了用枚举。

@dataclass
class BuilderBaseAttackIntent:
    name: str = "builder_base_attack"
