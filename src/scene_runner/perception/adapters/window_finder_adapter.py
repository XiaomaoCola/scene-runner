from __future__ import annotations
from window_finder import create_window_finder
from scene_runner.perception.geometry import ClientAreaRect, WindowGeometryProvider


class WindowFinderClientRectAdapter(WindowGeometryProvider):
    """
    Adapter: use `window_finder` package to provide client rect.

    Contract:
      - returns client rect in screen coords (LTRB)
    """

    def __init__(self) -> None:
        self._finder = create_window_finder()

    def get_client_rect(self, keyword: str) -> ClientAreaRect:
        win = self._finder.find_first(keyword)
        if not win:
            raise RuntimeError(f"Window not found by keyword: {keyword}")

        l, t, r, b = win.client_rect_ltrb
        rect = ClientAreaRect(int(l), int(t), int(r), int(b))

        if rect.width <= 0 or rect.height <= 0:
            raise RuntimeError(
                f"Invalid client rect for window '{win.title}': {win.client_rect_ltrb}"
            )

        return rect