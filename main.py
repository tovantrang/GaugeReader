from src.app import App
from src.display import Display


def main():
    config = {
        "image_path": "training_gauge.png",
        "canny_thrd1": 100,
        "canny_thrd2": 200,
        "hough_min_radius": 0,
        "hough_max_radius": 0,
        "hough_circle_param1": 200,
        "hough_circle_param2": 30,
        "hough_line_threshold": 50,
    }
    app = App(config)
    Display(app)


if __name__ == "__main__":
    main()
