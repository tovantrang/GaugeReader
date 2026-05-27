# GaugeReader Project Notes

## 1. Current Project Goal

Build a classical Computer Vision pipeline that estimates the angle of a needle on an analog dial/gauge from a single image.

The learning goal is robust CV engineering, not a one-off solution for the current training image. The project should stay understandable while the base pipeline is still forming.

## 2. Current Architecture

- `main.py`: entrypoint only. Builds the initial config, creates `App`, then creates `Display`.
- `src/app.py`: orchestrator and central logic. Owns pipeline execution order, writes algorithmic outputs into `State.results`, writes visualization entries into `State.debug_views`, and reacts to parameter changes from the UI.
- `src/params.py`: centralized parameter specs for slider generation and value coercion.
- `src/state.py`: mostly passive storage for `config`, `results`, `debug_views`, and `display_order`.
- `src/pipeline.py`: pure CV functions. It should not know about `App`, `State`, or `Display`.
- `src/display.py`: Matplotlib UI. Owns sliders, keyboard events, and display refresh. It can call `App`, but `App` should not call `Display`.
- Config import/export currently uses JSON through `App.save_config()` and `App.load_config()`.

Current note: the current view index is stored in `App.current`, not `State`. That is acceptable for now, but if the intended design is "State stores current view", move it later as a small cleanup.

## 3. Current Known Issues Or Likely Bugs

- `src/app.py` uses a simple `recompute_all()` for slider changes. Why it matters: this favors correctness while the pipeline is changing, but it may become too expensive when more steps are added. Smallest future fix: replace it with a parameter dependency map once the pipeline stabilizes.
- `src/app.py` initializes all views eagerly. This is good for Display startup, but every `add_view` appends to `display_order`. Why it matters: if setup methods are called again with a new key or without the existing-key branch, duplicate display entries could appear. Smallest fix: keep `add_view` only for first creation and `update_view` for refresh.

## 4. Import / Module / Package Status

- `src/__init__.py` exists, so `src` is now a package.
- `main.py` imports with `from src.app import App` and `from src.display import Display`.
- `src/app.py` correctly uses relative imports: `from .pipeline import Pipeline` and `from .state import State`.
- Preferred run path: run from the repository root with `python main.py` inside the `gauge-cv` environment.
- Avoid running files inside `src/` directly for now, because relative imports are package-oriented.

## 5. Bootstrap / Startup Path Status

- `main.py` now calls `main()` under `if __name__ == "__main__":`.
- `App.__init__()` currently computes initial `image_rgb`, `image_gray`, `edges`, `overlay_circles`, and `overlay_lines` before `Display` reads the first image.
- Verified in `gauge-cv`: `App` initializes `display_order` as `["image_rgb", "image_gray", "edges", "overlay_circles", "overlay_lines"]`.
- `Pipeline.compute_rgb_image()` now raises a clear `FileNotFoundError` if the image cannot be loaded.
- The full graphical `Display` launch was not validated headlessly, because it depends on an interactive Matplotlib backend.

## 6. State / Results / Debug Views Consistency Checklist

- `results` should store algorithmic data:
  - `image_rgb`: RGB image array.
  - `image_gray`: grayscale image array.
  - `edges`: Canny edge image array.
  - `circles`: raw `HoughCircles` result, possibly `None`.
  - `masked_edges`: Canny edges masked by the selected circle.
  - `lines`: raw `HoughLinesP` result, possibly `None`.
  - `needle_analysis`: prototype angle result from circle center and two selected needle edge lines.
- `debug_views` should store display-ready tuples: `(title, image, cmap)`.
- Debug views may reference arrays in `results` for non-mutating views.
- Overlay views should copy the source image before drawing.
- `overlay_circles` and `overlay_lines` should display RGB copies with drawings, not overwrite `image_rgb`.
- Grayscale-like views should use `cmap="gray"`.
- RGB overlay views should use `cmap=None`.
- `display_order` should contain keys that exist in `debug_views`.
- Slider callbacks should update `State.config`, recompute affected results/views, then call `Display.update_display()`.
- Current simple rule: slider callbacks update config, recompute all derived views, then refresh display.
- Save/load keyboard shortcuts: `ctrl+e` writes the current config to `config.json`; `ctrl+l` loads `config.json`, syncs sliders, and refreshes the display.

## 7. Immediate Next TODOs

1. Run the app interactively and confirm the fullscreen guard still behaves as expected on the current backend.
2. Tune the now-separated parameters: `canny_thrd2`, `hough_circle_param1`, `hough_circle_param2`, and `hough_line_threshold`.
3. Watch whether seven fixed sliders still feel usable. If not, filter sliders by current debug view.
4. Decide whether saved configs should be ignored locally or committed as named examples.

## 8. Later TODOs

- Add named config paths or a small CLI option for choosing which JSON config to load/save.
- Add a clear parameter model after the base works: name, type, min, max, step, default, and affected computations.
- Extend `src/params.py` with optional view filtering or dependency metadata if fixed sliders become too crowded.
- Replace `recompute_all()` with a dependency map after the pipeline stabilizes, if performance or UI responsiveness needs it.
- Add preprocessing experiments: blur, thresholding, masking, ROI crop, dial center/radius estimation.
- Detect the needle line robustly and estimate its angle.
- Map needle angle to gauge value using calibration points.
- Improve needle line selection beyond the current "two longest segments" prototype.
- Handle tilted/perspective images with rectification or another geometric correction.
- Separate "detected geometry" from "debug rendering" more clearly once angle estimation starts.
- Add small tests for pure pipeline functions and state update behavior.
- Add CLI options for image path and config path.

## 9. Design Decisions Already Made

- Keep the architecture simple until the base pipeline works.
- `Display` can call `App`.
- `App` must not depend on `Display`.
- `Pipeline` must stay pure CV logic and must not depend on `App`, `State`, or `Display`.
- `State` should stay mostly passive storage.
- Use `results` for algorithmic data.
- Use `debug_views` for visualization.
- Overlays should draw on copies of the RGB source image.
- For now, correctness is more important than clever dependency tracking.
- A simple `recompute_all()` is acceptable before introducing a richer parameter/dependency model.
- `canny_thrd2`, `hough_circle_param1`, and `hough_line_threshold` are separate controls even if their default values sometimes look similar.
- `HoughLinesP` should receive the Canny edge image, not the grayscale image.
- Line detection should use edges masked by the selected circle when a circle is available.
- Current prototype angle strategy: intersect the two selected needle contour lines, then measure the angle from the detected circle center to that intersection.
- Fixed sliders are acceptable for now, but they are generated from `PARAM_SPECS` so the UI can evolve toward contextual sliders later.
- JSON is the first config format. Keep it simple until the parameter set stabilizes.
