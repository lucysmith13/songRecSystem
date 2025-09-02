# Import Libraries
from spotipy import SpotifyOAuth
import spotipy

# Import files
from APIs import SpotifyAPI, YoutubeAPI, LastFMAPI
from Recommendations import GenreRecs, UserRecs, SeasonRecs, WeatherRecs
from Auths import LastFMAuth, SpotifyAuth
def main():
    def object_inst():
        # Auth objects
        lastfm = LastFMAuth()
        lastfm_key = lastfm.get_credentials()

        spotify_auth = SpotifyAuth()
        access_token = spotify_auth.get_access_token()
        sp = spotipy.Spotify(auth=access_token)

        # Recommendation Objects
        genre = GenreRecs(lastfm_key, spotify_auth)
        user = UserRecs(None, spotify_auth)
        season = SeasonRecs(lastfm_key, spotify_auth)
        weather = WeatherRecs(None, spotify_auth)

        # API instantiation
        spotifyAPI = SpotifyAPI()
        youtubeAPI = YoutubeAPI()

        return genre, user, season, weather, spotifyAPI, youtubeAPI

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

    def recommendations(genre, user, season, weather, spotifyAPI, youtubeAPI):
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
            spotifyAPI.add_to_playlist()
            #youtubeAPI.add_to_playlist()

    genre, user, season, weather, spotifyapi, youtubeapi = object_inst()
    test_spotify_auth()
    test_youtube_auth()
    recommendations(genre, user, season, weather, spotifyapi, youtubeapi)



if __name__ == '__main__':
    main()