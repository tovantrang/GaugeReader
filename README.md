# GaugeReader

An interactive OpenCV prototype that explores circle detection, edge detection, line detection, needle angle estimation, and manual gauge calibration.

## Run

```bash
python -m pip install -r requirements.txt
python main.py --example training
```

Try the second sample with `python main.py --example second`. Use your own image with `python main.py --image /path/to/gauge.jpg`.

## Explore the pipeline

The application opens on the source image. Use **left/right arrows** to browse grayscale, Canny edges, detected circles, masked edges, detected lines, and the needle overlay. Adjust the sliders to tune the classic CV stages.

On the needle view, press **1** and click the point representing the low gauge value, then press **2** and click the high-value point. Enter those values in the Low and High fields. The overlay then shows the estimated angle and interpolated gauge value. Press **d** to switch direction if the scale increases counter-clockwise. Press **Ctrl+E** to save the current settings to the local, ignored `config.json`; **Ctrl+L** reloads them. Press **q** to close.

## Example images and configurations

Images live in `data/examples/`, with matching starter settings in `configs/examples/`. These settings are starting points, not guaranteed detections: image contrast, framing, glare, and gauge geometry affect Hough detection. Calibration points must be selected again for each new image.

The needle detector is a prototype: it selects the two longest Hough line segments and intersects them. It can mistake tick marks or other long edges for the needle. The value mapping interpolates between the two manually selected endpoints and does not recognize scale markings or non-linear scales.
