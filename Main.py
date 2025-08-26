# Import Libraries
from spotipy import SpotifyOAuth

# Import files
from APIs import SpotifyAPI, YoutubeAPI, LastFMAPI
from Recommendations import GenreRecs, UserRecs, SeasonRecs, WeatherRecs
from Auths import LastFMAuth, SpotifyAuth
def main():
    def object_inst():
        # Auth objects
        lastfm = LastFMAuth()
        lastfm_key = lastfm.get_credentials()

        spotify = SpotifyAuth()
        id, secret, token, scope = spotify.get_credentials()
        sp = SpotifyOAuth(
            client_id = id,
            client_secret = secret,
            redirect_uri = 'http://127.0.0.1:8080/callback',
            scope = scope
        )


        # Recommendation Objects
        genre = GenreRecs(lastfm_key, None)
        user = UserRecs(None, None)
        season = SeasonRecs(lastfm_key, sp)
        weather = WeatherRecs(None, None)
        return genre, user, season, weather

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

    def recommendations(genre, user, season, weather):
        rec_choice = input("What type of recommendations? (Genre / User / Album / Seasonal / Weather)")
        if rec_choice.lower().startswith("g"):
            genre.generate_recs()
        elif rec_choice.lower().startswith("u"):
            user.generate_recs()
        elif rec_choice.lower().startswith("a"):
            pass
        elif rec_choice.lower().startswith("s"):
            season.generate_recs()
        elif rec_choice.lower().startswith("w"):
            weather.generate_recs()
        else:
            print("[DEBUG] Invalid recommendation input. ")

        if input("Would you like to add the recommendations to a playlist? ").lower().startswith("y"):
            # Run add to playlist function
            pass

    genre, user, season, weather = object_inst()
    test_spotify_auth()
    test_youtube_auth()
    recommendations(genre, user, season, weather)



if __name__ == '__main__':
    main()