from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize Gemini AI Client
genai.configure(api_key="AIzaSyBuTje5i_tHYA0XnIr-3i_jGeRV__Wqd8Q")
models = genai.list_models()
for model in models:
    print(model.name)

# Database Setup
def init_db():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_message TEXT,
                        bot_response TEXT
                    )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

# AI Chatbot Route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Message cannot be empty"}), 400

    user_message = data.get("message")

    try:
        # ✅ Initialize Gemini AI Client
        genai.configure(api_key="AIzaSyBuTje5i_tHYA0XnIr-3i_jGeRV__Wqd8Q")

        # ✅ Use the correct model
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(user_message)

        bot_response = response.text if response else "I'm sorry, I couldn't process that."

        # Store in Database
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (user_message, bot_response) VALUES (?, ?)",
                       (user_message, bot_response))
        conn.commit()
        conn.close()

        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get Chat History
@app.route("/history", methods=["GET"])
def get_history():
    try:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_message, bot_response FROM messages ORDER BY id DESC LIMIT 10")
        history = cursor.fetchall()
        conn.close()
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)