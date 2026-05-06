import requests
import os
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_BASE = "https://ws.audioscrobbler.com/2.0/"

# Genre to audio feature mapping based on music research
GENRE_AUDIO_MAP = {
    "rock": {"energy": 0.8, "valence": 0.5, "danceability": 0.5, "acousticness": 0.2},
    "pop": {"energy": 0.7, "valence": 0.7, "danceability": 0.7, "acousticness": 0.3},
    "hip-hop": {"energy": 0.7, "valence": 0.6, "danceability": 0.8, "acousticness": 0.1},
    "hip hop": {"energy": 0.7, "valence": 0.6, "danceability": 0.8, "acousticness": 0.1},
    "electronic": {"energy": 0.85, "valence": 0.6, "danceability": 0.85, "acousticness": 0.05},
    "dance": {"energy": 0.85, "valence": 0.7, "danceability": 0.9, "acousticness": 0.05},
    "classical": {"energy": 0.2, "valence": 0.4, "danceability": 0.2, "acousticness": 0.95},
    "jazz": {"energy": 0.4, "valence": 0.6, "danceability": 0.5, "acousticness": 0.8},
    "metal": {"energy": 0.95, "valence": 0.3, "danceability": 0.4, "acousticness": 0.05},
    "indie": {"energy": 0.55, "valence": 0.55, "danceability": 0.55, "acousticness": 0.45},
    "alternative": {"energy": 0.65, "valence": 0.45, "danceability": 0.5, "acousticness": 0.3},
    "r&b": {"energy": 0.6, "valence": 0.65, "danceability": 0.75, "acousticness": 0.35},
    "soul": {"energy": 0.55, "valence": 0.65, "danceability": 0.65, "acousticness": 0.5},
    "folk": {"energy": 0.35, "valence": 0.55, "danceability": 0.4, "acousticness": 0.85},
    "country": {"energy": 0.55, "valence": 0.65, "danceability": 0.6, "acousticness": 0.7},
    "blues": {"energy": 0.45, "valence": 0.35, "danceability": 0.5, "acousticness": 0.7},
    "reggae": {"energy": 0.55, "valence": 0.75, "danceability": 0.75, "acousticness": 0.45},
    "bollywood": {"energy": 0.7, "valence": 0.75, "danceability": 0.75, "acousticness": 0.4},
    "ambient": {"energy": 0.2, "valence": 0.45, "danceability": 0.25, "acousticness": 0.8},
    "punk": {"energy": 0.9, "valence": 0.45, "danceability": 0.55, "acousticness": 0.05},
}

DEFAULT_FEATURES = {"energy": 0.5, "valence": 0.5, "danceability": 0.5, "acousticness": 0.5}

def get_artist_tags(artist_name):
    """Get genre tags for an artist from Last.fm."""
    try:
        response = requests.get(LASTFM_BASE, params={
            "method": "artist.gettoptags",
            "artist": artist_name,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }, timeout=5)
        data = response.json()
        tags = data.get("toptags", {}).get("tag", [])
        return [t["name"].lower() for t in tags[:8]]
    except:
        return []

def get_user_top_artists(username):
    """Get top artists for a Last.fm username."""
    try:
        response = requests.get(LASTFM_BASE, params={
            "method": "user.gettopartists",
            "user": username,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": 20,
            "period": "6month"
        }, timeout=8)
        data = response.json()
        artists = data.get("topartists", {}).get("artist", [])
        return [a["name"] for a in artists]
    except:
        return []

def get_user_top_tracks(username):
    """Get top tracks for a Last.fm username."""
    try:
        response = requests.get(LASTFM_BASE, params={
            "method": "user.gettoptracks",
            "user": username,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": 30,
            "period": "6month"
        }, timeout=8)
        data = response.json()
        tracks = data.get("toptracks", {}).get("track", [])
        return [{"name": t["name"], "artist": t["artist"]["name"]} for t in tracks]
    except:
        return []

def features_from_genres(genres):
    """
    Convert genre tags into audio features using our mapping.
    This is our ML feature engineering step.
    """
    if not genres:
        return DEFAULT_FEATURES.copy()
    
    totals = {"energy": 0, "valence": 0, "danceability": 0, "acousticness": 0}
    count = 0
    
    for genre in genres:
        for key in GENRE_AUDIO_MAP:
            if key in genre:
                for feat in totals:
                    totals[feat] += GENRE_AUDIO_MAP[key][feat]
                count += 1
                break
    
    if count == 0:
        return DEFAULT_FEATURES.copy()
    
    return {k: round(v / count, 3) for k, v in totals.items()}

def get_user_music_data(username):
    """
    Main function — given a Last.fm username,
    fetch their top artists, genres, tracks,
    and compute audio features.
    """
    # Check user exists
    try:
        response = requests.get(LASTFM_BASE, params={
            "method": "user.getinfo",
            "user": username,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }, timeout=8)
        data = response.json()
        if "error" in data:
            return None
        display_name = data["user"].get("name", username)
    except:
        return None

    # Get top artists
    top_artists = get_user_top_artists(username)
    
    # Get top tracks
    top_tracks = get_user_top_tracks(username)
    
    # Get genres from top 5 artists
    all_genres = []
    for artist in top_artists[:5]:
        tags = get_artist_tags(artist)
        all_genres.extend(tags)
    all_genres = list(set(all_genres))
    
    # Compute audio features from genres
    audio_features = [features_from_genres(all_genres)]
    audio_features[0]["instrumentalness"] = 0.1
    audio_features[0]["tempo"] = 120
    
    return {
        "display_name": display_name,
        "top_artists": top_artists,
        "top_tracks": top_tracks,
        "genres": all_genres,
        "audio_features": audio_features
    }