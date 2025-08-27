from abc import ABC, abstractmethod
import random, requests
import datetime as dt
from datetime import datetime, time

class BaseRecs(ABC):
    def __init__(self, api_key1, credentials):
        self.api_key1 = api_key1
        self.credentials = credentials

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
    def __init__(self, api_key1, credentials):
        super().__init__(api_key1, credentials=None)
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
    def __init__(self, api_key1, credentials):
        super().__init__(api_key1, credentials=None)

    def rec_algorithm(self, param1, param2):
        pass

    def generate_recs(self):
        pass

    def link_youtube_spotify(self):
        pass

    def upload_recs(self):
        pass

class SeasonRecs(BaseRecs):
    def __init__(self, api_key1, credentials):
        super().__init__(api_key1, credentials)
        self.lastfm_api_key = api_key1
        self.credentials = credentials

    def rec_algorithm(self, param1, param2):
        hour = dt.datetime.now().hour
        if 5 <= hour < 12:
            tod = "morning"
        elif 12 <= hour < 18:
            tod = "afternoon"
        elif 18 <= hour < 21:
            tod = "evening"
        else:
            tod = "night"

        month = dt.datetime.now().month
        today = dt.date.today()

        if 3 <= month <= 5:
            season = "spring"
        elif 6 <= month <= 8:
            season = "summer"
        elif 9 <= month <= 11:
            season = "autumn"
        else:
            season = "winter"

        if today == dt.date(today.year, 12, 25):
            # its christmas!
            genre = ["christmas"]
        if season == "spring":
            descrip = "spring-like"
            genre = ["indie-pop", "post-punk", "blues", "folk", "acoustic"]
        if season == "summer":
            descrip = "summery"
            genre = ["reggae", "jungle", "hiphop", "pop-punk", "surf rock", "house"]
        if season == "autumn":
            descrip = "autumnal"
            genre = ["grunge", "classic-rock", "emo", "indie-rock", "jazz", "neo-soul", "ambient", "lo-fi"]
        if season == "winter":
            descrip = "winterly"
            genre = ["classical", "trip-hop", "post-rock", "industrial", "death-metal"]

        random_genre = random.choice(genre)

        url = 'http://ws.audioscrobbler.com/2.0/'
        params = {
            'method': 'tag.gettoptracks',
            'tag': random_genre,
            'api_key': self.lastfm_api_key,
            'format': 'json',
            'limit': 30
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"[ERROR] Failed to get recommendations for {genre}")
            print(f"Status code: {response.status_code}")
            print(f"Response text: {response.text}")
            return []

        data = response.json()
        tracks = data.get('tracks', {}).get('track', [])
        recommendations = []
        uris = []
        for track in tracks:
            name = track.get('name')
            artist = track.get('artist', {}).get('name')
            recommendations.append(f"{name} by {artist}")
            query = f"{name} {artist}"

            result = self.sp.search(q=query, type='track', limit=30)
            print(f"[DEBUG] Searching for track on spotify: {name} by {artist}")
            items = result['tracks']['items']
            if items:
                uri = items[0]['uri']
                uris.append(uri)

        playlist_name = f"{random_genre} songs on a {descrip} {tod}"
        print(playlist_name)

        print(playlist_name)
        for track in recommendations:
            print(" -", track)

        return recommendations, uris, playlist_name

    def generate_recs(self):
        recs, uris, playlist_name = self.rec_algorithm(None, None)
        return recs, uris, playlist_name
        

    def link_youtube_spotify(self):
        pass

    def upload_recs(self):
        pass

class WeatherRecs(BaseRecs):
    def __init__(self, api_key1, credentials):
        super().__init__(api_key1, credentials=None)

    def rec_algorithm(self, param1, param2):
        pass

    def generate_recs(self):
        pass

    def link_youtube_spotify(self):
        pass

    def upload_recs(self):
        pass



