import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

ksize = 5
thrd1 = 100
thrd2 = 200

image = cv2.imread("training_gauge.png")
assert image is not None, "file not read"

image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image_blur = cv2.blur(image_gray, (ksize, ksize))
image_gauss = cv2.GaussianBlur(image_gray, (ksize, ksize), 0)
edges = cv2.Canny(image_gray, thrd1, thrd2)
edges_blur = cv2.Canny(image_blur, thrd1, thrd2)
edges_gauss = cv2.Canny(image_gauss, thrd1, thrd2)

images = [
    ("RGB", image_rgb, None),
    ("Gray", image_gray, "gray"),
    ("Blur", image_blur, "gray"),
    ("Gauss", image_gauss, "gray"),
    ("Edges", edges, "gray"),
    ("Edges blur", edges_blur, "gray"),
    ("Edges gauss", edges_gauss, "gray"),
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


def update_canny(val):
    global thrd1, thrd2
    thrd1 = slider_thrd1.val
    thrd2 = slider_thrd2.val
    images[4] = ("Edges", cv2.Canny(image_gray, thrd1, thrd2), "gray")
    images[5] = ("Edges blur", cv2.Canny(image_blur, thrd1, thrd2), "gray")
    images[6] = ("Edges gauss", cv2.Canny(image_gauss, thrd1, thrd2), "gray")
    if current >= 4:
        update_display()


plt.subplots_adjust(bottom=0.25)
ax_thrd1 = plt.axes([0.25, 0.1, 0.65, 0.03])
ax_thrd2 = plt.axes([0.25, 0.15, 0.65, 0.03])
slider_thrd1 = Slider(ax_thrd1, "Threshold 1", 0, 500, valinit=thrd1)
slider_thrd2 = Slider(ax_thrd2, "Threshold 2", 0, 500, valinit=thrd2)
slider_thrd1.on_changed(update_canny)
slider_thrd2.on_changed(update_canny)

fig.canvas.mpl_connect("key_press_event", on_key)
manager = plt.get_current_fig_manager()
manager.window.attributes("-fullscreen", True)
plt.show()
