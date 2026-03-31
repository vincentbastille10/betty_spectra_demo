from flask import Flask, render_template, request, jsonify
import requests
import yaml
import os

app = Flask(__name__)

TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(BASE_DIR, "pack", "betty_spectra.yaml")

with open(yaml_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

SYSTEM_PROMPT = config["prompt"]


@app.route("/")
def home():
    return render_template("chat.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"response": "Je vous écoute 🙂"})

    if not TOGETHER_API_KEY:
        return jsonify({"response": "Erreur serveur : variable TOGETHER_API_KEY manquante."}), 500

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
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"].strip()

    except requests.exceptions.HTTPError as e:
        print("ERREUR TOGETHER HTTP :", e)
        print("REPONSE API :", response.text)
        reply = "Petit souci côté IA. Réessayez dans un instant 🙂"
    except Exception as e:
        print("ERREUR LLM :", e)
        reply = "Petit souci technique… pouvez-vous reformuler ? 🙂"

    return jsonify({"response": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
