# GaugeReader

An interactive OpenCV prototype for exploring circle detection, edge detection, line detection, needle angle estimation, and manual gauge calibration. It works on the included examples, but it is **not robust or reliable enough for unattended measurement**.

## Run

```bash
python -m pip install -r requirements.txt
python main.py --example training
```

Try the second sample with `python main.py --example second`. Use your own image with `python main.py --image /path/to/gauge.jpg`.

## Explore the pipeline

The application opens on the source image. Use **left/right arrows** to browse grayscale, Canny edges, detected circles, masked edges, detected lines, and the needle overlay. Adjust the sliders to tune the classic CV stages.

On the needle view, press **1** and click the point representing the low gauge value, then press **2** and click the high-value point. Enter those values in the Low and High fields. The overlay then shows the estimated angle and interpolated gauge value. Press **d** to switch direction if the scale increases counter-clockwise. Press **Ctrl+E** to save the current settings to the local, ignored `config.json`; **Ctrl+L** reloads them. Press **q** to close.

## Tune a new gauge

Tune one stage at a time, moving through the views with the arrow keys. A useful first goal is to get one circle around the dial, then visible needle edges, then a plausible needle overlay. The sliders recompute the pipeline immediately.

1. **Find the dial circle.** Open the detected-circles view. The green circle should follow the dial rim and its center marker should sit near the dial center. Increase **Min radius** to rule out small circles such as the hub or printed details. Leave **Max radius** at `0` for no upper limit, or set it just above the dial radius if larger circles are being detected. If several circles remain, increase **Circle votes**; this makes Hough circle detection stricter. If no circle appears, lower it. **Circle Canny** is the edge threshold used internally by circle detection; lower it to admit weaker edges, or raise it to ignore weaker edges. It is separate from the two Canny sliders.
2. **Inspect Canny edges.** Open the Canny view and look for continuous edges along the needle and dial. **Canny low** and **Canny high** control edge sensitivity: lowering them usually reveals more weak edges and noise; raising them suppresses weak edges and can break faint edges. Tune them while watching this view. If the needle edges are missing, try lowering the thresholds. If the image is crowded with ticks and texture, try raising them. The high threshold should normally be at least as large as the low threshold.
3. **Check the masked edges and detected lines.** The circle mask limits line detection to the detected dial. In the lines view, look for segments that trace both sides of the needle. **Line votes** is the minimum Hough accumulator support: lower it to reveal more, shorter or weaker segments; raise it to keep fewer, stronger segments. If tick marks dominate, increasing it may help, though it can also remove the needle. If very few lines appear, lower it.
4. **Judge the needle overlay.** The current prototype chooses the two longest detected line segments and intersects them. Check that the selected segments actually follow the two edges of the needle and that the resulting tip lies on the needle. If not, return to Canny and line detection and adjust their thresholds. A plausible angle or value does not prove the detected lines are correct.
5. **Calibrate the value.** On the needle view, press `1` and click the point on the scale for the low value; press `2` and click the high-value point. Enter the corresponding numbers. Use `d` if increasing values run counter-clockwise. This is linear interpolation between two endpoints; it will not model a non-linear scale.

Save a successful setup with **Ctrl+E**. The saved `config.json` is local and ignored by Git. To share a preset, copy its settings into a new JSON file under `configs/examples/` and set its image path. The saved calibration points are pixel coordinates, so they only apply to that exact image and framing.

## Example images and configurations

Images live in `data/examples/`, with matching starter settings in `configs/examples/`. These settings are starting points, not guaranteed detections: image contrast, framing, glare, and gauge geometry affect Hough detection. Calibration points must be selected again for each new image.

The included presets are tuned starting points for the bundled images, not guarantees for other images. The pipeline can fail when the dial is tilted, partly hidden, low contrast, reflective, or too small. Circle detection may choose the wrong circle, and line detection may select ticks or other long edges instead of the needle. Calibration is manual and image-specific. Treat outputs as an experiment to inspect, not as trusted measurements.
