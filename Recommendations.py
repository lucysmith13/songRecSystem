from abc import ABC, abstractmethod
import random, requests, socket
import datetime as dt
from datetime import datetime, time
import spotipy
from oauthlib.uri_validate import userinfo
from collections import defaultdict
import ipapi

from Auths import SpotifyAuth, YouTubeAuth, LastFMAuth

class BaseRecs(ABC):
    def __init__(self, api_key1, api_key2, credentials):
        self.api_key1 = api_key1
        self.api_key2 = api_key2
        self.credentials = credentials

    @abstractmethod
    def rec_algorithm(self, param1, param2):
        pass

    @abstractmethod
    def generate_recs(self):
        pass


class GenreRecs(BaseRecs):
    def __init__(self, api_key1, api_key2, spotify_auth: SpotifyAuth):
        super().__init__(api_key1, api_key2=None, credentials=None)
        self.lastfm_api_key = api_key1


        access_token = spotify_auth.get_access_token()
        self.sp = spotipy.Spotify(auth=access_token)

    def rec_algorithm(self, genre, limit):
        def get_similar_genre(genre):
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
                if response.status_code != 200:
                    print(f"[ERROR] Status Code: {response.status_code}")
                data = response.json()
                return [tag['name'] for tag in data.get('similarTags', {}).get('tag', [])]
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

        similar_genres = get_similar_genre(genre)
        print(similar_genres)
        genres_to_use = [genre] + similar_genres[:2]
        print(f"[DEBUG] Genres: {genres_to_use}")

        all_tracks = []
        seen_titles = set()
        uris = []

        for tag in genres_to_use:
            tracks = get_top_tracks_for_genre(tag)
            for t in tracks:
                track_name = t.get('name')
                artist_name = t.get('artist', {}).get('name', '')
                combined = f"{track_name} by {artist_name}"
                if combined not in seen_titles:
                    seen_titles.add(combined)
                    all_tracks.append(combined)

                    try:
                        query = f"track:{track_name} artist:{artist_name}"
                        results = self.sp.search(q=query, type='track', limit=1)
                        items = results.get('tracks', {}).get('items', [])
                        if items:
                            uris.append(items[0].get('uri'))
                    except Exception as e:
                        print(f"[ERROR] Couldn't fetch URI for {combined}: {e}")

                if len(all_tracks) >= limit:
                    break

        playlist_name = f"{genre} songs"

        self.recommended_tracks = all_tracks
        print(f"[DEBUG] Recommended tracks: {self.recommended_tracks}")


        return self.recommended_tracks, uris, playlist_name

    def generate_recs(self):
        genre = input("Enter a genre: ")
        limit = int(input("Enter number of recommended tracks (less than 50): "))
        print(f"[DEBUG] {limit} {genre} songs")

        recs, uris, playlist_name = self.rec_algorithm(genre, limit)
        return recs, uris, playlist_name



