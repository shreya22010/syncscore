from flask import Blueprint, request, render_template_string
from app.spotify import get_user_music_data
from app.agent import analyze_compatibility
 
main = Blueprint("main", __name__)
 
HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SyncScore</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {
    --purple: #6B21E8;
    --purple-mid: #9333EA;
    --purple-light: #C084FC;
    --green: #AAFF00;
    --green-dim: #7ACC00;
    --bg: #0A0A0F;
    --surface: #111118;
    --surface2: #18181F;
    --border: rgba(107,33,232,0.3);
    --text: #F0EEF8;
    --muted: #8880A8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
 
  body {
    font-family: 'Space Mono', monospace;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }
 
  /* Mesh background */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse 60% 50% at 20% 20%, rgba(107,33,232,0.18) 0%, transparent 60%),
      radial-gradient(ellipse 50% 40% at 80% 80%, rgba(170,255,0,0.08) 0%, transparent 60%),
      radial-gradient(ellipse 40% 60% at 60% 10%, rgba(147,51,234,0.12) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
  }
 
  .wrap {
    position: relative;
    z-index: 1;
    max-width: 560px;
    margin: 0 auto;
    padding: 60px 24px 80px;
  }
 
  /* Header */
  .logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: clamp(2.4rem, 10vw, 3.8rem);
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 6px;
    background: linear-gradient(135deg, #fff 0%, var(--purple-light) 50%, var(--green) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    word-break: keep-all;
    white-space: nowrap;
  }
 
  .tagline {
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 48px;
  }
 
  /* Error */
  .error-box {
    background: rgba(220,38,38,0.12);
    border: 1px solid rgba(220,38,38,0.4);
    border-radius: 12px;
    padding: 14px 18px;
    color: #FCA5A5;
    font-size: 12px;
    margin-bottom: 28px;
    letter-spacing: 0.02em;
  }
 
  /* Cards */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(170,255,0,0.4), transparent);
  }
  .card:focus-within {
    border-color: rgba(107,33,232,0.7);
  }
 
  .person-label {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 18px;
  }
 
  input {
    width: 100%;
    background: var(--surface2);
    border: 1px solid rgba(107,33,232,0.2);
    border-radius: 10px;
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    padding: 13px 16px;
    outline: none;
    transition: border-color 0.2s, background 0.2s;
    margin-bottom: 10px;
    letter-spacing: 0.02em;
  }
  input::placeholder { color: var(--muted); }
  input:focus {
    border-color: var(--purple);
    background: rgba(107,33,232,0.06);
  }
  input:last-child { margin-bottom: 0; }
 
  .hint {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.08em;
    margin-top: -4px;
    margin-bottom: 10px;
    padding-left: 4px;
  }
 
  /* Button */
  .btn {
    width: 100%;
    background: var(--green);
    color: #0A0A0F;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 18px;
    border: none;
    border-radius: 14px;
    cursor: pointer;
    margin-top: 8px;
    transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
    box-shadow: 0 0 30px rgba(170,255,0,0.2);
  }
  .btn:hover {
    background: #C5FF33;
    transform: translateY(-2px);
    box-shadow: 0 8px 40px rgba(170,255,0,0.3);
  }
  .btn:active { transform: translateY(0); }
 
  /* How it works strip */
 
</style>
</head>
<body>
<div class="wrap">
  <div class="logo">SyncScore</div>
  <p class="tagline">Music Compatibility</p>
 
  {% if error %}
  <div class="error-box">{{ error }}</div>
  {% endif %}
 
  <form method="POST" action="/results">
    <div class="card">
      <div class="person-label">Person 01</div>
      <input type="text" name="p1_name" placeholder="Name" required value="{{ p1_name or '' }}">
      <input type="text" name="p1_username" placeholder="Last.fm username" required value="{{ p1_username or '' }}">
      <p class="hint">last.fm/user/yourname</p>
    </div>
 
    <div class="card">
      <div class="person-label">Person 02</div>
      <input type="text" name="p2_name" placeholder="Name" required value="{{ p2_name or '' }}">
      <input type="text" name="p2_username" placeholder="Last.fm username" required value="{{ p2_username or '' }}">
      <p class="hint">last.fm/user/theirname</p>
    </div>
 
    <button type="submit" class="btn">Run Analysis</button>
  </form>
