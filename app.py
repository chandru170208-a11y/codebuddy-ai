import os
import anthropic
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "Please enter a message."}), 400

        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "You are CodeBuddy AI, a helpful coding assistant. "
                        "Help with programming, debugging, and explanations.\n\n"
                        + message
                    )
                }
            ]
        )

        answer = "".join(
            block.text
            for block in response.content
            if block.type == "text"
        )

        return jsonify({"reply": answer})

    except Exception:
        app.logger.exception("AI request failed")
        return jsonify({
            "error": "The AI request failed. Check the server configuration."
        }), 500

if __name__ == "__main__":
    app.run(debug=False)
