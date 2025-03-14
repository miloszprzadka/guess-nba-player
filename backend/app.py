from flask import Flask, jsonify, request
import sqlite3
import random
from datetime import date
from flask_cors import CORS
import os

app = Flask(__name__)

frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

CORS(app, origins=[frontend_url], supports_credentials=True)


def to_inches(player_height):
    try:
        parts = player_height.strip().split("'")
        feet = int(parts[0].strip())
        inches = int(parts[1].replace('"', '').strip())     
        total_inches = feet * 12 + inches
        return total_inches
    
    except Exception as e:
        print(f"Error converting height '{player_height}': {e}")
        return None

def get_players():
    conn = sqlite3.connect("players.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players")
    players = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return players

players = get_players()

print(players[0])

def get_daily_player():
    random.seed(date.today().toordinal())
    return random.choice(players)

daily_player = get_daily_player()

print(daily_player)

@app.route("/", methods=["GET", "POST"])
def guess():
    if request.method == "GET":
        return jsonify({"message": "Welcome to NBA Guessing Game! Submit a player name as JSON to play."})
    
    user_name = request.json.get("name")

    guessed_player = next(
    (p for p in players if p["Name"].lower() == user_name.lower()),None)

    print(guessed_player)

    response = {}
    if not guessed_player:
        return jsonify({"error": "Player not found"}), 400
    else:
        if guessed_player["Name"].lower() == daily_player["Name"].lower():
            for key in ["Age", "College", "Experience", "Height", "Jersey", "Position", "Team", "Weight"]:
                daily_value = daily_player[key]
                
                if key in ["Age", "Experience", "Jersey", "Weight", "Height"]:
                    try:
                        if key == "Weight":
                            daily_value_num = int(daily_value.split()[0])
                        elif key == "Height":
                            daily_value_num = to_inches(daily_value)
                        else:
                            daily_value_num = int(daily_value)
                    except ValueError:
                        daily_value_num = None
                else:
                    daily_value_num = daily_value    


                response[key] = {"value": daily_player[key], "color": "green"}

            return jsonify({
                "win": True,
                "response": response
            })


    for key in ["Age", "College", "Experience", "Height", "Jersey", "Position", "Team", "Weight"]:
        guessed_value = guessed_player[key]
        daily_value = daily_player[key]
        
        if key in ["Age", "Experience", "Jersey", "Weight", "Height"]:
            try:
                if key == "Weight":
                    guessed_value_num = int(guessed_value.split()[0])  
                    daily_value_num = int(daily_value.split()[0])
                elif key == "Height":
                    guessed_value_num = to_inches(guessed_value)  
                    daily_value_num = to_inches(daily_value)
                else:
                    guessed_value_num = int(guessed_value)
                    daily_value_num = int(daily_value)
            except ValueError:
                guessed_value_num = None
                daily_value_num = None

        else:
            guessed_value_num = guessed_value
            daily_value_num = daily_value    

        if guessed_player[key] == daily_player[key]:
            response[key] = {"value": guessed_player[key], "color": "green"}

        elif key in ["Age", "Experience","Jersey", "Weight", "Height"] and guessed_value_num is not None:
            diff = abs(guessed_value_num - daily_value_num)
            if diff <=3:
                response[key] = {
                    "value": guessed_value,
                    "color": "yellow",
                    "hint": "↑" if guessed_value_num < daily_value_num else "↓",
                }
            else:
                response[key] = {
                    "value": guessed_value, 
                    "color": "gray",
                    "hint": "↑" if guessed_value_num < daily_value_num else "↓"
                    }
        
        else:
            response[key] = {
                "value": guessed_player[key], 
                "color": "gray",
                } 
 
    return jsonify({
        "win": False,
        "response": response
    })

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)