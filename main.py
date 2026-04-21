import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

ksize = 5
thrd1 = 95
thrd2 = 360
min_radius = 0
max_radius = 0

image = cv2.imread("training_gauge.png")
assert image is not None, "file not read"

image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# image_blur = cv2.blur(image_gray, (ksize, ksize))
# image_gauss = cv2.GaussianBlur(image_gray, (ksize, ksize), 0)
edges = cv2.Canny(image_gray, thrd1, thrd2)
# edges_blur = cv2.Canny(image_blur, thrd1, thrd2)
# edges_gauss = cv2.Canny(image_gauss, thrd1, thrd2)
contours = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
circles = cv2.HoughCircles(
    image_gray,
    cv2.HOUGH_GRADIENT,
    1,
    20,
    param1=thrd2,
    param2=thrd1,
    minRadius=min_radius,
    maxRadius=max_radius,
)
circles = np.uint16(np.around(circles))
for i in circles[0, :]:
    # draw the outer circle
    cv2.circle(image_rgb, (i[0], i[1]), i[2], (0, 255, 0), 2)
    # draw the center of the circle
    cv2.circle(image_rgb, (i[0], i[1]), 2, (0, 0, 255), 3)

full_circle_mask = np.zeros_like(image_gray)
for i in circles[0, :]:
    cv2.circle(full_circle_mask, (i[0], i[1]), i[2], 255, -1)
masked_edges = cv2.bitwise_and(edges, full_circle_mask)
lines = cv2.HoughLinesP(
    masked_edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10
)
image_with_lines = image_rgb.copy()
for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(image_with_lines, (x1, y1), (x2, y2), (255, 0, 0), 2)

images = [
    ("Gauge circle", image_rgb, None),
    ("Lines", image_with_lines, None),
    ("Gray", image_gray, "gray"),
    # ("Blur", image_blur, "gray"),
    # ("Gauss", image_gauss, "gray"),
    ("Edges", edges, "gray"),
    # ("Edges blur", edges_blur, "gray"),
    # ("Edges gauss", edges_gauss, "gray"),
    (
        "Contours",
        cv2.drawContours(image_rgb.copy(), contours, -1, (0, 255, 0), 2),
        None,
    ),
]

current = 0

fig, ax = plt.subplots()
img_artist = ax.imshow(
    images[current][1],
    cmap=images[current][2],
    vmin=0,
    vmax=255 if images[current][2] == "gray" else None,
)
ax.set_title(images[current][0])
ax.axis("off")


def update_display():
    title, img, cmap = images[current]
    img_artist.set_data(img)
    img_artist.set_cmap(cmap)
    if cmap == "gray":
        img_artist.set_clim(0, 255)
    ax.set_title(title)
    fig.canvas.draw_idle()


def on_key(event):
    global current
    if event.key == "right":
        current = (current + 1) % len(images)
        update_display()
    elif event.key == "left":
        current = (current - 1) % len(images)
        update_display()
    elif event.key == "q":
        plt.close(fig)


def redraw_circles():
    circles = cv2.HoughCircles(
        image_gray,
        cv2.HOUGH_GRADIENT,
        1,
        20,
        param1=thrd2,
        param2=thrd1,
        minRadius=min_radius,
        maxRadius=max_radius,
    )
    circles = np.uint16(np.around(circles))
    img_rgb_copy = image_rgb.copy()
    for i in circles[0, :]:
        # draw the outer circle
        cv2.circle(img_rgb_copy, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(img_rgb_copy, (i[0], i[1]), 2, (0, 0, 255), 3)
    images[0] = ("Gauge circle", img_rgb_copy, None)


def update_canny():
    global thrd1, thrd2
    thrd1 = slider_thrd1.val
    thrd2 = slider_thrd2.val
    images[2] = ("Edges", cv2.Canny(image_gray, thrd1, thrd2), "gray")
    images[3] = (
        "Contours",
        cv2.drawContours(
            image_rgb.copy(),
            cv2.findContours(
                cv2.Canny(image_gray, thrd1, thrd2),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )[0],
            -1,
            (0, 255, 0),
            2,
        ),
        None,
    )
    redraw_circles()
    # images[5] = ("Edges blur", cv2.Canny(image_blur, thrd1, thrd2), "gray")
    # images[6] = ("Edges gauss", cv2.Canny(image_gauss, thrd1, thrd2), "gray")
    if current in [
        0,
        2,
        3,
    ]:  # Update display if currently showing RGB, Edges, or Contours
        update_display()


def update_hough():
    global min_radius, max_radius
    min_radius = int(slider_min_radius.val)
    max_radius = int(slider_max_radius.val)
    redraw_circles()
    if current == 0:
        update_display()


def update_lines():
    pass


plt.subplots_adjust(bottom=0.25)
ax_thrd1 = plt.axes([0.25, 0.15, 0.65, 0.03])
ax_thrd2 = plt.axes([0.25, 0.1, 0.65, 0.03])
ax_min_radius = plt.axes([0.25, 0.05, 0.65, 0.03])
ax_max_radius = plt.axes([0.25, 0.0, 0.65, 0.03])
slider_thrd1 = Slider(ax_thrd1, "Threshold 1", 0, 500, valinit=thrd1)
slider_thrd2 = Slider(ax_thrd2, "Threshold 2", 0, 500, valinit=thrd2)
slider_min_radius = Slider(
    ax_min_radius, "Min Radius", 0, 100, valinit=min_radius, valfmt="%i"
)
slider_max_radius = Slider(
    ax_max_radius, "Max Radius", 0, 100, valinit=max_radius, valfmt="%i"
)
slider_thrd1.on_changed(update_canny)
slider_thrd2.on_changed(update_canny)
slider_min_radius.on_changed(update_hough)
slider_max_radius.on_changed(update_hough)

fig.canvas.mpl_connect("key_press_event", on_key)
manager = plt.get_current_fig_manager()
manager.window.attributes("-fullscreen", True)
plt.show()
