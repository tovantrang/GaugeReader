import cv2
import numpy as np


class Pipeline:
    def compute_rgb_image(self, image_path):
        image_bgr = cv2.imread(image_path)
        if image_bgr is None:
            raise FileNotFoundError(f"Could not load image: {image_path}")
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        return image_rgb

    def compute_gray_image(self, image_rgb):
        return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

    def compute_canny_edges(self, image, thrd1, thrd2):
        return cv2.Canny(image, thrd1, thrd2)

    def compute_hough_circles(self, image, param1, param2, min_radius, max_radius):
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

    def draw_circles(self, image, circles):
        img_rgb_copy = image.copy()
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # circle
                cv2.circle(img_rgb_copy, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # center
                cv2.circle(img_rgb_copy, (i[0], i[1]), 2, (0, 0, 255), 3)
        return img_rgb_copy

    def compute_circle_masked_image(self, image, circles):
        if circles is None:
            return image

        circles = np.uint16(np.around(circles))
        x, y, radius = circles[0, 0]
        mask = np.zeros_like(image)
        cv2.circle(mask, (x, y), radius, 255, -1)
        return cv2.bitwise_and(image, mask)

    def compute_lines(self, image, thrd, min_line_length, max_line_gap):
        return cv2.HoughLinesP(
            image,
            1,
            np.pi / 180,
            threshold=thrd,
            minLineLength=min_line_length,
            maxLineGap=max_line_gap,
        )

    def draw_lines(self, image, lines):
        img_rgb_copy = image.copy()
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(img_rgb_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)
        return img_rgb_copy

    def compute_circle_center(self, circles):
        if circles is None:
            return None

        circles = np.uint16(np.around(circles))
        x, y, _ = circles[0, 0]
        return int(x), int(y)

    def select_needle_lines(self, lines):
        if lines is None or len(lines) < 2:
            return None

        flattened_lines = [tuple(int(value) for value in line[0]) for line in lines]
        sorted_lines = sorted(
            flattened_lines,
            key=lambda line: (line[2] - line[0]) ** 2 + (line[3] - line[1]) ** 2,
            reverse=True,
        )
        return sorted_lines[:2]

    def compute_line_intersection(self, line_a, line_b):
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

    def compute_angle(self, center, point):
        center_x, center_y = center
        point_x, point_y = point
        dx = point_x - center_x
        dy = center_y - point_y
        angle = np.degrees(np.arctan2(dy, dx))
        return float(angle)

    def compute_needle_analysis(self, circles, lines):
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

    def draw_needle_analysis(self, image, analysis):
        img_rgb_copy = image.copy()
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
            f"{analysis['angle_deg']:.1f} deg",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        return img_rgb_copy
