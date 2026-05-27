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
