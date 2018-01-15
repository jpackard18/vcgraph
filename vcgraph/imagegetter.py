from datetime import datetime
from random import choice, choices
from .settings import STATIC_ROOT, STATIC_URL
import os


IMAGE_DIR = os.path.join(STATIC_ROOT, 'img')
IMAGE_URL = os.path.join(STATIC_URL, 'img')
SEASONS = ['winter', 'spring', 'summer', 'fall']


def get_season(dt):
    return SEASONS[(dt.month % 12 + 3) // 3 - 1]


def choose_image():
    season = get_season(datetime.now())
    # Enable for non-season based selection:
    # season = choice(SEASONS)
    if season == 'summer':
        folder = os.path.join(IMAGE_DIR, 'uncategorized')
    else:
        folder = os.path.join(IMAGE_DIR, choices([season, 'uncategorized'], [0.75, 0.25])[0])
    images = [file for file in os.listdir(folder) if file.endswith('.jpg')]
    return os.path.join(IMAGE_URL, os.path.basename(folder), choice(images)).replace("\\", "/")
