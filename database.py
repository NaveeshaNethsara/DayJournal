"""
Local SQLite Database Module for Daily Journal Application.
Handles all persistence, querying, statistics, and data export.
"""

import sqlite3
import os
import json
import csv
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple, Any

from contextlib import contextmanager

DEFAULT_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "journal.db")


class JournalDatabase:
    def __init__(self, db_path: str = DEFAULT_DB_FILE):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initialize database schema with tables and indexes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_date TEXT NOT NULL,
                    entry_time TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    mood TEXT DEFAULT '😊 Happy',
                    tags TEXT DEFAULT '',
                    word_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entry_date ON journal_entries(entry_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mood ON journal_entries(mood)")
            conn.commit()

    def save_entry(
        self,
        entry_id: Optional[int] = None,
        entry_date: Optional[str] = None,
        entry_time: Optional[str] = None,
        title: str = "",
        content: str = "",
        mood: str = "😊 Happy",
        tags: str = ""
    ) -> int:
        """Create or update a journal entry."""
        now = datetime.now()
        if not entry_date:
            entry_date = now.strftime("%Y-%m-%d")
        if not entry_time:
            entry_time = now.strftime("%H:%M:%S")

        cleaned_title = title.strip() or f"Journal Entry - {entry_date}"
        cleaned_content = content.strip()
        word_count = len(cleaned_content.split()) if cleaned_content else 0

        # Clean tags
        if isinstance(tags, str):
            tag_list = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]
            cleaned_tags = ", ".join(tag_list)
        else:
            cleaned_tags = ""

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if entry_id:
                # Update existing entry
                cursor.execute("""
                    UPDATE journal_entries
                    SET entry_date = ?,
                        title = ?,
                        content = ?,
                        mood = ?,
                        tags = ?,
                        word_count = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    entry_date,
                    cleaned_title,
                    cleaned_content,
                    mood,
                    cleaned_tags,
                    word_count,
                    now.isoformat(),
                    entry_id
                ))
                saved_id = entry_id
            else:
                # Insert new entry
                cursor.execute("""
                    INSERT INTO journal_entries (
                        entry_date, entry_time, title, content,
                        mood, tags, word_count, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry_date,
                    entry_time,
                    cleaned_title,
                    cleaned_content,
                    mood,
                    cleaned_tags,
                    word_count,
                    now.isoformat(),
                    now.isoformat()
                ))
                saved_id = cursor.lastrowid
            conn.commit()
            return saved_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single entry by its primary key ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_entries(
        self,
        search: Optional[str] = None,
        mood: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Fetch filtered entries ordered by date and time descending."""
        query = "SELECT * FROM journal_entries WHERE 1=1"
        params: List[Any] = []

        if search:
            search_param = f"%{search.strip()}%"
            query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
            params.extend([search_param, search_param, search_param])

        if mood and mood != "All":
            query += " AND mood LIKE ?"
            params.append(f"%{mood}%")

        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{tag.strip()}%")

        query += " ORDER BY entry_date DESC, entry_time DESC"

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_statistics(self) -> Dict[str, Any]:
        """Compute journaling statistics: streaks, word totals, mood frequencies."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total entries and total words
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(word_count), 0) FROM journal_entries")
            total_entries, total_words = cursor.fetchone()

            # Mood counts
            cursor.execute("SELECT mood, COUNT(*) as cnt FROM journal_entries GROUP BY mood ORDER BY cnt DESC")
            mood_counts = {row["mood"]: row["cnt"] for row in cursor.fetchall()}

            # Distinct dates for streak calculation
            cursor.execute("SELECT DISTINCT entry_date FROM journal_entries ORDER BY entry_date DESC")
            dates_str = [row["entry_date"] for row in cursor.fetchall()]

            # Streak calculation
            streak = 0
            if dates_str:
                date_objects = set()
                for d in dates_str:
                    try:
                        date_objects.add(datetime.strptime(d, "%Y-%m-%d").date())
                    except ValueError:
                        continue

                current_check = date.today()
                # If no entry today, check if streak ended yesterday
                if current_check not in date_objects:
                    current_check = current_check - timedelta(days=1)

                while current_check in date_objects:
                    streak += 1
                    current_check -= timedelta(days=1)

            # Earliest and latest entry dates
            earliest_date = dates_str[-1] if dates_str else "None"
            latest_date = dates_str[0] if dates_str else "None"

            return {
                "total_entries": total_entries,
                "total_words": total_words,
                "streak_days": streak,
                "mood_counts": mood_counts,
                "earliest_date": earliest_date,
                "latest_date": latest_date
            }

    def export_data(self, export_format: str = "markdown", target_path: Optional[str] = None) -> str:
        """Export all entries to Markdown, JSON, or CSV."""
        entries = self.get_entries()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not target_path:
            folder = os.path.dirname(self.db_path)
            target_path = os.path.join(folder, f"journal_export_{timestamp}.{export_format.lower()}")

        if export_format.lower() == "json":
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)

        elif export_format.lower() == "csv":
            with open(target_path, "w", newline="", encoding="utf-8") as f:
                if entries:
                    fieldnames = ["id", "entry_date", "entry_time", "title", "mood", "tags", "word_count", "content", "created_at", "updated_at"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for e in entries:
                        writer.writerow(e)

        elif export_format.lower() in ("markdown", "md"):
            with open(target_path, "w", encoding="utf-8") as f:
                f.write("# 📖 My Personal Daily Journal\n\n")
                f.write(f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n---\n\n")
                for e in entries:
                    f.write(f"## {e['entry_date']} — {e['title']}\n")
                    f.write(f"- **Time:** {e['entry_time']}\n")
                    f.write(f"- **Mood:** {e['mood']}\n")
                    if e['tags']:
                        tags_formatted = " ".join([f"`#{t.strip()}`" for t in e['tags'].split(",") if t.strip()])
                        f.write(f"- **Tags:** {tags_formatted}\n")
                    f.write(f"- **Words:** {e['word_count']}\n\n")
                    f.write(f"{e['content']}\n\n")
                    f.write("---\n\n")

        return target_path

    def backup_db(self, backup_dir: Optional[str] = None) -> str:
        """Create a full backup of the SQLite database file."""
        import shutil
        if not backup_dir:
            backup_dir = os.path.dirname(self.db_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"journal_backup_{timestamp}.db")
        shutil.copy2(self.db_path, backup_file)
        return backup_file
