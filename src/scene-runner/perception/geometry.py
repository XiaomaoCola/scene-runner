from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ClientAreaRect:
    """
    Screen coordinates rectangle in (left, top, right, bottom).
    """
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    def to_mss_monitor(self) -> dict:
        """
        Convert to mss monitor dict: {left, top, width, height}
        """
        return {"left": int(self.left), "top": int(self.top), "width": int(self.width), "height": int(self.height)}


class WindowGeometryProvider(ABC):
    """
    Provide window geometry (client rect) in screen coordinates.

    This is a small interface that isolates OS-specific / external packages
    from the rest of the perception layer.
    """

    @abstractmethod
    def get_client_rect(self, keyword: str) -> ClientAreaRect:
        """
        Return client rect in screen coords (LTRB).

        Raises:
            RuntimeError if window not found / rect invalid.
        """
        raise NotImplementedError
