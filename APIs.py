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
'''
Name: SpotifyAPI
Purpose: This is to create objects of the Spotify web API object
and perform functions that work explicitly within Spotify.
Inherits from the base class - APIBase. 
'''
class SpotifyAPI(APIBase):
    def __init__(self):
        '''
        Name: __init__
        Parameters: None
        Returns: None
        Purpose: Initialises any variables needed for this class such as
        any authentication variables needed for api calls.
        '''
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

    '''
    Name: refresh_spotify
    Parameters: None
    Returns: None
    Purpose: Refreshes the access token using the .get_access_token method
    in the SpotifyAuth class. 
    '''
    def refresh_spotify(self):
        self.access_token = self.SpotifyAuth.get_access_token()
        self.spotify = spotipy.Spotify(auth=self.access_token)

    '''
    Name: add_to_playlist
    Parameters: playlist_name, track_uris
    Returns: playlist
    Purpose: Adds tracks generating my the rec algorithms from another class,
    to a playlist within the user's Spotify account using the Spotify Web API methods,
    also provides a playlist name for the playlist.
    '''
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

    '''
    Name: get_user_info
    Parameters:
    Returns: user_id, user_info, user_name
    Purpose: Gets user profile information from their spotify account profile
    that they have authenticated with.
    '''
    def get_user_info(self):
        self.refresh_spotify()
        user_id = self.spotify.current_user()['id']
        user_info = self.spotify.me()
        user_name = user_info.get('display_name', 'Unknown User')

        return user_id, user_info, user_name

    '''
    Name: get_track_info
    Parameters: uri
    Returns: name, artists
    Purpose: Gets name and artist of a single track uri using spotify.track.
    '''
    def get_track_info(self, uri):
        track = self.spotify.track(uri)
        name = track["name"]
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        return name, artists
'''
Name: YoutubeAPI
Purpose: This is a constructor to instantiate a YouTube API object with
specific methods to work explicitly within the YouTube Data API.
Inherits from the base class - APIBase
'''
class YoutubeAPI(APIBase):
    '''
    Name: __init__
    Parameters: None
    Returns: None
    Purpose: Initialises any variables needed for this class such as
    any authentication variables needed for api calls.
    '''
    def __init__(self):
        super().__init__("Youtube")
        self.YoutubeAuth = YouTubeAuth()
        self.YoutubeAuth.authenticate()
        credentials = self.YoutubeAuth.get_credentials()
        self.youtube = build('youtube', 'v3', credentials=credentials)
        self.video_id = None

    '''
    Name: set_video
    Parameters: video_id
    Returns: None
    Purpose: Sets the video_id parameter to a variable video_id which
    can be called for the YouTube API. 
    '''
    def set_video(self, video_id):
        self.video_id = video_id

    '''
    Name: search_video
    Parameters: query
    Returns: search["items"][0]["id"]["videoId"]
    Purpose: Searches for videos on YouTube API.
    '''
    def search_video(self, query):
        search = self.youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            maxResults=1
        ).execute()

        if not search["items"]:
            return None
        return search["items"][0]["id"]["videoId"]

    '''
    Name: create_playlist
    Parameters: playlist_name
    Returns: new_playlist["id"]
    Purpose: Creates a blank playlist with no songs currently 
    on it within the user's Spotify account. 
    '''
    def create_playlist(self, playlist_name):
        playlists = self.youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        ).execute()

        for playlist in playlists.get("items", []):
            if playlist["snippet"]["title"].lower() == playlist_name.lower():
                return playlist["id"]

        new_playlist = self.youtube.playlists().insert(
            part="snippet,status",
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
        return new_playlist["id"]

    '''
    Name: uris_to_ids
    Parameters: sp, uris
    Returns: video_ids
    Purpose: Method to convert the spotify URIs to 
    the YouTube video ids by searching youtube for the id. 
    '''
    def uris_to_ids(self, sp, uris):
        video_ids = []
        for uri in uris:
            name, artists = sp.get_track_info(uri)
            query = f"{name} {artists} official music video"

            vid = self.search_video(query)
            if vid:
                video_ids.append(vid)

        return video_ids

    ''' 
    Name: add_to_playlist
    Parameters: playlist_name, video_ids
    Returns: {
            "playlistId": playlist_id,
            "playlist_url": f"https://www.youtube.com/playlist?list={playlist_id}",
            "added_videos": len(video_ids),
            "responses": responses
        }
    Purpose: Uses my previous method create_playlist
    to create a blank playlist add then add the correct
    video_ids to the newly generated playlist. 
    '''
    def add_to_playlist(self, playlist_name, video_ids):
        if isinstance(video_ids, str):
            video_ids = [video_ids]

        playlist_id = self.create_playlist(playlist_name)

        responses = []
        for vid in video_ids:
            request = self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": vid
                        }
                    }
                }
            )
            responses.append(request.execute())

        print(f"[DEBUG] Playlist created: {playlist_name}")
        print(f"[DEBUG] Youtube Playlist URL: https://www.youtube.com/playlist?list={playlist_id}")

        return {
            "playlistId": playlist_id,
            "playlist_url": f"https://www.youtube.com/playlist?list={playlist_id}",
            "added_videos": len(video_ids),
            "responses": responses
        }
    '''
    Name: get_user_info
    Parameters: None
    Returns: user_info.get("title", "Unknown YouTube User"), user_info OR "Unknown YouTube", {}
    Purpose: 
    '''
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

'''
Name: LastFMAPI
Purpose: This is a constructor to instantiate a Last.fm API object with
specific methods to work explicitly within the Last.fm API.
This does not inherit from the APIBase class unlike the other APIs.  
'''
class LastFMAPI():
    '''
    Name: __init__
    Parameters: None
    Returns: None
    Purpose: Initialises any variables needed for this class such as
    any authentication variables needed for api calls.
    '''
    def __init__(self):
        self.LastFMAuth = LastFMAuth()
        self.api_key = self.LastFMAuth.get_credentials()

    '''
    Name: find_similar_artists
    Parameters: artist
    Returns: sim_names
    Purpose: Using the parameter artist, it searches last.fm
    to find similar artists to the original artist. 
    '''
    def find_similar_artists(self, artist):
        url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={artist}&api_key={self.api_key}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            similars = data.get("similarartists", {}).get("artist", [])
            sim_names = [sim['name'] for sim in similars]
            return sim_names