from typing import Any

from .params import PARAM_SPECS_BY_KEY


DebugView = tuple[str, Any, str | None]


class State:
    """Store config, computed results, display-ready views, and their order."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize empty result and view stores around the supplied config."""
        self.config = config
        self.results: dict[str, Any] = {}
        self.debug_views: dict[str, DebugView] = {}
        self.display_order: list[str] = list(self.debug_views.keys())

    def set_param(self, key: str, value: Any) -> None:
        """Coerce known slider parameters to their declared type, then store them."""
        if key in PARAM_SPECS_BY_KEY:
            value = PARAM_SPECS_BY_KEY[key].coerce(value)
        self.config[key] = value

    def add_result(self, key: str, result: Any) -> None:
        """Add or replace a computed result by key."""
        self.results[key] = result

    def add_view(
        self, key: str, title: str, image: Any, cmap: str | None = None
    ) -> None:
        """Add a display tuple and append its key to the navigation order."""
        self.debug_views[key] = (title, image, cmap)
        self.display_order.append(key)

    def update_result(self, key: str, result: Any) -> None:
        """Replace an existing result, raising ``KeyError`` if it is absent."""
        if key in self.results:
            self.results[key] = result
        else:
            raise KeyError(f"Result key '{key}' not found in state.")

    def update_view(self, key: str, image: Any) -> None:
        """Replace an existing view image while preserving its title and colormap."""
        if key in self.debug_views:
            title, _, cmap = self.debug_views[key]
            self.debug_views[key] = (title, image, cmap)
        else:
            raise KeyError(f"Image key '{key}' not found in state.")

    def remove_result(self, key: str) -> None:
        """Remove a result, raising ``KeyError`` if it is absent."""
        if key in self.results:
            del self.results[key]
        else:
            raise KeyError(f"Result key '{key}' not found in state.")

    def remove_view(self, key: str) -> None:
        """Remove a view and its navigation entry, raising ``KeyError`` if absent."""
        if key in self.debug_views:
            del self.debug_views[key]
            self.display_order.remove(key)
        else:
            raise KeyError(f"Image key '{key}' not found in state.")
