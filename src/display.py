from typing import Any

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.widgets import TextBox

from .app import App
from .params import PARAM_SPECS


class Display:
    """Matplotlib interface for browsing views, tuning parameters, and calibration."""

    def __init__(self, app: App) -> None:
        """Build the interactive figure and start its event loop."""
        self.app = app
        self.sliders: dict[str, Slider] = {}
        self.textboxes: dict[str, TextBox] = {}
        self.pending_calibration_point: str | None = None
        self.ui_init()
        self.display()

    def update_display(self) -> None:
        """Refresh the displayed image and title from the app's current view."""
        image = self.app.image_to_display()
        title, img, cmap = image
        self.img_artist.set_data(img)
        self.img_artist.set_cmap(cmap)
        if cmap == "gray":
            self.img_artist.set_clim(0, 255)
        self.ax.set_title(title)
        self.fig.canvas.draw_idle()

    def on_key(self, event: Any) -> None:
        """Handle view navigation, config shortcuts, and calibration key presses."""
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
        elif event.key == "1":
            self.pending_calibration_point = "low"
            print("Click the low-value point on the dial")
        elif event.key == "2":
            self.pending_calibration_point = "high"
            print("Click the high-value point on the dial")
        elif event.key == "d":
            self.app.toggle_gauge_direction()
            self.update_display()

    def on_click(self, event: Any) -> None:
        """Save the pending calibration point when the user clicks the image axes."""
        if self.pending_calibration_point is None or event.inaxes != self.ax:
            return
        if event.xdata is None or event.ydata is None:
            return
        self.app.set_calibration_point(
            self.pending_calibration_point, (event.xdata, event.ydata)
        )
        self.pending_calibration_point = None
        self.update_display()

    def quit(self) -> None:
        """Close the current Matplotlib figure."""
        plt.close(self.fig)

    def ui_init(self) -> None:
        """Create the image axes, tuning sliders, and calibration value fields."""
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

        bottom = 0.18 + len(PARAM_SPECS) * 0.05
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
        for name, y_pos in (("gauge_low_value", 0.08), ("gauge_high_value", 0.02)):
            ax = plt.axes((0.02, y_pos, 0.16, 0.04))
            label = "Low" if name.endswith("low_value") else "High"
            initial = str(self.app.state.config.get(name, 0.0))
            self.textboxes[name] = TextBox(ax, label, initial=initial)

    def set_param(self, param_name: str, value: float) -> None:
        """Apply a slider value through the app and refresh the displayed view."""
        self.app.set_param(param_name, value)
        self.update_display()

    def sync_sliders(self) -> None:
        """Move sliders to loaded config values without triggering recomputation."""
        for param_name, slider in self.sliders.items():
            slider.eventson = False
            slider.set_val(self.app.state.config[param_name])
            slider.eventson = True

    def set_calibration_value(self, name: str, value: str) -> None:
        """Parse a value field and update config, restoring its prior value if invalid."""
        try:
            self.app.set_param(name, float(value))
        except ValueError:
            self.textboxes[name].set_val(str(self.app.state.config.get(name, 0.0)))
            return
        self.update_display()

    def display(self) -> None:
        """Connect widget callbacks and show the interactive figure."""
        for param_name, slider in self.sliders.items():
            slider.on_changed(lambda val, name=param_name: self.set_param(name, val))
        for name, textbox in self.textboxes.items():
            textbox.on_submit(
                lambda value, key=name: self.set_calibration_value(key, value)
            )

        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        manager = plt.get_current_fig_manager()
        if hasattr(manager, "window") and hasattr(manager.window, "attributes"):
            manager.window.attributes("-fullscreen", True)
        plt.show()
