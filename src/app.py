from .pipeline import Pipeline
from .state import State


class App:
    def __init__(self, config):
        self.state = State(config)
        self.pipeline = Pipeline()
        self.current = 0
        self.set_rgb()
        self.set_gray()
        self.recompute_all()

    def image_to_display(self):
        key = self.state.display_order[self.current]
        return self.state.debug_views[key]

    def next_image(self):
        self.current = (self.current + 1) % len(self.state.display_order)

    def prev_image(self):
        self.current = (self.current - 1) % len(self.state.display_order)

    def set_rgb(self):
        image_rgb = self.pipeline.compute_rgb_image(self.state.config["image_path"])
        self.state.add_result("image_rgb", image_rgb)
        self.state.add_view("image_rgb", "RGB", self.state.results["image_rgb"])

    def set_gray(self):
        image_gray = self.pipeline.compute_gray_image(self.state.results["image_rgb"])
        self.state.add_result("image_gray", image_gray)
        self.state.add_view(
            "image_gray", "Grayscale", self.state.results["image_gray"], "gray"
        )

    def set_canny(self):
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
        lines = self.pipeline.compute_lines(
            self.state.results["edges"],
            self.state.config["hough_line_threshold"],
            50,
            10,
        )
        image_with_lines = self.pipeline.draw_lines(
            self.state.results["image_rgb"], lines
        )
        if "lines" in self.state.results:
            self.state.update_result("lines", lines)
            self.state.update_view("overlay_lines", image_with_lines)
        else:
            self.state.add_result("lines", lines)
            self.state.add_view("overlay_lines", "Hough Lines", image_with_lines)

    def recompute_all(self):
        self.set_canny()
        self.set_circles()
        self.set_lines()

    def set_param(self, key: str, value):
        self.state.set_param(key, value)
        self.recompute_all()
