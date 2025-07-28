# Import files
from APIs import SpotifyAPI, YoutubeAPI
def main():
    def test_spotify_auth():
        try:
            print("[DEBUG] Testing Spotify authentication...")
            spotify = SpotifyAPI()
            user_id, _, user_name = spotify.get_user_info()
            print(f"[DEBUG] Spotify Auth Successful: {user_name}")
        except Exception as e:
            print(f"[DEBUG] Spotify Auth Failed: {e}")

    def test_youtube_auth():
        try:
            print("[DEBUG] Testing YouTube authentication...")
            youtube = YoutubeAPI()
            user_name, _ = youtube.get_user_info()
            print(f"[DEBUG] YouTube Auth Successful: {user_name}")
        except Exception as e:
            print(f"[DEBUG] YouTube Auth Failed: {e}")

    def recommendations():
        rec_choice = input("What type of recommendations? (Genre / User / Album / Seasonal / Weather)")
        if rec_choice.lower().startswith("g"):
            pass
        elif rec_choice.lower().startswith("u"):
            pass
        elif rec_choice.lower().startswith("a"):
            pass
        elif rec_choice.lower().startswith("s"):
            pass
        elif rec_choice.lower().startswith("w"):
            pass
        else:
            print("[DEBUG] Invalid recommendation input. ")

    test_spotify_auth()
    test_youtube_auth()



if __name__ == '__main__':
    main()