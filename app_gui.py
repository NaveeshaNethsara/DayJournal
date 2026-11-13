"""
DayJournal - Modern Local Desktop Journal Software
Beautiful, aesthetic UI with adaptive Light & Dark themes and local SQLite database.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, date
import customtkinter as ctk

from database import JournalDatabase, DEFAULT_DB_FILE

# Appearance configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==============================================================================
# COMPREHENSIVE DUAL-THEME DESIGN SYSTEM (Light Mode, Dark Mode)
# Every tuple format is: (Light Mode Color, Dark Mode Color)
# ==============================================================================
THEME = {
    # Surfaces & Canvas
    "bg_main": ("#F8FAFC", "#0B0F19"),         # Light: Crisp airy canvas / Dark: Deep obsidian
    "bg_sidebar": ("#F1F5F9", "#111827"),      # Light: Soft slate / Dark: Charcoal sidebar
    "bg_card": ("#FFFFFF", "#1E293B"),         # Light: Pure white / Dark: Slate 800
    "bg_card_hover": ("#F8FAFC", "#334155"),   # Hover state
    "bg_card_active": ("#EFF6FF", "#1E293B"),  # Active selected card
    "bg_dialog": ("#FFFFFF", "#0F172A"),       # Modal dialog surface

    # Borders & Dividers
    "border": ("#E2E8F0", "#334155"),          # Clean visible border
    "border_card": ("#CBD5E1", "#334155"),
    "border_active": ("#3B82F6", "#60A5FA"),   # Vibrant blue accent
    "border_subtle": ("#E2E8F0", "#1E293B"),

    # Typography & Text (CRITICAL: High contrast in both Light & Dark modes!)
    "text_primary": ("#0F172A", "#F8FAFC"),    # Crisp almost-black in light, bright white in dark
    "text_secondary": ("#334155", "#94A3B8"),  # Slate in light, soft gray in dark
    "text_muted": ("#64748B", "#64748B"),      # Subtle hints / tags
    "text_accent": ("#2563EB", "#38BDF8"),     # Brand blue / Cyan

    # Inputs & Textboxes
    "input_bg": ("#FFFFFF", "#1E293B"),
    "input_border": ("#CBD5E1", "#475569"),
    "input_placeholder": ("#94A3B8", "#64748B"),

    # Dropdowns & Option Menus
    "dropdown_bg": ("#FFFFFF", "#1E293B"),
    "dropdown_btn": ("#E2E8F0", "#334155"),
    "dropdown_hover": ("#CBD5E1", "#475569"),

    # Buttons & Accents
    "btn_primary": ("#2563EB", "#3B82F6"),
    "btn_primary_hover": ("#1D4ED8", "#2563EB"),
    "btn_success": ("#059669", "#10B981"),
    "btn_success_hover": ("#047857", "#059669"),
    "btn_danger": ("#DC2626", "#EF4444"),
    "btn_danger_hover": ("#B91C1C", "#DC2626"),
    "btn_secondary": ("#E2E8F0", "#334155"),
    "btn_secondary_hover": ("#CBD5E1", "#475569"),

    # Badges
    "badge_bg": ("#E0E7FF", "#1E1B4B"),
    "badge_text": ("#4338CA", "#A5B4FC"),
}

MOOD_DATA = {
    "🌟 Fantastic": {"pill_bg": ("#FEF3C7", "#78350F"), "pill_text": ("#B45309", "#FDE68A")},
    "😊 Happy":     {"pill_bg": ("#D1FAE5", "#064E3B"), "pill_text": ("#047857", "#A7F3D0")},
    "🧘 Calm":      {"pill_bg": ("#E0F2FE", "#0C4A6E"), "pill_text": ("#0369A1", "#BAE6FD")},
    "💼 Productive":{"pill_bg": ("#EDE9FE", "#4C1D95"), "pill_text": ("#6D28D9", "#DDD6FE")},
    "😐 Neutral":   {"pill_bg": ("#F1F5F9", "#334155"), "pill_text": ("#475569", "#CBD5E1")},
    "🌧️ Down":      {"pill_bg": ("#DBEAFE", "#1E3A8A"), "pill_text": ("#1D4ED8", "#BFDBFE")},
    "⚡ Stressed":  {"pill_bg": ("#FEE2E2", "#7F1D1D"), "pill_text": ("#B91C1C", "#FECACA")},
    "😴 Tired":     {"pill_bg": ("#F3E8FF", "#581C87"), "pill_text": ("#7E22CE", "#E9D5FF")},
}

MOOD_OPTIONS = list(MOOD_DATA.keys())

REFLECTION_PROMPTS = [
    "💡 Select a reflection prompt to inspire your day...",
    "What went really well today and why?",
    "What are 3 things I am deeply grateful for today?",
    "What was my biggest breakthrough or victory today?",
    "What challenge did I face today, and how did I handle it?",
    "What is one valuable lesson or insight I gained today?",
    "How did I take care of my body, mind, and energy today?",
    "Who did I positively impact or connect with today?",
    "What are my top 3 focus priorities for tomorrow?"
]


class DayJournalApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db = JournalDatabase()
        self.current_entry_id = None
        self.is_modified = False

        # Configure window
        self.title("DayJournal — Your Private Daily Journal")
        self.geometry("1180x780")
        self.minsize(980, 640)
        self.configure(fg_color=THEME["bg_main"])

        # Center window on screen
        self.center_window(1180, 780)

        # Setup 2-Column Responsive Layout
        self.grid_columnconfigure(0, weight=0, minsize=350)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()
        self.setup_keybindings()

        # Load initial entries
        self.refresh_entries_list()
        self.new_entry()

    def center_window(self, width: int, height: int):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # ==========================================================================
    # SIDEBAR COMPONENT (Left: Navigation, History, Search, Theme)
    # ==========================================================================
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=350,
            corner_radius=0,
            fg_color=THEME["bg_sidebar"],
            border_width=1,
            border_color=THEME["border"]
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(3, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        # 1. Header Box (Brand Logo + Subtitle)
        header_card = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header_card.grid(row=0, column=0, padx=18, pady=(18, 12), sticky="ew")

        brand_row = ctk.CTkFrame(header_card, fg_color="transparent")
        brand_row.pack(fill="x")

        logo_icon = ctk.CTkLabel(
            brand_row,
            text="✨",
            font=ctk.CTkFont(size=22)
        )
        logo_icon.pack(side="left", padx=(0, 6))

        logo_title = ctk.CTkLabel(
            brand_row,
            text="DayJournal",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=THEME["text_primary"]
        )
        logo_title.pack(side="left")

        sub_label = ctk.CTkLabel(
            header_card,
            text="🔒 100% Local & Private SQLite Database",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME["text_muted"]
        )
        sub_label.pack(anchor="w", pady=(3, 0))

        # 2. Prominent "+ New Entry" Action Button
        self.btn_new = ctk.CTkButton(
            self.sidebar_frame,
            text="+ New Entry   (Ctrl+N)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color=THEME["btn_primary"],
            hover_color=THEME["btn_primary_hover"],
            text_color="#FFFFFF",
            command=self.new_entry
        )
        self.btn_new.grid(row=1, column=0, padx=18, pady=(4, 14), sticky="ew")

        # 3. Search and Mood Filter Box
        search_card = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        search_card.grid(row=2, column=0, padx=18, pady=(0, 10), sticky="ew")
        search_card.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_card,
            placeholder_text="🔍 Search entries, notes, or tags...",
            placeholder_text_color=THEME["input_placeholder"],
            textvariable=self.search_var,
            height=36,
            corner_radius=8,
            fg_color=THEME["input_bg"],
            text_color=THEME["text_primary"],
            border_width=1,
            border_color=THEME["input_border"]
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_entries_list())

        filter_row = ctk.CTkFrame(search_card, fg_color="transparent")
        filter_row.grid(row=1, column=0, sticky="ew")
        filter_row.grid_columnconfigure(1, weight=1)

        filter_lbl = ctk.CTkLabel(
            filter_row,
            text="Mood:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["text_secondary"]
        )
        filter_lbl.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.filter_mood_var = tk.StringVar(value="All Moods")
        self.mood_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["All Moods"] + MOOD_OPTIONS,
            variable=self.filter_mood_var,
            command=lambda _: self.refresh_entries_list(),
            height=30,
            corner_radius=8,
            fg_color=THEME["dropdown_btn"],
            button_color=THEME["dropdown_btn"],
            button_hover_color=THEME["dropdown_hover"],
            text_color=THEME["text_primary"],
            dropdown_fg_color=THEME["dropdown_bg"],
            dropdown_text_color=THEME["text_primary"],
            dropdown_hover_color=THEME["dropdown_hover"]
        )
        self.mood_filter.grid(row=0, column=1, sticky="ew")

        # 4. Scrollable Container for Entry Cards
        self.entries_scroll_frame = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            label_text="JOURNAL HISTORY",
            label_font=ctk.CTkFont(size=11, weight="bold"),
            label_text_color=THEME["text_muted"],
            fg_color="transparent"
        )
        self.entries_scroll_frame.grid(row=3, column=0, padx=14, pady=(0, 10), sticky="nsew")

        # 5. Bottom Toolbar (Insights, Export, Theme Switch)
        bottom_box = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color=THEME["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        bottom_box.grid(row=4, column=0, padx=16, pady=14, sticky="ew")
        bottom_box.grid_columnconfigure((0, 1), weight=1)

        self.btn_stats = ctk.CTkButton(
            bottom_box,
            text="📊 Insights",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            corner_radius=8,
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["text_primary"],
            command=self.show_statistics_dialog
        )
        self.btn_stats.grid(row=0, column=0, padx=(8, 4), pady=(8, 6), sticky="ew")

        self.btn_export = ctk.CTkButton(
            bottom_box,
            text="💾 Backup & Export",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            corner_radius=8,
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["text_primary"],
            command=self.show_export_dialog
        )
        self.btn_export.grid(row=0, column=1, padx=(4, 8), pady=(8, 6), sticky="ew")

        # Theme switch with clear label and mode tracking
        theme_row = ctk.CTkFrame(bottom_box, fg_color="transparent")
        theme_row.grid(row=1, column=0, columnspan=2, padx=10, pady=(2, 8), sticky="ew")
        theme_row.grid_columnconfigure(0, weight=1)

        self.theme_label = ctk.CTkLabel(
            theme_row,
            text="🌙 Dark Mode",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["text_primary"]
        )
        self.theme_label.pack(side="left")

        self.theme_switch = ctk.CTkSwitch(
            theme_row,
            text="",
            width=46,
            command=self.toggle_theme,
            onvalue="Dark",
            offvalue="Light"
        )
        self.theme_switch.select()  # Start in dark mode
        self.theme_switch.pack(side="right")

    # ==========================================================================
    # MAIN AREA COMPONENT (Right: Topbar, Title, Text Editor, Counts)
    # ==========================================================================
    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=THEME["bg_main"])
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=22, pady=18)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 1. Top Action Toolbar
        toolbar = ctk.CTkFrame(
            self.main_frame,
            fg_color=THEME["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12), ipady=4)
        toolbar.grid_columnconfigure(1, weight=1)

        # Date controls
        date_box = ctk.CTkFrame(toolbar, fg_color="transparent")
        date_box.grid(row=0, column=0, padx=14, pady=8, sticky="w")

        date_icon = ctk.CTkLabel(
            date_box,
            text="📅 Date:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME["text_primary"]
        )
        date_icon.pack(side="left", padx=(0, 6))

        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.date_entry = ctk.CTkEntry(
            date_box,
            textvariable=self.date_var,
            width=115,
            height=32,
            corner_radius=6,
            fg_color=THEME["input_bg"],
            text_color=THEME["text_primary"],
            border_width=1,
            border_color=THEME["input_border"],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.date_entry.pack(side="left", padx=(0, 6))

        btn_today = ctk.CTkButton(
            date_box,
            text="Today",
            width=60,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["text_primary"],
            command=lambda: self.date_var.set(date.today().strftime("%Y-%m-%d"))
        )
        btn_today.pack(side="left")

        # Mood Selector
        mood_box = ctk.CTkFrame(toolbar, fg_color="transparent")
        mood_box.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        mood_icon = ctk.CTkLabel(
            mood_box,
            text="Mood:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME["text_primary"]
        )
        mood_icon.pack(side="left", padx=(0, 6))

        self.mood_var = tk.StringVar(value="😊 Happy")
        self.mood_dropdown = ctk.CTkOptionMenu(
            mood_box,
            values=MOOD_OPTIONS,
            variable=self.mood_var,
            width=150,
            height=32,
            corner_radius=8,
            fg_color=THEME["dropdown_btn"],
            button_color=THEME["dropdown_btn"],
            button_hover_color=THEME["dropdown_hover"],
            text_color=THEME["text_primary"],
            dropdown_fg_color=THEME["dropdown_bg"],
            dropdown_text_color=THEME["text_primary"],
            dropdown_hover_color=THEME["dropdown_hover"],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.mood_dropdown.pack(side="left")

        # Save and Delete Actions
        actions_box = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions_box.grid(row=0, column=2, padx=14, pady=8, sticky="e")

        self.status_label = ctk.CTkLabel(
            actions_box,
            text="New Draft",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["text_muted"]
        )
        self.status_label.pack(side="left", padx=(0, 14))

        self.btn_delete = ctk.CTkButton(
            actions_box,
            text="🗑️ Delete",
            width=85,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=THEME["btn_danger"],
            hover_color=THEME["btn_danger_hover"],
            text_color="#FFFFFF",
            command=self.delete_current_entry
        )
        self.btn_delete.pack(side="left", padx=(0, 8))

        self.btn_save = ctk.CTkButton(
            actions_box,
            text="💾 Save (Ctrl+S)",
            width=125,
            height=34,
            corner_radius=8,
            fg_color=THEME["btn_success"],
            hover_color=THEME["btn_success_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.save_current_entry
        )
        self.btn_save.pack(side="left")

        # 2. Title & Tags Row
        metadata_card = ctk.CTkFrame(
            self.main_frame,
            fg_color=THEME["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        metadata_card.grid(row=1, column=0, sticky="ew", pady=(0, 10), padx=0)
        metadata_card.grid_columnconfigure(0, weight=3)
        metadata_card.grid_columnconfigure(1, weight=2)

        self.title_var = tk.StringVar()
        self.title_entry = ctk.CTkEntry(
            metadata_card,
            placeholder_text="Enter Title (e.g. Productive Morning, Lessons Learned...)",
            placeholder_text_color=THEME["input_placeholder"],
            textvariable=self.title_var,
            height=42,
            corner_radius=8,
            border_width=0,
            fg_color="transparent",
            text_color=THEME["text_primary"],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=(14, 10), pady=6)
        self.title_entry.bind("<KeyRelease>", self.on_text_change)

        self.tags_var = tk.StringVar()
        self.tags_entry = ctk.CTkEntry(
            metadata_card,
            placeholder_text="Tags: #work, #habits, #ideas",
            placeholder_text_color=THEME["input_placeholder"],
            textvariable=self.tags_var,
            height=42,
            corner_radius=8,
            border_width=0,
            fg_color="transparent",
            text_color=THEME["text_secondary"],
            font=ctk.CTkFont(size=13)
        )
        self.tags_entry.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=6)
        self.tags_entry.bind("<KeyRelease>", self.on_text_change)

        # 3. Reflection Prompts Bar
        prompt_card = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        prompt_card.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        prompt_card.grid_columnconfigure(0, weight=1)

        self.prompt_dropdown = ctk.CTkOptionMenu(
            prompt_card,
            values=REFLECTION_PROMPTS,
            command=self.insert_prompt,
            height=30,
            corner_radius=8,
            fg_color=THEME["bg_card"],
            button_color=THEME["dropdown_btn"],
            button_hover_color=THEME["dropdown_hover"],
            text_color=THEME["text_secondary"],
            dropdown_fg_color=THEME["dropdown_bg"],
            dropdown_text_color=THEME["text_primary"],
            dropdown_hover_color=THEME["dropdown_hover"],
            font=ctk.CTkFont(size=12)
        )
        self.prompt_dropdown.set(REFLECTION_PROMPTS[0])
        self.prompt_dropdown.grid(row=0, column=0, sticky="ew")

        # 4. Text Editor Canvas
        self.text_editor = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"],
            fg_color=THEME["input_bg"],
            text_color=THEME["text_primary"],
            undo=True
        )
        self.text_editor.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        self.text_editor.bind("<KeyRelease>", self.on_text_change)

        # 5. Bottom Status Bar (Word counts & Database health)
        footer = ctk.CTkFrame(
            self.main_frame,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
            height=36
        )
        footer.grid(row=4, column=0, sticky="ew")
        footer.grid_columnconfigure(1, weight=1)

        self.stats_label = ctk.CTkLabel(
            footer,
            text="Words: 0   |   Characters: 0   |   Reading Time: ~0m",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["text_secondary"]
        )
        self.stats_label.grid(row=0, column=0, padx=14, pady=6, sticky="w")

        db_badge = ctk.CTkLabel(
            footer,
            text="🟢 Database: Local SQLite ('journal.db')   |   Ctrl+S to Save",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME["text_muted"]
        )
        db_badge.grid(row=0, column=1, padx=14, pady=6, sticky="e")

    # ==========================================================================
    # KEYBOARD SHORTCUTS
    # ==========================================================================
    def setup_keybindings(self):
        self.bind("<Control-s>", lambda e: self.save_current_entry())
        self.bind("<Control-S>", lambda e: self.save_current_entry())
        self.bind("<Control-n>", lambda e: self.new_entry())
        self.bind("<Control-N>", lambda e: self.new_entry())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind("<Control-F>", lambda e: self.search_entry.focus_set())

    # ==========================================================================
    # LOGIC, THEME SWITCHING & STATE
    # ==========================================================================
    def toggle_theme(self):
        mode = self.theme_switch.get()
        ctk.set_appearance_mode(mode)
        if mode == "Dark":
            self.theme_label.configure(text="🌙 Dark Mode", text_color=THEME["text_primary"])
        else:
            self.theme_label.configure(text="☀️ Light Mode", text_color=THEME["text_primary"])

        # Refresh cards to repaint backgrounds and borders cleanly
        self.after(50, self.refresh_entries_list)

    def on_text_change(self, event=None):
        self.update_counts()
        self.is_modified = True
        self.status_label.configure(text="● Unsaved changes*", text_color=("#D97706", "#F59E0B"))

    def update_counts(self):
        content = self.text_editor.get("1.0", "end-1c").strip()
        words = len(content.split()) if content else 0
        chars = len(content)
        read_time = max(1, round(words / 200)) if words > 0 else 0
        self.stats_label.configure(
            text=f"Words: {words:,}   |   Characters: {chars:,}   |   Reading Time: ~{read_time}m"
        )

    def insert_prompt(self, choice: str):
        if choice and choice != REFLECTION_PROMPTS[0]:
            current_text = self.text_editor.get("1.0", "end-1c")
            prompt_block = f"\n\n### 💡 {choice}\n> "
            if not current_text.strip():
                prompt_block = f"### 💡 {choice}\n> "
            self.text_editor.insert("end", prompt_block)
            self.text_editor.focus_set()
            self.on_text_change()
            self.prompt_dropdown.set(REFLECTION_PROMPTS[0])

    def new_entry(self):
        self.current_entry_id = None
        self.date_var.set(date.today().strftime("%Y-%m-%d"))
        self.mood_var.set("😊 Happy")
        self.title_var.set("")
        self.tags_var.set("")
        self.text_editor.delete("1.0", "end")
        self.btn_delete.configure(state="disabled")
        self.status_label.configure(text="New Draft", text_color=THEME["text_muted"])
        self.update_counts()
        self.is_modified = False
        self.title_entry.focus_set()
        self.refresh_entries_list()

    def load_entry(self, entry_id: int):
        entry = self.db.get_entry(entry_id)
        if not entry:
            messagebox.showerror("Error", "Selected entry could not be found.")
            return

        self.current_entry_id = entry["id"]
        self.date_var.set(entry["entry_date"])
        self.mood_var.set(entry["mood"] or "😊 Happy")
        self.title_var.set(entry["title"])
        self.tags_var.set(entry["tags"] or "")
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", entry["content"] or "")

        self.btn_delete.configure(state="normal")
        self.status_label.configure(
            text=f"✓ Saved ({entry['entry_time']})",
            text_color=("#059669", "#10B981")
        )
        self.update_counts()
        self.is_modified = False
        self.refresh_entries_list()

    def save_current_entry(self):
        title = self.title_var.get().strip()
        content = self.text_editor.get("1.0", "end-1c").strip()
        entry_date = self.date_var.get().strip()
        mood = self.mood_var.get()
        tags = self.tags_var.get().strip()

        if not content and not title:
            messagebox.showwarning("Empty Entry", "Please write a title or thoughts before saving.")
            return

        if not title:
            title = f"Journal Entry - {entry_date}"
            self.title_var.set(title)

        saved_id = self.db.save_entry(
            entry_id=self.current_entry_id,
            entry_date=entry_date,
            title=title,
            content=content,
            mood=mood,
            tags=tags
        )

        self.current_entry_id = saved_id
        self.btn_delete.configure(state="normal")
        now_time = datetime.now().strftime("%H:%M:%S")
        self.status_label.configure(
            text=f"✓ Saved at {now_time}",
            text_color=("#059669", "#10B981")
        )
        self.is_modified = False
        self.refresh_entries_list()

    def delete_current_entry(self):
        if not self.current_entry_id:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to permanently delete this journal entry?\nThis cannot be undone."
        )
        if confirm:
            self.db.delete_entry(self.current_entry_id)
            self.new_entry()

    # ==========================================================================
    # SIDEBAR ENTRIES RENDERING (High visual polish & contrast)
    # ==========================================================================
    def refresh_entries_list(self):
        for widget in self.entries_scroll_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().strip()
        selected_mood = self.filter_mood_var.get()
        mood_filter = None if selected_mood == "All Moods" else selected_mood

        entries = self.db.get_entries(search=search_text, mood=mood_filter)

        if not entries:
            empty_lbl = ctk.CTkLabel(
                self.entries_scroll_frame,
                text="No entries found.\nClick '+ New Entry' to start journaling!",
                font=ctk.CTkFont(size=12),
                text_color=THEME["text_muted"],
                justify="center"
            )
            empty_lbl.pack(pady=35)
            return

        for entry in entries:
            self.create_entry_card(entry)

    def create_entry_card(self, entry: dict):
        is_active = (entry["id"] == self.current_entry_id)
        border_col = THEME["border_active"] if is_active else THEME["border_card"]
        bg_col = THEME["bg_card_active"] if is_active else THEME["bg_card"]
        border_w = 2 if is_active else 1

        card = ctk.CTkFrame(
            self.entries_scroll_frame,
            corner_radius=10,
            border_width=border_w,
            border_color=border_col,
            fg_color=bg_col
        )
        card.pack(fill="x", pady=4, padx=2)

        # Header: Date & Mood Pill
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 2))

        date_lbl = ctk.CTkLabel(
            header,
            text=f"📅 {entry['entry_date']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME["text_secondary"]
        )
        date_lbl.pack(side="left")

        # Mood badge
        mood_str = entry.get("mood") or "😊 Happy"
        mood_info = MOOD_DATA.get(mood_str, {"pill_bg": THEME["btn_secondary"], "pill_text": THEME["text_primary"]})

        mood_pill = ctk.CTkLabel(
            header,
            text=f" {mood_str} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=mood_info["pill_bg"],
            text_color=mood_info["pill_text"],
            corner_radius=6
        )
        mood_pill.pack(side="right")

        # Title
        title_text = entry["title"]
        if len(title_text) > 34:
            title_text = title_text[:31] + "..."

        btn_title = ctk.CTkButton(
            card,
            text=title_text,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            hover_color=THEME["bg_card_hover"],
            text_color=THEME["text_primary"],
            height=26,
            command=lambda eid=entry["id"]: self.load_entry(eid)
        )
        btn_title.pack(fill="x", padx=6, pady=2)

        # Snippet
        snippet = entry["content"].replace("\n", " ").strip()
        if len(snippet) > 60:
            snippet = snippet[:57] + "..."
        if not snippet:
            snippet = "(Empty entry)"

        snippet_lbl = ctk.CTkLabel(
            card,
            text=snippet,
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=THEME["text_muted"]
        )
        snippet_lbl.pack(fill="x", padx=10, pady=(0, 4))

        # Tags badges
        if entry["tags"]:
            tag_box = ctk.CTkFrame(card, fg_color="transparent")
            tag_box.pack(fill="x", padx=10, pady=(0, 8))
            for t in entry["tags"].split(",")[:3]:
                t_clean = t.strip()
                if not t_clean:
                    continue
                tag_pill = ctk.CTkLabel(
                    tag_box,
                    text=f"#{t_clean}",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    fg_color=THEME["badge_bg"],
                    text_color=THEME["badge_text"],
                    corner_radius=4
                )
                tag_pill.pack(side="left", padx=(0, 4))

    # ==========================================================================
    # MODAL DIALOGS (Insights & Export)
    # ==========================================================================
    def show_statistics_dialog(self):
        stats = self.db.get_statistics()

        dialog = ctk.CTkToplevel(self)
        dialog.title("📊 Journaling Insights & Streaks")
        dialog.geometry("480x520")
        dialog.minsize(440, 480)
        dialog.configure(fg_color=THEME["bg_dialog"])
        dialog.transient(self)
        dialog.grab_set()

        # Center
        x = self.winfo_x() + (self.winfo_width() - 480) // 2
        y = self.winfo_y() + (self.winfo_height() - 520) // 2
        dialog.geometry(f"+{x}+{y}")

        title = ctk.CTkLabel(
            dialog,
            text="Your Journaling Journey",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=THEME["text_primary"]
        )
        title.pack(pady=(22, 4))

        sub = ctk.CTkLabel(
            dialog,
            text="Keep the momentum going every single day!",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_muted"]
        )
        sub.pack(pady=(0, 14))

        # 4 Metric Cards Grid
        grid_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=6)
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        def add_stat_box(parent, r, c, label, value, color):
            box = ctk.CTkFrame(
                parent,
                fg_color=THEME["bg_card"],
                corner_radius=10,
                border_width=1,
                border_color=THEME["border"]
            )
            box.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            v_lbl = ctk.CTkLabel(box, text=str(value), font=ctk.CTkFont(size=24, weight="bold"), text_color=color)
            v_lbl.pack(pady=(10, 2))
            l_lbl = ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["text_secondary"])
            l_lbl.pack(pady=(0, 10))

        add_stat_box(grid_frame, 0, 0, "Total Entries", stats["total_entries"], ("#0284C7", "#38BDF8"))
        add_stat_box(grid_frame, 0, 1, "Words Written", f"{stats['total_words']:,}", ("#059669", "#10B981"))
        add_stat_box(grid_frame, 1, 0, "Daily Streak", f"{stats['streak_days']} Days 🔥", ("#D97706", "#F59E0B"))
        avg_words = round(stats["total_words"] / max(1, stats["total_entries"]))
        add_stat_box(grid_frame, 1, 1, "Avg Words/Entry", f"{avg_words:,}", ("#7C3AED", "#A855F7"))

        # Mood distribution
        mood_title = ctk.CTkLabel(
            dialog,
            text="Mood Frequencies",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME["text_primary"]
        )
        mood_title.pack(pady=(14, 6))

        mood_scroll = ctk.CTkScrollableFrame(
            dialog,
            height=130,
            fg_color=THEME["bg_card"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=10
        )
        mood_scroll.pack(fill="x", padx=20, pady=(0, 16))

        if stats["mood_counts"]:
            for mood, count in stats["mood_counts"].items():
                row = ctk.CTkFrame(mood_scroll, fg_color="transparent")
                row.pack(fill="x", pady=3)
                m_lbl = ctk.CTkLabel(row, text=mood, font=ctk.CTkFont(size=13, weight="bold"), text_color=THEME["text_primary"])
                m_lbl.pack(side="left")
                c_lbl = ctk.CTkLabel(row, text=f"{count} entries", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["text_accent"])
                c_lbl.pack(side="right")
        else:
            no_mood = ctk.CTkLabel(mood_scroll, text="No mood data yet.", text_color=THEME["text_muted"])
            no_mood.pack(pady=15)

        btn_close = ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            width=130,
            height=34,
            corner_radius=8,
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["text_primary"]
        )
        btn_close.pack(pady=(0, 16))

    def show_export_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("💾 Export & Full Database Backup")
        dialog.geometry("460x380")
        dialog.configure(fg_color=THEME["bg_dialog"])
        dialog.transient(self)
        dialog.grab_set()

        # Center
        x = self.winfo_x() + (self.winfo_width() - 460) // 2
        y = self.winfo_y() + (self.winfo_height() - 380) // 2
        dialog.geometry(f"+{x}+{y}")

        title = ctk.CTkLabel(
            dialog,
            text="Export Your Journal",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME["text_primary"]
        )
        title.pack(pady=(20, 6))

        sub = ctk.CTkLabel(
            dialog,
            text="You have 100% ownership of your data.\nExport your notes or create a timestamped database backup.",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_secondary"],
            justify="center"
        )
        sub.pack(pady=(0, 16))

        btn_box = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_box.pack(fill="x", padx=36, pady=6)

        def do_export(fmt):
            ext = ".md" if fmt == "markdown" else f".{fmt}"
            file_types = [("Markdown", "*.md")] if fmt == "markdown" else [("JSON file", "*.json")] if fmt == "json" else [("CSV file", "*.csv")]
            out = filedialog.asksaveasfilename(
                title=f"Export as {fmt.upper()}",
                defaultextension=ext,
                filetypes=file_types,
                initialfile=f"journal_export_{datetime.now().strftime('%Y%m%d')}{ext}"
            )
            if out:
                path = self.db.export_data(export_format=fmt, target_path=out)
                messagebox.showinfo("Export Successful", f"Entries successfully exported to:\n{path}")
                dialog.destroy()

        def do_backup():
            backup_file = self.db.backup_db()
            messagebox.showinfo("Backup Successful", f"Full database backup saved to:\n{backup_file}")
            dialog.destroy()

        ctk.CTkButton(
            btn_box,
            text="📝 Export to Markdown (.md)",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["text_primary"],
            command=lambda: do_export("markdown")
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            btn_box,
            text="📋 Export to JSON (.json)",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["text_primary"],
            command=lambda: do_export("json")
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            btn_box,
            text="📊 Export to CSV / Excel (.csv)",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME["btn_secondary"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["text_primary"],
            command=lambda: do_export("csv")
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            btn_box,
            text="🔒 Backup Full SQLite Database (.db)",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME["btn_success"],
            hover_color=THEME["btn_success_hover"],
            text_color="#FFFFFF",
            command=do_backup
        ).pack(fill="x", pady=10)


def main():
    app = DayJournalApp()
    app.mainloop()


if __name__ == "__main__":
    main()
