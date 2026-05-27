from typing import Any


DebugView = tuple[str, Any, str | None]


class State:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.results: dict[str, Any] = {}
        self.debug_views: dict[str, DebugView] = {}
        self.display_order: list[str] = list(self.debug_views.keys())

    def set_param(self, key: str, value: Any) -> None:
        self.config[key] = value

    def add_result(self, key: str, result: Any) -> None:
        self.results[key] = result

    def add_view(
        self, key: str, title: str, image: Any, cmap: str | None = None
    ) -> None:
        self.debug_views[key] = (title, image, cmap)
        self.display_order.append(key)

    def update_result(self, key: str, result: Any) -> None:
        if key in self.results:
            self.results[key] = result
        else:
            raise KeyError(f"Result key '{key}' not found in state.")

    def update_view(self, key: str, image: Any) -> None:
        if key in self.debug_views:
            title, _, cmap = self.debug_views[key]
            self.debug_views[key] = (title, image, cmap)
        else:
            raise KeyError(f"Image key '{key}' not found in state.")

    def remove_result(self, key: str) -> None:
        if key in self.results:
            del self.results[key]
        else:
            raise KeyError(f"Result key '{key}' not found in state.")

    def remove_view(self, key: str) -> None:
        if key in self.debug_views:
            del self.debug_views[key]
            self.display_order.remove(key)
        else:
            raise KeyError(f"Image key '{key}' not found in state.")
