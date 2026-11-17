from pathlib import Path
from typing import Any
from typing import TypeAlias
from typing import TypedDict

import cv2
import numpy as np
from numpy.typing import NDArray


ImageArray: TypeAlias = NDArray[np.uint8]
CircleArray: TypeAlias = NDArray[np.float32] | None
LineArray: TypeAlias = NDArray[np.int32] | None


class NeedleAnalysis(TypedDict):
    """Needle geometry returned by the prototype line-selection heuristic."""

    center: tuple[int, int]
    tip: tuple[float, float]
    angle_deg: float
    lines: list[tuple[int, int, int, int]]


class Calibration(TypedDict):
    """Mapped gauge value and the two calibration angles, in degrees."""

    value: float
    low_angle: float
    high_angle: float


class Pipeline:
    """Image-processing steps used to detect a gauge and estimate its reading."""

    def compute_rgb_image(self, image_path: str | Path) -> ImageArray:
        """Load an image as RGB; relative paths are resolved from the repository root."""
        image_path = Path(image_path)
        if not image_path.is_absolute():
            image_path = Path(__file__).resolve().parent.parent / image_path
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            raise FileNotFoundError(f"Could not load image: {image_path}")
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        return image_rgb

    def compute_gray_image(self, image_rgb: ImageArray) -> ImageArray:
        """Convert an RGB image to the grayscale image used by OpenCV detectors."""
        return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

    def compute_canny_edges(
        self, image: ImageArray, thrd1: int, thrd2: int
    ) -> ImageArray:
        """Return Canny edges using the lower and upper hysteresis thresholds."""
        return cv2.Canny(image, thrd1, thrd2)

    def compute_hough_circles(
        self,
        image: ImageArray,
        param1: int,
        param2: int,
        min_radius: int,
        max_radius: int,
    ) -> CircleArray:
        """Detect circles with Hough gradient; return OpenCV's array or ``None``."""
        circles = cv2.HoughCircles(
            image,
            cv2.HOUGH_GRADIENT,
            1,
            20,
            param1=param1,
            param2=param2,
            minRadius=min_radius,
            maxRadius=max_radius,
        )
        return circles

    def draw_circles(self, image: ImageArray, circles: CircleArray) -> ImageArray:
        """Draw detected circles and centers on a copy of the RGB image."""
        img_rgb_copy = image.copy()
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # circle
                cv2.circle(img_rgb_copy, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # center
                cv2.circle(img_rgb_copy, (i[0], i[1]), 2, (0, 0, 255), 3)
        return img_rgb_copy

    def compute_circle_masked_image(
        self, image: ImageArray, circles: CircleArray
    ) -> ImageArray:
        """Keep pixels inside the first detected circle, or return the input unchanged."""
        if circles is None:
            return image

        circles = np.uint16(np.around(circles))
        x, y, radius = circles[0, 0]
        mask = np.zeros_like(image)
        cv2.circle(mask, (x, y), radius, 255, -1)
        return cv2.bitwise_and(image, mask)

    def compute_lines(
        self, image: ImageArray, thrd: int, min_line_length: int, max_line_gap: int
    ) -> LineArray:
        """Detect line segments with probabilistic Hough transform parameters."""
        return cv2.HoughLinesP(
            image,
            1,
            np.pi / 180,
            threshold=thrd,
            minLineLength=min_line_length,
            maxLineGap=max_line_gap,
        )

    def draw_lines(self, image: ImageArray, lines: LineArray) -> ImageArray:
        """Draw detected segments on a copy of the RGB image."""
        img_rgb_copy = image.copy()
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(img_rgb_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)
        return img_rgb_copy

    def compute_circle_center(self, circles: CircleArray) -> tuple[int, int] | None:
        """Return the rounded center of the first detected circle, if any."""
        if circles is None:
            return None

        circles = np.uint16(np.around(circles))
        x, y, _ = circles[0, 0]
        return int(x), int(y)

    def select_needle_lines(
        self, lines: LineArray
    ) -> list[tuple[int, int, int, int]] | None:
        """Select the two longest detected segments as a simple needle-edge heuristic."""
        if lines is None or len(lines) < 2:
            return None

        flattened_lines: list[tuple[int, int, int, int]] = [
            (
                int(line[0][0]),
                int(line[0][1]),
                int(line[0][2]),
                int(line[0][3]),
            )
            for line in lines
        ]
        sorted_lines = sorted(
            flattened_lines,
            key=lambda line: (line[2] - line[0]) ** 2 + (line[3] - line[1]) ** 2,
            reverse=True,
        )
        return sorted_lines[:2]

    def compute_line_intersection(
        self, line_a: tuple[int, int, int, int], line_b: tuple[int, int, int, int]
    ) -> tuple[float, float] | None:
        """Return the infinite-line intersection, or ``None`` for parallel lines."""
        x1, y1, x2, y2 = (float(value) for value in line_a)
        x3, y3, x4, y4 = (float(value) for value in line_b)

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            return None

        determinant_a = x1 * y2 - y1 * x2
        determinant_b = x3 * y4 - y3 * x4
        px = (determinant_a * (x3 - x4) - (x1 - x2) * determinant_b) / denominator
        py = (determinant_a * (y3 - y4) - (y1 - y2) * determinant_b) / denominator
        return float(px), float(py)

    def compute_angle(
        self, center: tuple[float, float], point: tuple[float, float]
    ) -> float:
        """Return image angle in degrees: 0 right, 90 up, 180 left, -90 down."""
        center_x, center_y = center
        point_x, point_y = point
        dx = point_x - center_x
        dy = center_y - point_y
        angle = np.degrees(np.arctan2(dy, dx))
        return float(angle)

    def normalize_angle(self, angle: float) -> float:
        """Wrap an angle in degrees into the interval [0, 360)."""
        return float(angle % 360)

    def compute_gauge_value(
        self,
        needle_angle: float,
        low_angle: float,
        high_angle: float,
        low_value: float,
        high_value: float,
        direction: str = "cw",
    ) -> float | None:
        """Linearly interpolate between endpoint angles, clamping outside the sweep."""
        needle_angle = self.normalize_angle(needle_angle)
        low_angle = self.normalize_angle(low_angle)
        high_angle = self.normalize_angle(high_angle)
        if direction == "cw":
            sweep = (low_angle - high_angle) % 360
            position = (low_angle - needle_angle) % 360
        else:
            sweep = (high_angle - low_angle) % 360
            position = (needle_angle - low_angle) % 360
        if sweep == 0:
            return None
        ratio = min(max(position / sweep, 0), 1)
        return float(low_value + ratio * (high_value - low_value))

    def compute_calibrated_value(
        self, analysis: NeedleAnalysis | None, config: dict[str, Any]
    ) -> Calibration | None:
        """Map a needle angle to a value using configured clicked endpoints, if set."""
        if analysis is None:
            return None
        low_point = config.get("gauge_low_point")
        high_point = config.get("gauge_high_point")
        if low_point is None or high_point is None:
            return None
        center = analysis["center"]
        low_angle = self.compute_angle(center, low_point)
        high_angle = self.compute_angle(center, high_point)
        value = self.compute_gauge_value(
            analysis["angle_deg"],
            low_angle,
            high_angle,
            config.get("gauge_low_value", 0.0),
            config.get("gauge_high_value", 100.0),
            config.get("gauge_direction", "cw"),
        )
        if value is None:
            return None
        return {"value": value, "low_angle": low_angle, "high_angle": high_angle}

    def compute_needle_analysis(
        self, circles: CircleArray, lines: LineArray
    ) -> NeedleAnalysis | None:
        """Estimate center, tip, angle, and selected segments; return ``None`` on failure."""
        center = self.compute_circle_center(circles)
        selected_lines = self.select_needle_lines(lines)
        if center is None or selected_lines is None:
            return None

        tip = self.compute_line_intersection(selected_lines[0], selected_lines[1])
        if tip is None:
            return None

        angle = self.compute_angle(center, tip)
        return {
            "center": center,
            "tip": tip,
            "angle_deg": angle,
            "lines": selected_lines,
        }

    def draw_needle_analysis(
        self,
        image: ImageArray,
        analysis: NeedleAnalysis | None,
        calibration: Calibration | None = None,
        config: dict[str, Any] | None = None,
    ) -> ImageArray:
        """Render the needle estimate and optional calibration marks on an image copy."""
        img_rgb_copy = image.copy()
        if config is not None:
            for name, color in (("low", (0, 180, 255)), ("high", (0, 255, 255))):
                point = config.get(f"gauge_{name}_point")
                if point is not None:
                    point = tuple(int(round(value)) for value in point)
                    cv2.circle(img_rgb_copy, point, 5, color, -1)
                    label = f"{name}={config.get(f'gauge_{name}_value', 0)}"
                    cv2.putText(
                        img_rgb_copy,
                        label,
                        (point[0] + 8, point[1] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1,
                        cv2.LINE_AA,
                    )
        if analysis is None:
            return img_rgb_copy

        center = tuple(int(round(value)) for value in analysis["center"])
        tip = tuple(int(round(value)) for value in analysis["tip"])
        for line in analysis["lines"]:
            x1, y1, x2, y2 = line
            cv2.line(img_rgb_copy, (x1, y1), (x2, y2), (255, 180, 0), 2)

        cv2.circle(img_rgb_copy, center, 4, (0, 255, 0), -1)
        cv2.circle(img_rgb_copy, tip, 4, (255, 0, 0), -1)
        cv2.line(img_rgb_copy, center, tip, (255, 255, 0), 2)
        cv2.putText(
            img_rgb_copy,
            f"{analysis['angle_deg']:.1f} deg"
            + (
                f" | value={calibration['value']:.2f}"
                if calibration
                else " | calibrate: press 1/2, click endpoints"
            ),
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        return img_rgb_copy
