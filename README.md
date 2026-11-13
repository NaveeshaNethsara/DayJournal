# 📔 DayJournal — Private Local Daily Journal

A sleek, lightweight, and modern daily journaling software that keeps all your entries, reflections, moods, and thoughts safely stored in a **local SQLite database** right on your computer.

No subscriptions, no cloud servers, no account logins — **100% private, offline, and yours forever.**

---

## 🚀 Quick Start (1-Click Launch)

You can use DayJournal as a **Native Windows Desktop App** or as a **Browser Web App**. Both connect to the exact same local SQLite database (`journal.db`).

### Option 1: Native Desktop App (Recommended)
- **Silent Launch (No CMD popup):** Double-click [`Launch_Desktop.vbs`](file:///c:/Users/nneth/OneDrive/Desktop/Naveesha%20Nethsara%20Munasingha/Company%205/NBS/Start%20up%20Tech%20Company/nb2k/Digital%20Products/Software%20for%20jouralize%20My%20day/Launch_Desktop.vbs)
- **Standard Launch:** Double-click [`Launch_Desktop.bat`](file:///c:/Users/nneth/OneDrive/Desktop/Naveesha%20Nethsara%20Munasingha/Company%205/NBS/Start%20up%20Tech%20Company/nb2k/Digital%20Products/Software%20for%20jouralize%20My%20day/Launch_Desktop.bat)
- **Or from terminal:**
  ```powershell
  python app_gui.py
  ```

### Option 2: Modern Web Browser App
If you prefer writing in your favorite browser with split Markdown preview:
- Double-click [`Launch_Web_Browser.bat`](file:///c:/Users/nneth/OneDrive/Desktop/Naveesha%20Nethsara%20Munasingha/Company%205/NBS/Start%20up%20Tech%20Company/nb2k/Digital%20Products/Software%20for%20jouralize%20My%20day/Launch_Web_Browser.bat)
- Opens automatically at `http://localhost:5000`

---

## ✨ Features

- **📝 Daily Journaling:** Clean, distraction-free writing environment with automatic date and time stamps.
- **🌟 Mood Tracking:** Track how you feel each day (`😊 Happy`, `🌟 Fantastic`, `🧘 Calm`, `💼 Productive`, `😐 Neutral`, `🌧️ Down`, `⚡ Stressed`, `😴 Tired`).
- **🏷️ Tags & Categories:** Organize entries with tags like `#work`, `#ideas`, `#gratitude`, `#startup`.
- **💡 Reflection Prompts:** Built-in prompt selector to inspire you when you don't know what to write.
- **🔍 Instant Search & Filtering:** Filter your entire history by mood or search keywords across titles, notes, and tags.
- **📊 Insights & Streaks:** View your current journaling streak, total words written, average entry length, and mood distribution.
- **💾 Local SQLite Database:** Zero configuration. All data is saved directly to `journal.db` in this folder.
- **📤 Export & Backup:** 
  - Export to **Markdown (`.md`)** for Obsidian/Notion/GitHub.
  - Export to **JSON** or **CSV (Excel)**.
  - 1-Click SQLite database backup with timestamped snapshots.
- **🌓 Dark & Light Modes:** Seamless toggle to suit your preferred aesthetic.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + S` | **Save** current journal entry |
| `Ctrl + N` | **New** journal entry |
| `Ctrl + F` | Focus **Search** bar |

---

## 🗄️ Local Database Details

- **File:** `journal.db` (SQLite 3)
- **Table:** `journal_entries`
- **Schema:**
  - `id` (INTEGER PRIMARY KEY)
  - `entry_date` (TEXT - `YYYY-MM-DD`)
  - `entry_time` (TEXT - `HH:MM:SS`)
  - `title` (TEXT)
  - `content` (TEXT)
  - `mood` (TEXT)
  - `tags` (TEXT)
  - `word_count` (INTEGER)
  - `created_at` (TEXT ISO timestamp)
  - `updated_at` (TEXT ISO timestamp)

You can inspect or query this file anytime using SQLite tools (e.g. DB Browser for SQLite, DBeaver, or Python's `sqlite3`).

---

## 📦 Project File Structure

```
Software for jouralize My day/
├── database.py              # SQLite database manager (CRUD, search, stats, export)
├── app_gui.py               # CustomTkinter Desktop GUI application
├── app_web.py               # Flask Local Web server
├── templates/
│   └── index.html           # Tailwind CSS responsive Web UI
├── journal.db               # Local SQLite database file
├── Launch_Desktop.bat       # 1-Click desktop launcher
├── Launch_Desktop.vbs       # Silent 1-click desktop launcher
├── Launch_Web_Browser.bat   # 1-Click local web launcher
├── requirements.txt         # Python dependencies
└── README.md                # Documentation & User Guide
```
