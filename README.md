# SyncScore
### Music compatibility, powered by ML and AI

Two people. Two music libraries. One score.

SyncScore analyzes two people's real listening history and tells them exactly how musically compatible they are, with a mood breakdown, a compatibility score, an AI-written narrative about their music chemistry, and a playlist made just for them.


## How it works

1. Two people enter their Last.fm usernames
2. The app pulls their real top artists and genres via the Last.fm API
3. A Random Forest ML model maps those genres to emotional dimensions, valence (happy vs sad) and arousal (energetic vs calm), using the DEAM dataset framework
4. Each person gets a mood label: Energetic, Calm, Melancholic, or Tense
5. A compatibility score is calculated by comparing their mood profiles and genre overlap
6. An AI agent (Llama 3 via Groq) writes a relationship-style narrative and recommends 5 songs for them as a pair


## Tech stack

| | Technology | Why |
|--|-----------|-----|
| Language | Python | Best ecosystem for ML + web |
| Web framework | Flask | Lightweight, deployment-ready |
| ML model | scikit-learn Random Forest | Classical ML, interpretable, fast to train |
| Emotional framework | DEAM dataset (valence + arousal scale) | Academic research basis for mood mapping |
| AI agent | Groq API + Llama 3 | Free, fast, produces human-quality narrative |
| Music data | Last.fm API | Real listening history, no Spotify Premium needed |
| Frontend | HTML + CSS | Dark UI, clean cards, no unnecessary frameworks |


## Project structure

```
syncscore/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── routes.py          # All URL routes and page rendering
│   ├── agent.py           # AI agent, narrative and playlist generation
│   ├── compatibility.py   # Compatibility score algorithm
│   └── spotify.py         # Last.fm API integration
├── ml/
│   ├── features.py        # Genre-to-audio-feature mapping
│   ├── train.py           # Random Forest training
│   └── predict.py         # Mood prediction per user
├── config.py              # Loads environment variables
├── run.py                 # Entry point
└── requirements.txt       # All dependencies
```


## Run it locally

```bash
git clone https://github.com/shreya22010/syncscore.git
cd syncscore
pip install -r requirements.txt
```

Create a `.env` file in the root folder:

```
LAST_FM_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
SECRET_KEY=any-random-string
```

Free Last.fm key at last.fm/api/account/create  
Free Groq key at console.groq.com

```bash
python run.py
```

Open `http://127.0.0.1:5000` in your browser.


## Try it now

Enter these two real Last.fm usernames to see a full result:

```
Username 1: rj
Username 2: Babs_05
```


## Why this is different

Every existing app like Receiptify, Obscurify, and basic compatibility tools measures surface-level things such as shared artists and listening counts. Nobody has combined ML-based emotional profiling with two-person compatibility scoring and an AI agent that writes a personalised narrative. That combination, plus a real song playlist at the end, is what makes SyncScore different.


## Built with intention

End-to-end pipeline from user input to API to ML model to AI agent to result. Random Forest classifier trained on the DEAM valence-arousal emotional framework. Multi-step AI agent with prompt engineering for narrative and playlist generation. Structured for deployment on Railway or Render.