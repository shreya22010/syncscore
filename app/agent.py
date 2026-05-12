from groq import Groq
import os
import numpy as np
from dotenv import load_dotenv
from ml.predict import predict_mood, get_mood_description
 
load_dotenv()

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Create a key at https://console.groq.com/keys "
                "and add GROQ_API_KEY=... to a .env file in the project root (or export it in your shell)."
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def analyze_compatibility(user1_data, user2_data):
    mood1 = predict_mood(user1_data["audio_features"])
    mood2 = predict_mood(user2_data["audio_features"])
    compatibility = calculate_compatibility(user1_data, user2_data, mood1, mood2)
    artists1 = set(a.lower() for a in user1_data.get("top_artists", []))
    artists2 = set(a.lower() for a in user2_data.get("top_artists", []))
    shared_artists = list(artists1 & artists2)
    narrative, playlist = generate_narrative(user1_data, user2_data, mood1, mood2, compatibility)
    return {
        "mood1": mood1,
        "mood2": mood2,
        "compatibility_score": compatibility["score"],
        "breakdown": compatibility["breakdown"],
        "narrative": narrative,
        "shared_artists": shared_artists,
        "playlist": playlist,
    }
 
 
def calculate_compatibility(user1_data, user2_data, mood1, mood2):
    score = 0
    breakdown = {}
    genres1 = set(g.lower() for g in user1_data.get("genres", []))
    genres2 = set(g.lower() for g in user2_data.get("genres", []))
    if genres1 and genres2:
        overlap = len(genres1 & genres2)
        total = len(genres1 | genres2)
        genre_score = int((overlap / total) * 40) if total > 0 else 0
    else:
        genre_score = 0
    score += genre_score
    breakdown["genre_overlap"] = genre_score
    mood_pairs = {
        ("energetic", "energetic"): 30, ("calm", "calm"): 30,
        ("melancholic", "melancholic"): 30, ("tense", "tense"): 30,
        ("energetic", "calm"): 20, ("calm", "energetic"): 20,
        ("melancholic", "calm"): 18, ("calm", "melancholic"): 18,
        ("tense", "energetic"): 15, ("energetic", "tense"): 15,
        ("melancholic", "tense"): 10, ("tense", "melancholic"): 10,
    }
    mood_score = mood_pairs.get((mood1, mood2), 10)
    score += mood_score
    breakdown["mood_match"] = mood_score
    from ml.features import extract_avg_features
    f1 = extract_avg_features(user1_data["audio_features"])
    f2 = extract_avg_features(user2_data["audio_features"])
    if f1 and f2:
        keys = ["danceability", "energy", "valence", "acousticness"]
        diffs = [abs(f1[k] - f2[k]) for k in keys]
        avg_diff = np.mean(diffs)
        audio_score = int((1 - avg_diff) * 30)
    else:
        audio_score = 15
    score += audio_score
    breakdown["audio_similarity"] = audio_score
    return {"score": min(score, 100), "breakdown": breakdown}
 
 
def generate_narrative(user1_data, user2_data, mood1, mood2, compatibility):
    prompt = f"""You are SyncScore, a music compatibility analyst. Be direct and specific.
NO emojis. NO filler. NO generic statements.
 
Person 1: {user1_data['display_name']}
Mood: {mood1} — {get_mood_description(mood1)}
Genres: {', '.join(user1_data['genres'][:5]) or 'varied'}
 
Person 2: {user2_data['display_name']}
Mood: {mood2} — {get_mood_description(mood2)}
Genres: {', '.join(user2_data['genres'][:5]) or 'varied'}
 
Score: {compatibility['score']}/100
 
Write 3 short paragraphs: what their music says about each person, where they connect or diverge, where they'd clash. Under 130 words. No emojis.
 
Then on a new line write exactly: PLAYLIST: followed by 5 song recommendations in format "Artist - Song Title" separated by | that would suit both their tastes."""
 
    response = _get_groq_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )
    full = response.choices[0].message.content
    if "PLAYLIST:" in full:
        parts = full.split("PLAYLIST:")
        songs = [s.strip() for s in parts[1].strip().split("|") if s.strip()]
        return parts[0].strip(), songs[:5]
    return full.strip(), []