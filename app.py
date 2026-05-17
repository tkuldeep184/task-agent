"""Flask web UI for the task agent."""

from flask import Flask, render_template, request, jsonify
from agent import chat, conversation_history

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the chat page."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """Handle chat messages from the frontend."""
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    try:
        response = chat(user_message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset_endpoint():
    """Clear the conversation history (but keep tasks in DB)."""
    # Keep the system prompt, clear everything else
    while len(conversation_history) > 1:
        conversation_history.pop()
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)