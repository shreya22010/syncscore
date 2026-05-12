from ml.features import extract_avg_features, label_mood

def predict_mood(audio_features):
    """
    Averages Spotify audio features across a user's tracks and maps
    the (valence, energy) pair to one of four mood quadrants.
    """
    avg_features = extract_avg_features(audio_features)
    if avg_features is None:
        return "unknown"
    return label_mood(avg_features["valence"], avg_features["energy"])

def get_mood_description(mood):
    """Returns a human-readable description of each mood."""
    descriptions = {
        "energetic": "high energy, upbeat, and positive",
        "calm": "relaxed, peaceful, and content",
        "melancholic": "reflective, emotional, and introspective",
        "tense": "intense, driven, and edgy"
    }
    return descriptions.get(mood, "balanced and varied")