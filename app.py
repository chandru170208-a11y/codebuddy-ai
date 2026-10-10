import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        return jsonify({
            "error": "OpenRouter API key is missing from Render."
        }), 503

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-Title": "CodeBuddy AI"
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are CodeBuddy AI, a helpful coding "
                            "assistant. Help users write code, debug "
                            "errors, and understand programming."
                        )
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "max_tokens": 1200
            },
            timeout=90
        )

        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        return jsonify({"reply": answer})

    except requests.HTTPError as error:
        app.logger.warning("OpenRouter HTTP error: %s", error)

        return jsonify({
            "error": (
                "The AI request failed. The free model may be "
                "temporarily unavailable or rate-limited."
            )
        }), 502

    except (requests.RequestException, ValueError, KeyError, IndexError):
        app.logger.exception("OpenRouter request failed")

        return jsonify({
            "error": "The AI service is temporarily unavailable."
        }), 502


if __name__ == "__main__":
    app.run(debug=False)
