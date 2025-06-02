from flask import Flask, request, jsonify
import requests
import os
from datetime import date

app = Flask(__name__)

OUTLINE_API_KEY = os.getenv("OUTLINE_API_KEY")
DOCUMENT_ID = os.getenv("OUTLINE_DOCUMENT_ID")
OUTLINE_API_URL = "https://xchange.netwrix.com/api"

HEADERS = {
    "Authorization": f"Bearer {OUTLINE_API_KEY}",
    "Content-Type": "application/json"
}

def fetch_current_markdown():
    response = requests.post(
        f"{OUTLINE_API_URL}/documents.info",
        json={"id": DOCUMENT_ID},
        headers=HEADERS,
        verify=False
    )
    response.raise_for_status()
    return response.json()["data"]["text"]

def update_markdown(text):
    response = requests.post(
        f"{OUTLINE_API_URL}/documents.update",
        json={"id": DOCUMENT_ID, "text": text},
        headers=HEADERS,
        verify=False
    )
    response.raise_for_status()
    return response.json()

@app.route("/prepend-entry", methods=["POST"])
def prepend_entry():
    data = request.get_json()

    name = data.get("name")
    score = data.get("score")
    date_str = data.get("date") or date.today().isoformat()
    highlights = data.get("highlights", [])

    if not name or score is None or not isinstance(highlights, list):
        return jsonify({"error": "Missing or invalid fields"}), 400

    highlight_text = "<br>".join(f"- {h}" for h in highlights)
    new_row = f"| {name} | {score} | {date_str} | {highlight_text} |"

    try:
        current_md = fetch_current_markdown()
        lines = current_md.splitlines()

        # Insert after table header
        header_index = next(i for i, line in enumerate(lines) if "| Name" in line)
        lines.insert(header_index + 2, new_row)

        updated_text = "\n".join(lines)
        update_markdown(updated_text)

        return jsonify({"message": "Leaderboard updated successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
