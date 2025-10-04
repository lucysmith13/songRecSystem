# Import Libraries
from spotipy import SpotifyOAuth
import spotipy

# Import files
from APIs import SpotifyAPI, YoutubeAPI, LastFMAPI
from NEA.songRecSystem.Other import random_album_picker
from Recommendations import GenreRecs, UserRecs, SeasonRecs, WeatherRecs
from Auths import LastFMAuth, SpotifyAuth, WeatherAPI
import Other

def main():
    def object_inst():
        # Auth objects
        lastfm = LastFMAuth()
        lastfm_key = lastfm.get_credentials()

        open_weather = WeatherAPI()
        open_weather_key = open_weather.get_credentials()

        spotify_auth = SpotifyAuth()
        access_token = spotify_auth.get_access_token()
        sp = spotipy.Spotify(auth=access_token)

        # Recommendation Objects
        genre = GenreRecs(lastfm_key, None, spotify_auth)
        user = UserRecs(lastfm_key, None, spotify_auth)
        season = SeasonRecs(lastfm_key, None, spotify_auth)
        weather = WeatherRecs(open_weather_key, lastfm_key, spotify_auth)

        # API instantiation
        spotifyAPI = SpotifyAPI()
        youtubeAPI = YoutubeAPI()

        return genre, user, season, weather, spotifyAPI, youtubeAPI, sp

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
        while True:
            while True:
                rec_choice = input("What type of recommendations? (Genre / User / Album / Seasonal / Weather)")
                if rec_choice.lower().startswith("g"):
                    recs, uris, playlist_name  = genre.generate_recs()
                    break
                elif rec_choice.lower().startswith("u"):
                    recs, uris, playlist_name = user.generate_recs()
                    break
                elif rec_choice.lower().startswith("a"):
                    random_album_picker(None, None, sp)
                    break
                elif rec_choice.lower().startswith("s"):
                    recs, uris, playlist_name = season.generate_recs()
                    break
                elif rec_choice.lower().startswith("w"):
                    recs, uris, playlist_name = weather.generate_recs()
                    break
                else:
                    print("[DEBUG] Invalid recommendation input. ")
                    continue

            if not rec_choice.lower().startswith("a"):
                if input("Would you like to add the recommendations to a playlist? ").lower().startswith("y"):
                    APIChoice = input("Youtube or Spotify or Both?")
                    if APIChoice.lower().startswith("y"):
                        video_ids = youtubeAPI.uris_to_ids(spotifyAPI, uris)
                        youtubeAPI.add_to_playlist(playlist_name, video_ids)
                    elif APIChoice.lower().startswith("s"):
                        if uris:
                            print("URIs to add:", uris)
                            spotifyAPI.add_to_playlist(playlist_name, uris)
                        else:
                            print("[ERROR] No songs to add. ")
                    else:
                        spotifyAPI.add_to_playlist(playlist_name, uris)
                        video_ids = youtubeAPI.uris_to_ids(spotifyAPI, uris)
                        youtubeAPI.add_to_playlist(playlist_name, video_ids)

            if input("Press Q to end recommendations. Or click enter to continue. ").lower().startswith("q"):
                break

    genre, user, season, weather, spotifyapi, youtubeapi, sp = object_inst()
    test_spotify_auth()
    test_youtube_auth()
    recommendations(genre, user, season, weather, spotifyapi, youtubeapi)



if __name__ == '__main__':
    main()