</div>
</body>
</html>"""
 
 
RESULT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SyncScore — Results</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {
    --purple: #6B21E8;
    --purple-mid: #9333EA;
    --purple-light: #C084FC;
    --green: #AAFF00;
    --bg: #0A0A0F;
    --surface: #111118;
    --surface2: #18181F;
    --border: rgba(107,33,232,0.3);
    --text: #F0EEF8;
    --muted: #8880A8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Space Mono', monospace;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse 70% 50% at 10% 0%, rgba(107,33,232,0.2) 0%, transparent 55%),
      radial-gradient(ellipse 50% 60% at 90% 90%, rgba(170,255,0,0.07) 0%, transparent 55%);
    pointer-events: none;
    z-index: 0;
  }
  .wrap {
    position: relative;
    z-index: 1;
    max-width: 600px;
    margin: 0 auto;
    padding: 50px 24px 80px;
  }
 
  /* Header row */
  .header-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 36px;
  }
  .logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    background: linear-gradient(135deg, #fff, var(--purple-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .back-btn {
    font-size: 10px;
    color: var(--muted);
    text-decoration: none;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border: 1px solid var(--border);
    padding: 7px 14px;
    border-radius: 8px;
    transition: color 0.2s, border-color 0.2s;
  }
  .back-btn:hover { color: var(--text); border-color: rgba(107,33,232,0.7); }
 
  /* BIG score */
  .score-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 40px 28px;
    text-align: center;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
  }
  .score-block::before {
    content: '';
    position: absolute;
    top: -40px; left: 50%;
    transform: translateX(-50%);
    width: 300px; height: 200px;
    background: radial-gradient(ellipse, rgba(170,255,0,0.12) 0%, transparent 70%);
    pointer-events: none;
  }
  .score-num {
    font-family: 'Syne', sans-serif;
    font-size: clamp(5rem, 18vw, 8rem);
    font-weight: 800;
    line-height: 1;
    color: var(--green);
    letter-spacing: -0.04em;
    text-shadow: 0 0 80px rgba(170,255,0,0.3);
  }
  .score-denom {
    font-size: 14px;
    color: var(--muted);
    letter-spacing: 0.1em;
    margin-top: 4px;
  }
  .names-row {
    margin-top: 20px;
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.04em;
  }
  .names-sep { color: var(--purple-light); margin: 0 10px; }
 
  /* Cards */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 24px 28px;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
  }
  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(107,33,232,0.5), transparent);
  }
 
  .card-label {
    font-size: 9px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--green);
    font-weight: 700;
    margin-bottom: 16px;
  }
 
  /* Breakdown grid */
  .breakdown {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .b-item {
    background: var(--surface2);
    border-radius: 14px;
    padding: 18px 12px;
    text-align: center;
    border: 1px solid rgba(107,33,232,0.15);
  }
  .b-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--purple-light);
    line-height: 1;
  }
  .b-max { font-size: 11px; color: var(--muted); }
  .b-label {
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 6px;
  }
 
  /* Mood row */
  .mood-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .mood-item {
    background: var(--surface2);
    border-radius: 14px;
    padding: 16px;
    border: 1px solid rgba(107,33,232,0.15);
  }
  .mood-person {
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
  }
  .mood-val {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    text-transform: capitalize;
  }
 
  /* Genre tags */
  .genre-wrap { margin-top: 10px; }
  .genre-label {
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
  }
  .tags { display: flex; flex-wrap: wrap; gap: 6px; }
  .tag {
    background: rgba(107,33,232,0.2);
    border: 1px solid rgba(107,33,232,0.35);
    color: var(--purple-light);
    font-size: 10px;
    padding: 4px 12px;
    border-radius: 100px;
    letter-spacing: 0.06em;
  }
  .tag.green {
    background: rgba(170,255,0,0.1);
    border-color: rgba(170,255,0,0.3);
    color: var(--green);
  }
 
  /* Narrative */
  .narrative {
    font-size: 13px;
    color: #C8C4DC;
    line-height: 1.85;
    letter-spacing: 0.01em;
  }
 
  /* Shared artists */
  .artist-grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .artist-item {
    background: var(--surface2);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 12px;
    color: var(--text);
    border: 1px solid rgba(107,33,232,0.15);
    letter-spacing: 0.04em;
  }
 
  /* Try again */
  .try-again {
    display: block;
    text-align: center;
    margin-top: 28px;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 14px;
    border-radius: 14px;
    text-decoration: none;
    transition: color 0.2s, border-color 0.2s;
  }
  .try-again:hover { color: var(--text); border-color: rgba(107,33,232,0.7); }
</style>
</head>
<body>
<div class="wrap">
 
  <div class="header-row">
    <span class="logo">SyncScore</span>
    <a href="/" class="back-btn">New Analysis</a>
  </div>
 
  <div class="score-block">
    <div class="score-num">{{ score }}</div>
    <div class="score-denom">out of 100</div>
    <div class="names-row">{{ p1_name }}<span class="names-sep">×</span>{{ p2_name }}</div>
  </div>
 
  <div class="card">
    <div class="card-label">Score Breakdown</div>
    <div class="breakdown">
      <div class="b-item">
        <div class="b-num">{{ genre_score }}<span class="b-max">/40</span></div>
        <div class="b-label">Genre Overlap</div>
      </div>
      <div class="b-item">
        <div class="b-num">{{ mood_score }}<span class="b-max">/30</span></div>
        <div class="b-label">Mood Match</div>
      </div>
      <div class="b-item">
        <div class="b-num">{{ audio_score }}<span class="b-max">/30</span></div>
        <div class="b-label">Audio Profile</div>
      </div>
    </div>
  </div>
 
  <div class="card">
    <div class="card-label">Mood Detection</div>
    <div class="mood-row">
      <div class="mood-item">
        <div class="mood-person">{{ p1_name }}</div>
        <div class="mood-val">{{ mood1 }}</div>
      </div>
      <div class="mood-item">
        <div class="mood-person">{{ p2_name }}</div>
        <div class="mood-val">{{ mood2 }}</div>
      </div>
    </div>
 
    {% if p1_genres %}
    <div class="genre-wrap">
      <div class="genre-label">{{ p1_name }}'s genres</div>
      <div class="tags">{% for g in p1_genres %}<span class="tag">{{ g }}</span>{% endfor %}</div>
    </div>
    {% endif %}
 
    {% if p2_genres %}
    <div class="genre-wrap" style="margin-top:14px;">
      <div class="genre-label">{{ p2_name }}'s genres</div>
      <div class="tags">{% for g in p2_genres %}<span class="tag">{{ g }}</span>{% endfor %}</div>
    </div>
    {% endif %}
  </div>
 
  <div class="card">
    <div class="card-label">AI Analysis</div>
    <p class="narrative">{{ narrative }}</p>
  </div>
 
  {% if shared_artists %}
  <div class="card">
    <div class="card-label">Shared Artists</div>
    <div class="artist-grid">
      {% for artist in shared_artists %}
      <div class="artist-item">{{ artist }}</div>
      {% endfor %}
    </div>
  </div>
  {% endif %}
 
  {% if playlist %}
  <div class="card">
    <div class="card-label">Your Shared Playlist</div>
    <div class="artist-grid">
      {% for song in playlist %}
      <div class="artist-item">{{ song }}</div>
      {% endfor %}
    </div>
  </div>
  {% endif %}
 
  <a href="/" class="try-again">Run New Analysis</a>
</div>
</body>
</html>"""
 
 
@main.route("/")
def index():
    return render_template_string(
        HOME_HTML, error=None, p1_name="", p1_username="", p2_name="", p2_username=""
    )
 
 
