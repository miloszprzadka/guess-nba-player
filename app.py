from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def get_random_players():
    conn = sqlite3.connect("players.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players ORDER BY RANDOM() LIMIT 1;")
    players = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return players

@app.route("/")
def random_players():
    return jsonify(get_random_players())

if __name__ == "__main__":
    app.run(debug=True)