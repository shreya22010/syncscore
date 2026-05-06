import joblib
import numpy as np
import os
from ml.features import extract_avg_features, features_to_array

def load_model():
    model_path = os.path.join("models", "mood_classifier.pkl")
    return joblib.load(model_path)

def predict_mood(audio_features):
    """
    Takes a list of Spotify audio feature dicts,
    averages them, and returns the predicted mood.
    """
    model = load_model()
    
    avg_features = extract_avg_features(audio_features)
    if avg_features is None:
        return "unknown"
    
    feature_array = features_to_array(avg_features).reshape(1, -1)
    mood = model.predict(feature_array)[0]
    
    return mood

def get_mood_description(mood):
    """Returns a human-readable description of each mood."""
    descriptions = {
        "energetic": "high energy, upbeat, and positive",
        "calm": "relaxed, peaceful, and content",
        "melancholic": "reflective, emotional, and introspective",
        "tense": "intense, driven, and edgy"
    }
    return descriptions.get(mood, "balanced and varied")