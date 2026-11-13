"""
DayJournal - Local Web Interface & Server
Runs a lightweight local web server with Flask and SQLite.
"""

import os
import sys
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, send_file
from database import JournalDatabase, DEFAULT_DB_FILE

app = Flask(__name__, template_folder="templates")
db = JournalDatabase()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/entries", methods=["GET"])
def get_entries():
    search = request.args.get("search", "")
    mood = request.args.get("mood", "All")
    entries = db.get_entries(search=search if search else None, mood=mood if mood != "All" else None)
    return jsonify(entries)


@app.route("/api/entries/<int:entry_id>", methods=["GET"])
def get_entry(entry_id):
    entry = db.get_entry(entry_id)
    if entry:
        return jsonify(entry)
    return jsonify({"error": "Entry not found"}), 404


@app.route("/api/entries", methods=["POST"])
def save_entry():
    data = request.json or {}
    entry_id = data.get("id")
    entry_date = data.get("entry_date")
    title = data.get("title", "")
    content = data.get("content", "")
    mood = data.get("mood", "😊 Happy")
    tags = data.get("tags", "")

    saved_id = db.save_entry(
        entry_id=entry_id,
        entry_date=entry_date,
        title=title,
        content=content,
        mood=mood,
        tags=tags
    )
    return jsonify({"id": saved_id, "status": "success"})


@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    success = db.delete_entry(entry_id)
    return jsonify({"status": "deleted" if success else "failed"})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    stats = db.get_statistics()
    return jsonify(stats)


@app.route("/api/export", methods=["GET"])
def export_file():
    fmt = request.args.get("format", "markdown").lower()
    temp_dir = os.path.dirname(DEFAULT_DB_FILE)
    export_path = db.export_data(export_format=fmt)
    filename = os.path.basename(export_path)
    return send_file(export_path, as_attachment=True, download_name=filename)


@app.route("/api/backup", methods=["GET"])
def backup_file():
    backup_path = db.backup_db()
    filename = os.path.basename(backup_path)
    return send_file(backup_path, as_attachment=True, download_name=filename)


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    port = 5000
    print(f"\n==========================================")
    print(f" 📔 DayJournal Web Server is Running!")
    print(f" URL: http://127.0.0.1:{port}")
    print(f" Database: {DEFAULT_DB_FILE}")
    print(f" Press Ctrl+C in this terminal to stop.")
    print(f"==========================================\n")

    threading.Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=port, debug=False)
