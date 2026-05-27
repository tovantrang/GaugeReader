import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from .params import PARAM_SPECS


class Display:
    def __init__(self, app):
        self.app = app
        self.sliders = {}
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
        elif event.key == "ctrl+e":
            try:
                config_path = self.app.save_config()
                print(f"Saved config to {config_path}")
            except OSError as exc:
                print(f"Could not save config: {exc}")
        elif event.key == "ctrl+l":
            try:
                config_path = self.app.load_config()
            except (OSError, ValueError) as exc:
                print(f"Could not load config: {exc}")
            else:
                self.sync_sliders()
                self.update_display()
                print(f"Loaded config from {config_path}")

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

        bottom = 0.08 + len(PARAM_SPECS) * 0.05
        plt.subplots_adjust(bottom=bottom)
        for index, spec in enumerate(PARAM_SPECS):
            y_pos = bottom - 0.06 - index * 0.05
            slider_ax = plt.axes((0.25, y_pos, 0.65, 0.03))
            self.sliders[spec.key] = Slider(
                slider_ax,
                spec.label,
                spec.min_value,
                spec.max_value,
                valinit=self.app.state.config[spec.key],
                valfmt=spec.valfmt,
                valstep=spec.step,
            )

    def set_param(self, param_name, value):
        self.app.set_param(param_name, value)
        self.update_display()

    def sync_sliders(self):
        for param_name, slider in self.sliders.items():
            slider.eventson = False
            slider.set_val(self.app.state.config[param_name])
            slider.eventson = True

    def display(self):
        for param_name, slider in self.sliders.items():
            slider.on_changed(lambda val, name=param_name: self.set_param(name, val))

        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        manager = plt.get_current_fig_manager()
        if hasattr(manager, "window") and hasattr(manager.window, "attributes"):
            manager.window.attributes("-fullscreen", True)
        plt.show()
