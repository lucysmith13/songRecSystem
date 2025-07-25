from abc import ABC, abstractmethod

from google.auth.transport import requests

class BaseRecs(ABC):
    def __init__(self, api_key1):
        self.api_key1 = api_key1

    @abstractmethod
    def rec_algorithm(self, param1, param2):
        pass

    @abstractmethod
    def generate_recs(self):

    @abstractmethod
    def link_youtube_spotify(self):
        pass

    @abstractmethod
    def upload_recs(self):
        pass

class GenreRecs(BaseRecs):
    def __init__(self, api_key1):
        super().__init__(api_key1)
        self.lastfm_api_key = api_key1


    def rec_algorithm(self, genre, limit):
        def get_similar_genre():
            url = 'http://ws.audioscrobbler.com/2.0/'
            params = {
                'method': 'tag.getSimilar',
                'tag': genre,
                'api_key': self.lastfm_api_key,
                'format': 'json'
            }
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    similar = data.get('similarTags', {}).get("tag", [])
                    if similar:
                        return [tag['name'] for tag in similar]
            except Exception as e:
                print(f"[ERROR] Exception while getting last fm genres: {e}")

        similar_genre_weights = get_similar_genre(genre)
        similar_genres = similar_genre_weights.keys()
        similar_genres = list(similar_genres)
        random.shuffle(similar_genres)
        similar_genres = similar_genres[:2]
        print(f"[DEBUG] Similar genres to {genre}: {similar_genres}")
        genres = [genre] + similar_genres

        genre_string = ", ".join(genres)

        top_tracks = []
        uris = []
        seen_tracks = set()
        seen_artists = set()
        all_artists = []
        url = 'http://ws.audioscrobbler.com/2.0/'

        for genre in sorted(genres)

    def generate_recs(self):
        pass

class UserRecs(BaseRecs):
    def __init__(self):
        super().__init__()

    def rec_algorithm(self, param1, param2):
        pass

class SeasonRecs(BaseRecs):
    def __init__(self):
        super().__init__()

    def rec_algorithm(self, param1, param2):
        pass

class WeatherRecs(BaseRecs):
    def __init__(self):
        super().__init__()

    def rec_algorithm(self, param1, param2):
        pass



