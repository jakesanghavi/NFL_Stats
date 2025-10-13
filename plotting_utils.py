import requests
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from pathlib import Path
import os


def get_player_headshot(player_id):
    filename = Path.cwd() / "Headshots" / f"{player_id}.png"

    if os.path.exists(filename):
        return plt.imread(filename)

    url = f"https://assets.nflallday.com/resize/static/images/players-headshots/{player_id}.png?format=webp&quality=80&width=256"

    response = requests.get(url)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))
    image.save(filename)

    return plt.imread(BytesIO(response.content), format='PNG')