class UserRecs(BaseRecs):
    def __init__(self, api_key1, api_key2, spotify_auth: SpotifyAuth):
        super().__init__(api_key1, api_key2=None, credentials=None)
        self.lastfm_api_key = api_key1

        access_token = spotify_auth.get_access_token()
        self.sp = spotipy.Spotify(auth=access_token)

    def rec_algorithm(self, param1, param2):
        time_range = param1

        # Temp
        top_artist_limit = param2
        total_tracks_limit = 30


        print("[DEBUG] Fetching user's top artists...")
        top_artists = self.sp.current_user_top_artists(limit=top_artist_limit, time_range=time_range)
        top_artist_names = [artist['name'] for artist in top_artists['items']]
        print(f"[DEBUG] Top artists: {top_artist_names}")

        weighted_similar_artists = defaultdict(int)
        artist_to_similars = {}

        for rank, top_artist in enumerate(top_artist_names):
            weight = top_artist_limit - rank  # higher rank = more weight
            url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={top_artist}&api_key={self.lastfm_api_key}&format=json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                similars = data.get("similarartists", {}).get("artist", [])
                sim_names = [sim['name'] for sim in similars]
                artist_to_similars[top_artist] = sim_names
                for name in sim_names:
                    weighted_similar_artists[name] += weight
            elif response.status_code != 200:
                print(f"[WARNING] Failed to get similar artists for {top_artist}")
                continue

        sorted_similars = sorted(weighted_similar_artists.items(), key=lambda x: x[1], reverse=True)
        similar_artists = [name for name, _ in sorted_similars]

        must_include_artists = set()
        for sim_list in artist_to_similars.values():
            if sim_list:
                must_include_artists.add(sim_list[0])

        final_similar_artists = list(must_include_artists)
        for artist in similar_artists:
            if artist not in final_similar_artists:
                final_similar_artists.append(artist)
            if len(final_similar_artists) >= top_artist_limit * 2:
                break

        print(f"[DEBUG] Final similar artists: {final_similar_artists}")

        if not final_similar_artists:
            print("No final similar artists found, using top artists instead.")
            final_similar_artists = top_artist_names

        recommended_tracks = []
        seen_track_uris = set()
        tracks_per_artist = max(total_tracks_limit // len(final_similar_artists), 1)

        for artist_name in final_similar_artists:
            print(f"[DEBUG] Searching for artist on Spotify {artist_name}")
            search_results = self.sp.search(q=artist_name, type='artist', limit=1)
            print(f"[DEBUG] Spotify search result FOR {artist_name}.")

            if search_results['artists']['items']:
                artist_id = search_results['artists']['items'][0]['id']
                print(f"[DEBUG] Artist ID for {artist_name}: {artist_id}")

                top_tracks = self.sp.artist_top_tracks(artist_id)['tracks']
                #print(f"[DEBUG] Top tracks for {artist_name}: {top_tracks}")

                selected = 0
                for track in top_tracks:
                    if track['uri'] not in seen_track_uris and selected < tracks_per_artist:
                        recommended_tracks.append(track)
                        seen_track_uris.add(track['uri'])
                        selected += 1
            else:
                print(f"[ERROR] No artist found for search query {artist_name}")

        recommended_tracks = recommended_tracks[:total_tracks_limit]
        #print(f"[DEBUG] Tracks being added to recommendations: {recommended_tracks}")

        final_results = []
        final_results_uris = []
        for track in recommended_tracks:
            artist_names = ", ".join(artist['name'] for artist in track['artists'])
            final_results.append(f"{track['name']} by {artist_names}")
            final_results_uris.append(track['uri'])

        user_info = self.sp.me()
        username = user_info.get('display_name', 'Unknown User')
        playlist_name = f"{username}'s playlist"
        
        print(f"[DEBUG] Final recommended tracks: {final_results}")
        return final_results, final_results_uris, playlist_name

    def generate_recs(self):
        time_range = input("Time-Range: (short_term/medium_term/long_term) ")
        top_artist_limit = int(input("Top artist limit: "))
        recs, uris, playlist_name = self.rec_algorithm(time_range, top_artist_limit)
        return recs, uris, playlist_name


class SeasonRecs(BaseRecs):
    def __init__(self, api_key1, api_key2, spotify_auth: SpotifyAuth):
        super().__init__(api_key1, api_key2=None, credentials=None)
        self.lastfm_api_key = api_key1

        access_token = spotify_auth.get_access_token()
        self.sp = spotipy.Spotify(auth=access_token)

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
            genre = ["indie+pop", "post-punk", "blues", "folk", "acoustic"]
        if season == "summer":
            descrip = "summery"
            genre = ["reggae", "jungle", "hiphop", "pop-punk", "surf rock", "house"]
        if season == "autumn":
            descrip = "autumnal"
            genre = ["grunge", "classic+rock", "emo", "indie+rock", "jazz", "neo-soul", "ambient", "lo-fi"]
        if season == "winter":
            descrip = "winterly"
            genre = ["classical", "trip-hop", "post-rock", "industrial", "death+metal"]

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
            #print(f"[DEBUG] Searching for track on spotify: {name} by {artist}")
            items = result['tracks']['items']
            if items:
                uri = items[0]['uri']
                uris.append(uri)

        playlist_name = f"{random_genre} songs on a {descrip} {tod}"
        print(playlist_name)

        for track in recommendations:
            print(" -", track)

        return recommendations, uris, playlist_name

    def generate_recs(self):
        recs, uris, playlist_name = self.rec_algorithm(None, None)
        return recs, uris, playlist_name
        


class WeatherRecs(BaseRecs):
    def __init__(self, api_key1, api_key2, spotify_auth: SpotifyAuth):
        super().__init__(api_key1, api_key2, credentials=None)
        self.OPEN_WEATHER_KEY = api_key1
        self.last_fm_api_key = api_key2

        access_token = spotify_auth.get_access_token()
        self.sp = spotipy.Spotify(auth=access_token)

    def rec_algorithm(self, param1, param2):
        print(f"[DEBUG] Starting weather recommendations")

        def get_location():
            ip = requests.get("https://api.ipify.org").text
            print(f"[DEBUG] Public IP: {ip}")

            url = f"http://ip-api.com/json/{ip}?fields=city"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"[ERROR] Failed to get location. Status code: {response.status_code}")
                return None

            data = response.json()
            city = data['city']
            print(f"[DEBUG] City: {city}")
            return city

        city = get_location()

        country_code = "GB"

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={self.OPEN_WEATHER_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"[ERROR] Failed to get weather data. Status code :{response.status_code}")
            return [], [], ""

        data = response.json()
        weather = data['weather'][0]['main'].lower()
        detailed_weather = data['weather'][0]['description'].lower()
        print(f"[DEBUG] The weather is {weather}")

        genre_mapping = {
            "thunderstorm": ['ambient', 'industrial', 'gothic', 'metal', 'alternative-rock'],
            "drizzle": ['lo-fi', 'jazz', 'indie-pop', 'soul', 'ambient'],
            "rain": ['blues', 'acoustic', 'classical', 'chillwave'],
            "snow": ['classical', 'folk', 'dream-pop', 'ambient'],
            "atmosphere": ['ambient', 'chillwave', 'synthwave', 'post-rock'],
            "clear": ['pop', 'reggae', 'house', 'funk', 'indie-rock'],
            "clouds": ['indie', 'soft-rock', 'jazz', 'dream-pop']
        }

        if detailed_weather == "tornado":
            genre = ['hard-rock', 'heavy-metal', 'industrial', 'dubstep', 'drum-and-bass']
        else:
            # defualt genre pop if not found
            genre = genre_mapping.get(weather, ['pop'])

        print(f"[DEBUG] Selected genres: {genre}")
        genre_string = ", ".join(genre)

        url = 'http://ws.audioscrobbler.com/2.0/'
        params = {
            'method': 'tag.gettoptracks',
            'api_key': self.last_fm_api_key,
            'format': 'json',
        }

        recommendations = []
        uris = []
        tracks_per_genre = 30 // len(genre)

        for single_genre in genre:
            print(f"[DEBUG] Fetching tracks for genre: {single_genre}")
            params['tag'] = single_genre
            params['limit'] = tracks_per_genre
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"[ERROR] Failed to get tracks for genre {single_genre}")
                continue

            data = response.json()
            tracks = data.get('tracks', {}).get('track', [])
            if not tracks:
                print(f"[ERROR] No tracks found for genre: {single_genre}")
                continue

            count = 0

            for track in tracks:
                if count >= tracks_per_genre:
                    break

                name = track.get('name')
                artist = track.get('artist', {}).get('name')
                if not name or not artist:
                    print(f"[WARNING] Skipping track with missing name or artist.")
                recommendations.append(f"{name} by {artist}")
                query = f"{name} {artist}"
                print(f"[DEBUG] Searching for track on spotify: {name} by {artist}")
                result = self.sp.search(q=query, type='track', limit=5)
                items = result.get('tracks', {}).get('items', [])
                if items:
                    uri = items[0]['uri']
                    if uri not in uris:
                        uris.append(uri)
                        count += 1
                        if count >= tracks_per_genre:
                            break

        playlist_name = f"Songs for {weather}"
        recommendations = recommendations[:30]
        random.shuffle(recommendations)
        uris = uris[:30]
        print(f"[DEBUG] Final recommendations: {recommendations}")
        print(len(recommendations))
        genre_string = ", ".join(genre)

        return recommendations, uris, playlist_name

    def generate_recs(self):
        recs, uris, playlist_name = self.rec_algorithm(None, None)
        return recs, uris, playlist_name

