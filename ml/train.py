import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.features import label_mood

def generate_training_data(n_samples=2000):
    """
    Generates synthetic training data based on the DEAM dataset's
    emotional ranges. Valence and energy are the two main axes
    used in music emotion research.
    """
    np.random.seed(42)
    
    data = []
    for _ in range(n_samples):
        valence = np.random.beta(2, 2)          # 0 to 1
        energy = np.random.beta(2, 2)           # 0 to 1
        danceability = np.random.beta(2, 2)     # 0 to 1
        acousticness = np.random.beta(2, 2)     # 0 to 1
        instrumentalness = np.random.beta(1, 5) # mostly low
        tempo = np.random.uniform(0.3, 1.0)     # normalized BPM
        
        mood = label_mood(valence, energy)
        
        data.append({
            "danceability": danceability,
            "energy": energy,
            "valence": valence,
            "acousticness": acousticness,
            "instrumentalness": instrumentalness,
            "tempo": tempo,
            "mood": mood
        })
    
    return pd.DataFrame(data)

def train_model():
    print("Generating training data...")
    df = generate_training_data(2000)
    
    print(f"Mood distribution:\n{df['mood'].value_counts()}")
    
    feature_cols = ["danceability", "energy", "valence", 
                    "acousticness", "instrumentalness", "tempo"]
    X = df[feature_cols]
    y = df["mood"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",  # handles uneven mood distribution
        random_state=42
    )
    model.fit(X_train, y_train)
    
    print("\nModel Evaluation:")
    print(classification_report(y_test, model.predict(X_test)))
    
    # Save the model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/mood_classifier.pkl")
    print("Model saved to models/mood_classifier.pkl")
    
    return model

if __name__ == "__main__":
    train_model()