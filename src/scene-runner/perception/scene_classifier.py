from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

from scene_runner.world_model.observation import Observation


IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


@dataclass(frozen=True, slots=True)
class TorchCheckpointSpec:
# 这个类用来描述“训练时的关键参数”。
    model_architecture: str = "resnet18"
    # must match training，训练时用的是 resnet18 还是 resnet50必须写对。
    dropout: float = 0.5
    mean: Tuple[float, float, float] = IMAGENET_MEAN
    std: Tuple[float, float, float] = IMAGENET_STD
    # mean/std是指，训练时是不是按 ImageNet 归一化。


class SceneClassifier:
    """
    Torch scene classifier for saved checkpoint dict:

      {
        "model_state": state_dict,
        "class_names": [...],
        "num_classes": int,
        "img_size": int,
        ...
      }

    Responsibility:
      frame(RGB HWC uint8) -> Observation(scene, confidence)
    """

    def __init__(
        self,
        *,
        model_path: str | Path,
        device: str = "cpu",
        spec: TorchCheckpointSpec = TorchCheckpointSpec(),
    ) -> None:
        self.device = torch.device(device)
        self.spec = spec

        ckpt = torch.load(str(model_path), map_location=self.device)
        if not isinstance(ckpt, dict) or "model_state" not in ckpt:
            raise RuntimeError(
                "model_path is not a checkpoint dict with key 'model_state'. "
                "It must be saved by trainer.save_model()."
            )

        self.class_names: List[str] = list(ckpt["class_names"])
        self.num_classes: int = int(ckpt["num_classes"])
        self.img_size: int = int(ckpt["img_size"])

        # Build same architecture as training
        self.model = self._build_model(
            arch=self.spec.model_architecture,
            num_classes=self.num_classes,
            dropout=self.spec.dropout,
        ).to(self.device)

        self.model.load_state_dict(ckpt["model_state"])
        self.model.eval()

    def predict(self, frame: np.ndarray) -> Observation:
        x = self._preprocess(frame)
        # 把图片整理成模型能吃的格式

        with torch.no_grad():
            logits = self.model(x)
            # 把整理好的图片喂给模型

        scene, conf = self._postprocess(logits)
        # 把模型给出的“数字结果”翻译成人能懂的答案

        return Observation.now(scene=scene, confidence=conf)

    def _build_model(self, *, arch: str, num_classes: int, dropout: float) -> nn.Module:
        arch = arch.lower()
        if arch == "resnet18":
            m = models.resnet18(pretrained=False)  # weights irrelevant; we load state_dict
            in_features = m.fc.in_features
            m.fc = nn.Sequential(nn.Dropout(float(dropout)), nn.Linear(in_features, int(num_classes)))
            return m
        if arch == "resnet50":
            m = models.resnet50(pretrained=False)
            in_features = m.fc.in_features
            m.fc = nn.Sequential(nn.Dropout(float(dropout)), nn.Linear(in_features, int(num_classes)))
            return m
        raise ValueError(f"Unsupported model_architecture: {arch}")

    def _preprocess(self, frame: np.ndarray) -> torch.Tensor:
        if frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError(f"frame must be HWC RGB, got {frame.shape}")
            # .ndim = 这个数组有“几层方括号”。图片是 ndim == 3， [ 高度 [宽度 [ 颜色 ]]]
            # .shape 是一个 元组（tuple），表示每一维的大小。.所以可以用.shape[2]。
            # 如果不是高 × 宽 × 3，或者不是RGB三通道，返回ValueError。

        # uint8 RGB -> float32 [0,1]
        x = torch.from_numpy(frame).to(self.device).float() / 255.0  # HWC
        x = x.permute(2, 0, 1).unsqueeze(0)  # NCHW

        # resize to training img_size
        x = F.interpolate(x, size=(self.img_size, self.img_size), mode="bilinear", align_corners=False)

        # normalize (ImageNet)
        mean = torch.tensor(self.spec.mean, device=self.device).view(1, 3, 1, 1)
        std = torch.tensor(self.spec.std, device=self.device).view(1, 3, 1, 1)
        x = (x - mean) / std

        return x

    def _postprocess(self, logits: torch.Tensor) -> Tuple[str, float]:
        if logits.ndim != 2 or logits.shape[0] != 1:
            raise ValueError(f"logits must be [1,C], got {tuple(logits.shape)}")

        probs = torch.softmax(logits, dim=1)
        conf, idx = torch.max(probs, dim=1)

        i = int(idx.item())
        if i < 0 or i >= len(self.class_names):
            raise IndexError(f"class index {i} out of range, class_names size={len(self.class_names)}")

        return self.class_names[i], float(conf.item())
