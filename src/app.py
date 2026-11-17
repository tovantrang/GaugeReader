import json
from pathlib import Path

from .pipeline import Pipeline
from .state import State


class App:
    """Coordinate pipeline calculations, application state, and config persistence."""

    def __init__(self, config, config_path="config.json"):
        """Create state and compute the initial set of result and debug views."""
        self.state = State(config)
        self.pipeline = Pipeline()
        self.config_path = Path(config_path)
        self.current = 0
        self.reload_image()

    def reload_image(self):
        """Clear image-dependent data and rebuild all pipeline views from the config."""
        self.current = 0
        self.state.results.clear()
        self.state.debug_views.clear()
        self.state.display_order.clear()
        self.set_rgb()
        self.set_gray()
        self.recompute_all()

    def image_to_display(self):
        """Return the title, image, and colormap for the currently selected view."""
        key = self.state.display_order[self.current]
        return self.state.debug_views[key]

    def next_image(self):
        """Advance the selected debug view, wrapping at the end."""
        self.current = (self.current + 1) % len(self.state.display_order)

    def prev_image(self):
        """Move to the previous debug view, wrapping at the beginning."""
        self.current = (self.current - 1) % len(self.state.display_order)

    def set_rgb(self):
        """Load the configured source image and register its initial view."""
        image_rgb = self.pipeline.compute_rgb_image(self.state.config["image_path"])
        self.state.add_result("image_rgb", image_rgb)
        self.state.add_view(
            "image_rgb",
            "Start here: source image (use ←/→ to explore)",
            self.state.results["image_rgb"],
        )

    def set_gray(self):
        """Compute and register the grayscale source image."""
        image_gray = self.pipeline.compute_gray_image(self.state.results["image_rgb"])
        self.state.add_result("image_gray", image_gray)
        self.state.add_view(
            "image_gray", "Grayscale", self.state.results["image_gray"], "gray"
        )

    def set_canny(self):
        """Compute Canny edges and create or refresh their debug view."""
        image_canny = self.pipeline.compute_canny_edges(
            self.state.results["image_gray"],
            self.state.config["canny_thrd1"],
            self.state.config["canny_thrd2"],
        )
        if "edges" in self.state.results:
            self.state.update_result("edges", image_canny)
            self.state.update_view("edges", image_canny)
        else:
            self.state.add_result("edges", image_canny)
            self.state.add_view(
                "edges", "Canny Edges", self.state.results["edges"], "gray"
            )

    def set_circles(self):
        """Detect circles and refresh the circle overlay."""
        circles = self.pipeline.compute_hough_circles(
            self.state.results["image_gray"],
            self.state.config["hough_circle_param1"],
            self.state.config["hough_circle_param2"],
            self.state.config["hough_min_radius"],
            self.state.config["hough_max_radius"],
        )
        image_with_circles = self.pipeline.draw_circles(
            self.state.results["image_rgb"], circles
        )
        if "circles" in self.state.results:
            self.state.update_result("circles", circles)
            self.state.update_view("overlay_circles", image_with_circles)
        else:
            self.state.add_result("circles", circles)
            self.state.add_view("overlay_circles", "Hough Circles", image_with_circles)

    def set_lines(self):
        """Mask edges by the first circle, detect line segments, and refresh views."""
        masked_edges = self.pipeline.compute_circle_masked_image(
            self.state.results["edges"],
            self.state.results["circles"],
        )
        lines = self.pipeline.compute_lines(
            masked_edges,
            self.state.config["hough_line_threshold"],
            50,
            10,
        )
        image_with_lines = self.pipeline.draw_lines(
            self.state.results["image_rgb"], lines
        )
        if "masked_edges" in self.state.results:
            self.state.update_result("masked_edges", masked_edges)
            self.state.update_view("masked_edges", masked_edges)
        else:
            self.state.add_result("masked_edges", masked_edges)
            self.state.add_view("masked_edges", "Masked Edges", masked_edges, "gray")

        if "lines" in self.state.results:
            self.state.update_result("lines", lines)
            self.state.update_view("overlay_lines", image_with_lines)
        else:
            self.state.add_result("lines", lines)
            self.state.add_view("overlay_lines", "Hough Lines", image_with_lines)

    def set_needle_analysis(self):
        """Estimate the needle angle/value and refresh the final overlay."""
        needle_analysis = self.pipeline.compute_needle_analysis(
            self.state.results["circles"],
            self.state.results["lines"],
        )
        calibration = self.pipeline.compute_calibrated_value(
            needle_analysis, self.state.config
        )
        image_with_needle = self.pipeline.draw_needle_analysis(
            self.state.results["image_rgb"],
            needle_analysis,
            calibration,
            self.state.config,
        )
        if "needle_analysis" in self.state.results:
            self.state.update_result("needle_analysis", needle_analysis)
            self.state.update_view("overlay_needle", image_with_needle)
        else:
            self.state.add_result("needle_analysis", needle_analysis)
            self.state.add_view("overlay_needle", "Needle Angle", image_with_needle)

    def recompute_all(self):
        """Recompute parameter-dependent stages in pipeline order."""
        self.set_canny()
        self.set_circles()
        self.set_lines()
        self.set_needle_analysis()

    def set_param(self, key: str, value):
        """Update a config value and recompute all derived outputs."""
        self.state.set_param(key, value)
        self.recompute_all()

    def set_calibration_point(self, point_name, point):
        """Store a clicked low/high endpoint in source-image pixel coordinates."""
        self.state.set_param(
            f"gauge_{point_name}_point", [float(point[0]), float(point[1])]
        )
        self.set_needle_analysis()

    def toggle_gauge_direction(self):
        """Switch the configured scale direction and return its new value."""
        direction = self.state.config.get("gauge_direction", "cw")
        self.state.set_param("gauge_direction", "ccw" if direction == "cw" else "cw")
        self.set_needle_analysis()
        return self.state.config["gauge_direction"]

    def save_config(self, path=None):
        """Write the current config as JSON and return the destination path."""
        config_path = Path(path) if path is not None else self.config_path
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open("w", encoding="utf-8") as config_file:
            json.dump(self.state.config, config_file, indent=2)
            config_file.write("\n")
        return config_path

    def load_config(self, path=None):
        """Load JSON settings; reload the image only when its path changed."""
        config_path = Path(path) if path is not None else self.config_path
        with config_path.open(encoding="utf-8") as config_file:
            loaded_config = json.load(config_file)
        if not isinstance(loaded_config, dict):
            raise ValueError(f"Config must be a JSON object: {config_path}")

        old_image_path = self.state.config["image_path"]
        for key, value in loaded_config.items():
            self.state.set_param(key, value)

        if self.state.config["image_path"] != old_image_path:
            self.reload_image()
        else:
            self.recompute_all()
        return config_path
