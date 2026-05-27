import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


class Display:
    def __init__(self, app):
        self.app = app
        self.ui_init()
        self.display()

    def update_display(self):
        image = self.app.image_to_display()
        title, img, cmap = image
        self.img_artist.set_data(img)
        self.img_artist.set_cmap(cmap)
        if cmap == "gray":
            self.img_artist.set_clim(0, 255)
        self.ax.set_title(title)
        self.fig.canvas.draw_idle()

    def on_key(self, event):
        if event.key == "right":
            self.app.next_image()
            self.update_display()
        elif event.key == "left":
            self.app.prev_image()
            self.update_display()
        elif event.key == "q":
            plt.close(self.fig)

    def quit(self):
        plt.close(self.fig)

    def ui_init(self):
        image = self.app.image_to_display()
        self.fig, self.ax = plt.subplots()
        self.img_artist = self.ax.imshow(
            image[1],
            cmap=image[2],
            vmin=0,
            vmax=255 if image[2] == "gray" else None,
        )
        self.ax.set_title(image[0])
        self.ax.axis("off")

        plt.subplots_adjust(bottom=0.25)
        ax_thrd1 = plt.axes((0.25, 0.15, 0.65, 0.03))
        ax_thrd2 = plt.axes((0.25, 0.1, 0.65, 0.03))
        ax_min_radius = plt.axes((0.25, 0.05, 0.65, 0.03))
        ax_max_radius = plt.axes((0.25, 0.0, 0.65, 0.03))
        self.slider_thrd1 = Slider(
            ax_thrd1,
            "Threshold 1",
            0,
            500,
            valinit=self.app.state.config["canny_thrd1"],
        )
        self.slider_thrd2 = Slider(
            ax_thrd2,
            "Threshold 2",
            0,
            500,
            valinit=self.app.state.config["canny_thrd2"],
        )
        self.slider_min_radius = Slider(
            ax_min_radius,
            "Min Radius",
            0,
            100,
            valinit=self.app.state.config["hough_min_radius"],
            valfmt="%i",
            valstep=1,
        )
        self.slider_max_radius = Slider(
            ax_max_radius,
            "Max Radius",
            0,
            100,
            valinit=self.app.state.config["hough_max_radius"],
            valfmt="%i",
            valstep=1,
        )

    def set_param(self, param_name, value):
        self.app.set_param(param_name, value)
        self.update_display()

    def display(self):
        self.slider_thrd1.on_changed(lambda val: self.set_param("canny_thrd1", val))
        self.slider_thrd2.on_changed(lambda val: self.set_param("canny_thrd2", val))
        self.slider_min_radius.on_changed(
            lambda val: self.set_param("hough_min_radius", val)
        )
        self.slider_max_radius.on_changed(
            lambda val: self.set_param("hough_max_radius", val)
        )

        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        manager = plt.get_current_fig_manager()
        if hasattr(manager, "window") and hasattr(manager.window, "attributes"):
            manager.window.attributes("-fullscreen", True)
        plt.show()
