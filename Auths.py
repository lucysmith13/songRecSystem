import os, pickle
from abc import ABC, abstractmethod
from flask.cli import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


load_dotenv()

class AuthBase(ABC):
    def __init__(self):
        self.access_token = None

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def get_credentials(self):
        pass

class SpotifyAuth(AuthBase):
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv("spotify_client_id")
        self.client_secret = os.getenv("spotify_client_secret")
        self.redirect_uri = os.getenv("redirect_uri")

        self.scope = ("user-read-private user-library-read user-top-read"
                      " playlist-modify-public playlist-modify-private")

        self.token_file = "spotify_token.pickle"
        self.access_token = None
        self.refresh_token = None

    def authenticate(self, code=None):
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as f:
                token_info = pickle.load(f)

            if not self._is_token_expired(token_info):
                self.access_token = token_info["access_token"]
                self.refresh_token = token_info.get("refresh_token")
                return self.access_token
            else:
                return self._refresh_access_token(token_info["refresh_token"])

        if code is None:
            from urllib.parse import urlencode

            params = {
                "client_id": self.client_id,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "scope": self.scope,
            }
            auth_url = "https://accounts.spotify.com/authorize?" + urlencode(params)
            print("\n Please login to Spotify using this link")
            print(auth_url)

            redirected_url = input("\n Paste the full redirect URL here after logging in:")
            from urllib.parse import urlparse, parse_qs
            code = parse_qs(urlparse(redirected_url).query)["code"][0]

            token_url = "https://accounts.spotify.com/api/token"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            import requests, time
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            token_info = response.json()

            token_info["expires_at"] = int(time.time()) + token_info.get("expires_in", 3600)

            self.access_token = token_info["access_token"]
            self.refresh_token = token_info.get("refresh_token")

            with open(self.token_file, "wb") as f:
                pickle.dump(token_info, f)

            return self.access_token

    def _refresh_access_token(self, refresh_token):
        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        import requests, time
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token_info = response.json()

        token_info["expires_at"] = int(time.time()) + token_info.get("expires_in", 3600)

        if "refresh_token" not in token_info:
            token_info["refresh_token"] = refresh_token

        self.access_token = token_info["access_token"]
        self.refresh_token = token_info.get("refresh_token", refresh_token)

        with open(self.token_file, "wb") as f:
            pickle.dump(token_info, f)

        return self.access_token

    def _is_token_expired(self, token_info):
        import time
        expires_at = token_info.get("expires_at")
        if not expires_at:
            expires_in = token_info.get("expires_in", 3600)
            expires_at = int(time.time()) + expires_in
            token_info["expires_at"] = expires_at
        return time.time() > expires_at

    def get_credentials(self):
        return self.client_id, self.client_secret, self.access_token, self.scope

    def get_access_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as f:
                token_info = pickle.load(f)

            if self._is_token_expired(token_info):
                return self._refresh_access_token(token_info["refresh_token"])
            else:
                return token_info["access_token"]

        return self.authenticate()

class YouTubeAuth(AuthBase):
    def __init__(self):
        super().__init__()
        self.scopes = ["https://www.googleapis.com/auth/youtube"]
        self.credentials = None
        self.client_secret_file = "client_secret.json"
        self.token_file = "youtube_token.pickle"

    def authenticate(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secret_file,
                scopes = self.scopes
            )
            self.credentials = flow.run_local_server(port=8080)
            with open(self.token_file, "wb") as token:
                pickle.dump(self.credentials, token)

        self.access_token = self.credentials.token
        return self.access_token

    def get_credentials(self):
        return self.credentials

class LastFMAuth(AuthBase):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("lastfm_api_key")

    def authenticate(self, **kwargs):
        if not self.api_key:
            raise ValueError("LastFM API key is missing")
        self.access_token = self.api_key
        return self.access_token

    def get_credentials(self):
        return self.api_key

class WeatherAPI(AuthBase):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("open_weather_api_key")

    def authenticate(self, **kwargs):
        if not self.api_key:
            raise ValueError("Open Weather API key is missing")
        self.access_token = self.api_key
        return self.access_token

    def get_credentials(self):
        return self.api_key