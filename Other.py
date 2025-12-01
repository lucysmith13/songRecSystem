import random, requests
from PIL import Image as PILImage
import requests
from io import BytesIO
from rich.console import Console
'''
Name: random_album_picker
Parameters: api_key1, api_key2, sp
Returns: None
Purpose: This function holds the multiple methods
needed for the random album picker. 
'''
def random_album_picker(api_key1, api_key2, sp):
    '''
    Name: generate_albums
    Parameters: None
    Returns: None or Chosen
    Purpose: This uses the Spotify API object to
    generate a random album from the user's saved
    library.
    '''
    def generate_albums():
        saved_albums = sp.current_user_saved_albums(limit=50)
        albums = saved_albums['items']
        if not albums:
            return None
        album_list = [item['album'] for item in albums]
        num = min(15, len(album_list))
        chosen = random.sample(album_list, num)
        return chosen

    '''
    Name: get_album_art
    Parameters: None
    Returns: name, artist, image_url
    Purpose: This gets the album art for the 
    one random album by searching for a url. 
    '''
    def get_album_art():
        albums = generate_albums()
        album = random.choice(albums)
        name = album['name']
        artist = ", ".join(artist['name'] for artist in album['artists'])
        image_url = album['images'][0]['url'] if album['images'] else None
        return name, artist, image_url

    '''
    Name: display
    Parameters: None
    Returns: None
    Purpose: This displays the album art in a new window
    view whilst displaying the album and artist name in the terminal
    '''
    def display():
        name, artist, image_url = get_album_art()
        if image_url:
            response = requests.get(image_url)
            img = PILImage.open(BytesIO(response.content))

            console = Console()
            console.print(f"{name} - {artist}")
            img.show()

    display()
