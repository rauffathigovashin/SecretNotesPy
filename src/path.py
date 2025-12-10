import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
DATA_DIR = os.path.join(ROOT_DIR, "data")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SRC_DIR = os.path.join(ROOT_DIR, "src")

ICON_PNG = os.path.join(IMAGES_DIR, "icon.png")