@main.route("/results", methods=["POST"])
def results():
    p1_name = request.form.get("p1_name", "Person 1")
    p2_name = request.form.get("p2_name", "Person 2")
    p1_username = request.form.get("p1_username", "").strip()
    p2_username = request.form.get("p2_username", "").strip()
 
    try:
        p1_data = get_user_music_data(p1_username)
    except Exception as e:
        return render_template_string(
            HOME_HTML,
            error=f"Error fetching data for {p1_username}: {str(e)}",
            p1_name=p1_name, p1_username=p1_username,
            p2_name=p2_name, p2_username=p2_username,
        )
 
    try:
        p2_data = get_user_music_data(p2_username)
    except Exception as e:
        return render_template_string(
            HOME_HTML,
            error=f"Error fetching data for {p2_username}: {str(e)}",
            p1_name=p1_name, p1_username=p1_username,
            p2_name=p2_name, p2_username=p2_username,
        )
 
    if not p1_data:
        return render_template_string(
            HOME_HTML,
            error=f"Cannot find Last.fm user '{p1_username}'. Check the username.",
            p1_name=p1_name, p1_username=p1_username,
            p2_name=p2_name, p2_username=p2_username,
        )
    if not p2_data:
        return render_template_string(
            HOME_HTML,
            error=f"Cannot find Last.fm user '{p2_username}'. Check the username.",
            p1_name=p1_name, p1_username=p1_username,
            p2_name=p2_name, p2_username=p2_username,
        )
 
    p1_data["display_name"] = p1_name
    p2_data["display_name"] = p2_name
 
    try:
        result = analyze_compatibility(p1_data, p2_data)
    except Exception as e:
        return render_template_string(
            HOME_HTML,
            error=f"AI analysis error: {str(e)}",
            p1_name=p1_name, p1_username=p1_username,
            p2_name=p2_name, p2_username=p2_username,
        )
 
    return render_template_string(
        RESULT_HTML,
        score=result["compatibility_score"],
        p1_name=p1_name,
        p2_name=p2_name,
        mood1=result["mood1"],
        mood2=result["mood2"],
        p1_genres=p1_data["genres"][:6],
        p2_genres=p2_data["genres"][:6],
        genre_score=result["breakdown"]["genre_overlap"],
        mood_score=result["breakdown"]["mood_match"],
        audio_score=result["breakdown"]["audio_similarity"],
        narrative=result["narrative"],
        shared_artists=result.get("shared_artists", [])[:5],
        playlist=result.get("playlist", []),
    )
