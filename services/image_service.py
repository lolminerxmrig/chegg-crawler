import pyautogui
from PIL import Image


def get_resolution():
    img = "web.png"
    im = Image.open(img)
    x, y = im.size
    screen_x, screen_y = pyautogui.size()
    print(screen_x)
    dx = screen_x / x
    dy = screen_y / y
    return dx, dy
