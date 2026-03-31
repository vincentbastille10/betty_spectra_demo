from flask import Flask, render_template, request, jsonify
import requests
import yaml
import os

app = Flask(__name__)

# 🔑 ENV (tu as déjà tes variables → parfait)
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

# 📦 Load YAML
with open("pack/betty_spectra.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

SYSTEM_PROMPT = config["prompt"]

# 🏠 Page chat
@app.route("/")
def home():
    return render_template("chat.html")

# 💬 API CHAT
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"response": "Je vous écoute 🙂"})

    try:
        response = requests.post(
            TOGETHER_API_URL,
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 220
            }
        )

        result = response.json()

        reply = result["choices"][0]["message"]["content"]

    except Exception as e:
        print("ERREUR LLM :", e)
        reply = "Petit souci technique… pouvez-vous reformuler ? 🙂"

    return jsonify({"response": reply})


if __name__ == "__main__":
    app.run(debug=True)
