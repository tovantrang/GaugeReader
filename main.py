import cv2
import matplotlib.pyplot as plt

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


fig.canvas.mpl_connect("key_press_event", on_key)
manager = plt.get_current_fig_manager()
manager.window.attributes("-fullscreen", True)
plt.show()
