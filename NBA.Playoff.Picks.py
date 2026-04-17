import requests
import ollama
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. SETUP & SECURITY
# Force-find the .env file in the same folder as this script
script_dir = Path(__file__).parent 
env_path = script_dir / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv('ODDS_API_KEY')
SPORT = 'basketball_nba'

if not API_KEY:
    print(f"❌ ERROR: No API Key found in {env_path}")
    exit()

print("🏀 NBA Agent: Connecting to FanDuel Live Feed...")

# 2. CONNECT TO THE LIVE FEED (v4)
# Targeted for FanDuel, American Odds, and Spreads
url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions=us&markets=spreads&bookmakers=fanduel&oddsFormat=american'

try:
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ API Error {response.status_code}: {response.text}")
        exit()
    data = response.json()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit()

# 3. ORGANIZE DATA FOR THE AI
game_summary = ""
for game in data:
    home = game['home_team']
    away = game['away_team']
    try:
        # Pull the specific FanDuel Spread data
        outcomes = game['bookmakers'][0]['markets'][0]['outcomes']
        game_summary += f"{away} @ {home} | Spread: {outcomes[0]['name']} {outcomes[0]['point']}, {outcomes[1]['name']} {outcomes[1]['point']}\n"
    except (IndexError, KeyError):
        continue

if not game_summary:
    print("⚠️ No live FanDuel spreads found for tomorrow yet.")
    exit()

print("🧠 Agent is analyzing the Playoff Slate...")

# 4. THE BRAIN (Ollama)
prompt = f"""
Act as a professional NBA betting analyst. 
Today is April 17, 2026. Tomorrow, April 18, is Game 1 of the NBA Playoffs.
The highlight is Hawks @ Knicks at Madison Square Garden.

Here are the live FanDuel spreads:
{game_summary}

Task:
1. Provide a 'Lock of the Day' for the Knicks vs Hawks game.
2. Analyze the other matchups (Raptors/Cavs, Wolves/Nuggets, Rockets/Lakers).
3. Predict a Final Score for the Knicks game.
4. Write in a sharp, authoritative, NYC-centric betting style.
"""

ai_response = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt}])
picks_text = ai_response['message']['content'].replace("\n", "<br>")

# 5. GENERATE THE WEBSITE
# Added encoding='utf-8' to handle the trophy and basketball emojis
with open("index.html", "w", encoding='utf-8') as f:
    f.write(f"""
    <html>
    <head>
        <title>NBA Playoff Intelligence | April 18</title>
        <style>
            body {{ max-width: 850px; margin: auto; font-family: 'Segoe UI', sans-serif; padding: 50px; background-color: #0c0c0c; color: #eee; }}
            .container {{ background: #1a1a1a; padding: 40px; border-radius: 15px; border-top: 6px solid #1d428a; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }}
            h1 {{ color: #fff; text-transform: uppercase; letter-spacing: 3px; text-align: center; margin-bottom: 0; }}
            .date {{ text-align: center; color: #f58426; font-weight: bold; margin-top: 5px; }}
            .picks {{ font-size: 1.15em; line-height: 1.8; color: #ddd; margin-top: 30px; }}
            hr {{ border: 0; border-top: 1px solid #333; margin: 30px 0; }}
            footer {{ text-align: center; margin-top: 40px; font-size: 0.8em; color: #555; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏆 Playoff Intelligence</h1>
            <div class="date">SATURDAY, APRIL 18, 2026</div>
            <hr>
            <div class="picks">{picks_text}</div>
        </div>
        <footer>Generated via Local Agentic Workflow (Ollama/Python)</footer>
    </body>
    </html>
    """)

print("--- SUCCESS! Site updated with full Emoji support ---")

import subprocess

print("🚀 Pushing updates to GitHub...")

# These are the commands you'd usually type manually
try:
    subprocess.run(["git", "add", "index.html"], check=True)
    subprocess.run(["git", "commit", "-m", "Daily Playoff Update"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Site is now updating on the web!")
except Exception as e:
    print(f"❌ Auto-upload failed. You might need to sign in to Git. Error: {e}")