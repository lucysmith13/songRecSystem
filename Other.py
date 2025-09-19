import random, requests
from PIL import Image as PILImage
import requests
from io import BytesIO
from rich.console import Console

def random_album_picker(api_key1, api_key2, sp):
    def generate_albums():
        saved_albums = sp.current_user_saved_albums(limit=50)
        albums = saved_albums['items']
        if not albums:
            return None
        album_list = [item['album'] for item in albums]
        num = min(15, len(album_list))
        chosen = random.sample(album_list, num)
        return chosen

    def get_album_art():
        albums = generate_albums()
        album = random.choice(albums)
        name = album['name']
        artist = ", ".join(artist['name'] for artist in album['artists'])
        image_url = album['images'][0]['url'] if album['images'] else None
        return name, artist, image_url

    def display():
        name, artist, image_url = get_album_art()
        if image_url:
            response = requests.get(image_url)
            img = PILImage.open(BytesIO(response.content))

            console = Console()
            console.print(f"{name} - {artist}")
            img.show()

    display()
