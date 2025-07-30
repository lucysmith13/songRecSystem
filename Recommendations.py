from abc import ABC, abstractmethod
import random
import requests

class BaseRecs(ABC):
    def __init__(self, api_key1):
        self.api_key1 = api_key1

    @abstractmethod
    def rec_algorithm(self, param1, param2):
        pass

    @abstractmethod
    def generate_recs(self):
        pass

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
                response.raise_for_status()
                data = response.json()
                return [tag['name'] for tag in data.get('similarTags', {}).get('tags', [])]
            except Exception as e:
                print(f"[ERROR] Exception while getting last fm genres: {e}")
                return []

        def get_top_tracks_for_genre(genre_tag):
            url = 'http://ws.audioscrobbler.com/2.0/'
            params = {
                'method': 'tag.getTopTracks',
                'tag': genre_tag,
                'api_key': self.lastfm_api_key,
                'format': 'json',
                'limit': limit,
            }
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get('tracks', {}).get('track', [])
            except Exception as e:
                print(f"[ERROR] Exception while getting top tracks for genre: {e}")
                return []

        similar_genres = get_similar_genre()
        genres_to_use = [genre] + similar_genres[:2]
        print(f"[DEBUG] Genres: {genres_to_use}")

        all_tracks = []
        seen_titles = set()

        for tag in genres_to_use:
            tracks = get_top_tracks_for_genre(tag)
            for t in tracks:
                track_name = t.get('name')
                artist_name = t.get('artist', {}).get('name', '')
                combined = f"{track_name} by {artist_name}"
                if combined not in seen_titles:
                    seen_titles.add(combined)
                    all_tracks.append(combined)
                if len(all_tracks) >= limit:
                    break

        self.recommended_tracks = all_tracks
        print(f"[DEBUG] Recommended tracks: {self.recommended_tracks}")
        return self.recommended_tracks

    def generate_recs(self):
        genre = input("Enter a genre: ")
        limit = int(input("Enter number of recommended tracks (less than 50): "))
        print(f"[DEBUG] {limit} {genre} songs")
        return self.rec_algorithm(genre, limit)

    def link_youtube_spotify(self):
        pass

    def upload_recs(self):
        pass

class UserRecs(BaseRecs):
    def __init__(self, api_key1):
        super().__init__(api_key1)

    def rec_algorithm(self, param1, param2):
        pass

    def generate_recs(self):
        pass

    def link_youtube_spotify(self):
        pass

    def upload_recs(self):
        pass

class SeasonRecs(BaseRecs):
    def __init__(self, api_key1):
        super().__init__(api_key1)

    def rec_algorithm(self, param1, param2):
        pass

    def generate_recs(self):
        pass

    def link_youtube_spotify(self):
        pass

    def upload_recs(self):
        pass

class WeatherRecs(BaseRecs):
    def __init__(self, api_key1):
        super().__init__(api_key1)

    def rec_algorithm(self, param1, param2):
        pass

    def generate_recs(self):
        pass

    def link_youtube_spotify(self):
        pass

    def upload_recs(self):
        pass



