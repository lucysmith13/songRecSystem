# Import Libraries
from abc import ABC, abstractmethod
import spotipy
import requests
from googleapiclient.discovery import build

# Import Files
from Auths import SpotifyAuth, YouTubeAuth, LastFMAuth

class APIBase(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def add_to_playlist(self, playlist_name,track_uris):
        pass

    @abstractmethod
    def get_user_info(self):
        pass

class SpotifyAPI(APIBase):
    def __init__(self):
        super().__init__("Spotify")
        self.SpotifyAuth = SpotifyAuth()

        self.access_token = self.SpotifyAuth.get_access_token()
        self.spotify = spotipy.Spotify(auth=self.access_token)

        try:
            self.user_id = self.spotify.current_user()['id']
        except spotipy.exceptions.SpotifyException:
            print("[DEBUG] Token was expired. Refreshing now...")
            self.access_token = self.SpotifyAuth.get_access_token()
            self.spotify = spotipy.Spotify(auth=self.access_token)
            self.user_id = self.spotify.current_user()['id']


    def refresh_spotify(self):
        self.access_token = self.SpotifyAuth.get_access_token()
        self.spotify = spotipy.Spotify(auth=self.access_token)

    def add_to_playlist(self, playlist_name, track_uris):
        if not track_uris:
            raise ValueError("track uris missing.")

        self.refresh_spotify()

        playlist = self.spotify.user_playlist_create(
            user = self.user_id,
            name = playlist_name,
            public = False,
            description = "Created by Lucy's song recommendation system."
        )

        playlist_url = playlist["external_urls"]["spotify"]

        self.spotify.playlist_add_items(playlist["id"], track_uris)
        print(f"[DEBUG] Playlist created: {playlist_name}")
        print(f"[DEBUG] Spotify playlist URL: {playlist_url}")
        return playlist

    def get_user_info(self):
        self.refresh_spotify()
        user_id = self.spotify.current_user()['id']
        user_info = self.spotify.me()
        user_name = user_info.get('display_name', 'Unknown User')

        return user_id, user_info, user_name


class YoutubeAPI(APIBase):
    def __init__(self):
        super().__init__("Youtube")
        self.YoutubeAuth = YouTubeAuth()
        self.YoutubeAuth.authenticate()
        credentials = self.YoutubeAuth.get_credentials()
        self.youtube = build('youtube', 'v3', credentials=credentials)
        self.video_id = None

    def set_video(self, video_id):
        self.video_id = video_id

    def add_to_playlist(self, playlist_name, playlist_id, *_):
        if not self.video_id:
            raise ValueError("No video selected, make sure to use set_video first.")

        playlists = self.youtube.playlists().list(
            part='snippet,contentDetails',
            mine=True,
            maxResults=50,
        ).execute()

        playlist_id = None
        for playlist in playlists.get("items", []):
            if playlist["snippet"]["title"].lower() == playlist_name.lower():
                playlist_id = playlist["id"]
                break

        if not playlist_id:
            new_playlist = self.youtube.playlists().insert(
                part='snippet,status',
                body={
                    "snippet": {
                        "title": playlist_name,
                        "description": "Created by Lucy's song recommendation system.",
                    },
                    "status": {
                        "privacyStatus": "private",
                    }
                }
            ).execute()
            playlist_id = new_playlist["id"]

            request = self.youtube.playlistItems.insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": self.video_id,
                        }
                    }
                }
            )

            response = request.execute()
            return {
                "playlist_id": playlist_id,
                "playlist_url": f"https://www.youtube.com/playlist?list={playlist_id}",
                "response": response,
            }

    def get_user_info(self):
        channels_response = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        ).execute()

        if channels_response['items']:
            user_info = channels_response['items'][0]["snippet"]
            return user_info.get("title", "Unknown YouTube User"), user_info
        else:
            return "Unknown YouTube", {}

class LastFMAPI():
    def __init__(self):
        self.LastFMAuth = LastFMAuth()
        self.api_key = self.LastFMAuth.get_credentials()

    def find_similar_artists(self, artist):
        url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={artist}&api_key={self.api_key}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            similars = data.get("similarartists", {}).get("artist", [])
            sim_names = [sim['name'] for sim in similars]
            return sim_names