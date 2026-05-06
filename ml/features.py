import numpy as np

def extract_avg_features(audio_features):
    """
    Takes a list of audio feature dicts from Spotify
    and returns the average values as a single feature vector.
    This is what we feed into the ML model.
    """
    if not audio_features:
        return None
    
    keys = ["danceability", "energy", "valence", 
            "acousticness", "instrumentalness", "tempo"]
    
    averages = {}
    for key in keys:
        values = [f[key] for f in audio_features if f and key in f]
        averages[key] = np.mean(values) if values else 0.0
    
    # Normalize tempo to 0-1 range (tempo is usually 60-200 BPM)
    averages["tempo"] = averages["tempo"] / 200.0
    
    return averages

def features_to_array(feature_dict):
    """Converts feature dict to a numpy array for the ML model."""
    keys = ["danceability", "energy", "valence", 
            "acousticness", "instrumentalness", "tempo"]
    return np.array([feature_dict[k] for k in keys])

def label_mood(valence, energy):
    """
    Maps valence + energy values to a mood label.
    This is based on the standard emotion quadrant model
    used in music psychology research.
    """
    if valence >= 0.5 and energy >= 0.5:
        return "energetic"    # happy + active
    elif valence >= 0.5 and energy < 0.5:
        return "calm"         # happy + relaxed
    elif valence < 0.5 and energy >= 0.5:
        return "tense"        # negative + active
    else:
        return "melancholic"  # negative + relaxed