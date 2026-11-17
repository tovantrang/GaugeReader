from dataclasses import dataclass
from typing import Literal


ParamType = Literal["int", "float"]


@dataclass(frozen=True)
class ParamSpec:
    """Describe a numeric UI parameter and how slider values are displayed."""

    key: str
    label: str
    min_value: float
    max_value: float
    step: float
    value_type: ParamType

    @property
    def valfmt(self) -> str:
        """Return the Matplotlib format string appropriate for the parameter type."""
        return "%i" if self.value_type == "int" else "%.2f"

    def coerce(self, value: float) -> int | float:
        """Convert a slider value to the declared integer or float type."""
        if self.value_type == "int":
            return int(round(value))
        return float(value)


# Slider ranges and steps; Hough circle parameters are independent of Canny sliders.
PARAM_SPECS: list[ParamSpec] = [
    ParamSpec("canny_thrd1", "Canny low", 0, 500, 1, "int"),
    ParamSpec("canny_thrd2", "Canny high", 0, 500, 1, "int"),
    ParamSpec("hough_circle_param1", "Circle Canny", 0, 500, 1, "int"),
    ParamSpec("hough_circle_param2", "Circle votes", 0, 100, 1, "int"),
    ParamSpec("hough_min_radius", "Min radius", 0, 200, 1, "int"),
    ParamSpec("hough_max_radius", "Max radius", 0, 200, 1, "int"),
    ParamSpec("hough_line_threshold", "Line votes", 0, 200, 1, "int"),
]

PARAM_SPECS_BY_KEY: dict[str, ParamSpec] = {spec.key: spec for spec in PARAM_SPECS}
