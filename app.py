"""
FileVault — A visual file manager
----------------------------------
Instead of typing file names into blank fields, you browse your files
as clickable cards, click one to open it, edit inline, and save.
New files are created with one click. Built with pure Tkinter (stdlib
only) — no installs needed.

Run with: python filevault.py
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------ #
#  Palette — warm, editorial, not another dark "dev tool" theme
# ------------------------------------------------------------------ #
PAGE_BG   = "#FDFBF7"
CARD_BG   = "#FFFFFF"
CARD_HOVER= "#FFF4EF"
BORDER    = "#EDE7DD"
ACCENT    = "#FF6B4A"   # coral — primary actions
ACCENT_H  = "#E85A3B"
TEAL      = "#14B8A6"   # secondary accent
TEXT      = "#241C15"
MUTED     = "#8A8178"
DANGER    = "#E63946"
DANGER_H  = "#C62839"
SUCCESS   = "#2A9D8F"

F_TITLE = ("Segoe UI", 21, "bold")
F_SUB   = ("Segoe UI", 10)
F_BODY  = ("Segoe UI", 11)
F_BOLD  = ("Segoe UI", 11, "bold")
F_MONO  = ("Consolas", 11)
F_ICON  = ("Segoe UI Emoji", 26)

ICONS = {
    ".py": "🐍", ".md": "📝", ".txt": "📄", ".json": "🧾",
    ".csv": "📊", ".html": "🌐", ".css": "🎨", ".js": "📜",
    ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️",
    ".pdf": "📕", ".zip": "🗜️", ".yml": "⚙️", ".yaml": "⚙️",
}


def rounded_rect(canvas, x1, y1, x2, y2, r=16, **kwargs):
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class PillButton(tk.Canvas):
    """A rounded, hover-aware button drawn on a canvas (real tk.Button
    can't do rounded corners)."""

    def __init__(self, parent, text, command, bg, fg="white", hover=None,
                 width=140, height=38, font=F_BOLD):
        super().__init__(parent, width=width, height=height,
                          bg=parent["bg"], highlightthickness=0, cursor="hand2")
        self.command = command
        self.bg_color = bg
        self.hover_color = hover or bg
        self.rect = rounded_rect(self, 1, 1, width - 1, height - 1,
                                  r=height // 2, fill=bg, outline="")
        self.create_text(width / 2, height / 2, text=text, fill=fg, font=font)
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.itemconfig(self.rect, fill=self.hover_color))
        self.bind("<Leave>", lambda e: self.itemconfig(self.rect, fill=self.bg_color))


class FileCard(tk.Canvas):
    """A clickable card representing one file on disk."""

    def __init__(self, parent, path: Path, on_click, width=210, height=110):
        super().__init__(parent, width=width, height=height,
                          bg=PAGE_BG, highlightthickness=0, cursor="hand2")
        self.path = path
        self.on_click = on_click
        self.w, self.h = width, height
        self._draw(CARD_BG, BORDER)

        self.bind("<Button-1>", lambda e: self.on_click(self.path))
        self.bind("<Enter>", lambda e: self._draw(CARD_HOVER, ACCENT))
        self.bind("<Leave>", lambda e: self._draw(CARD_BG, BORDER))

    def _draw(self, fill, outline):
        self.delete("all")
        rounded_rect(self, 1, 1, self.w - 1, self.h - 1, r=16,
                     fill=fill, outline=outline, width=1.5)
        icon = ICONS.get(self.path.suffix.lower(), "📄")
        self.create_text(20, 34, text=icon, font=F_ICON, anchor="w")

        name = self.path.name
        if len(name) > 20:
            name = name[:17] + "…"
        self.create_text(20, 68, text=name, font=F_BOLD, fill=TEXT, anchor="w")

        try:
            size = self.path.stat().st_size
            size_str = f"{size} B" if size < 1024 else f"{size / 1024:.1f} KB"
        except OSError:
            size_str = "—"
        self.create_text(20, 88, text=size_str, font=F_SUB, fill=MUTED, anchor="w")


class FileVaultApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileVault")
        self.geometry("980x640")
        self.minsize(860, 560)
        self.configure(bg=PAGE_BG)

        self.current_dir = Path.cwd()
        self.selected_file = None
        self.cards = []

        self._build_header()
        self._build_body()
        self.refresh_files()

    # -------------------------------------------------------------- #
    #  Header
    # -------------------------------------------------------------- #
    def _build_header(self):
        header = tk.Frame(self, bg=PAGE_BG)
        header.pack(fill="x", padx=28, pady=(22, 10))

        title_box = tk.Frame(header, bg=PAGE_BG)
        title_box.pack(side="left")
        tk.Label(title_box, text="🗂️  FileVault", font=F_TITLE, bg=PAGE_BG, fg=TEXT).pack(anchor="w")
        tk.Label(title_box, text=f"Browsing {self.current_dir}", font=F_SUB,
                 bg=PAGE_BG, fg=MUTED).pack(anchor="w")

        action_box = tk.Frame(header, bg=PAGE_BG)
        action_box.pack(side="right")

        PillButton(action_box, "＋ New File", self.new_file, bg=ACCENT,
                   hover=ACCENT_H, width=130).pack(side="right", padx=(8, 0))
        PillButton(action_box, "⟳", self.refresh_files, bg="#F1EDE4",
                   fg=TEXT, hover=BORDER, width=44).pack(side="right")

        search_wrap = tk.Frame(header, bg=PAGE_BG)
        search_wrap.pack(side="right", padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.render_cards())
        search_entry = tk.Entry(search_wrap, textvariable=self.search_var, font=F_BODY,
                                 bg=CARD_BG, fg=TEXT, relief="flat", bd=0,
                                 highlightthickness=1, highlightbackground=BORDER,
                                 highlightcolor=ACCENT, width=18)
        search_entry.pack(ipady=7, ipadx=8)
        self._placeholder(search_entry, "🔍 Search files…")

    def _placeholder(self, entry, text):
        entry.insert(0, text)
        entry.config(fg=MUTED)

        def on_in(_e):
            if entry.get() == text:
                entry.delete(0, "end")
                entry.config(fg=TEXT)

        def on_out(_e):
            if not entry.get():
                entry.insert(0, text)
                entry.config(fg=MUTED)

        entry.bind("<FocusIn>", on_in)
        entry.bind("<FocusOut>", on_out)

    # -------------------------------------------------------------- #
    #  Body: file grid (left) + editor (right)
    # -------------------------------------------------------------- #
    def _build_body(self):
        body = tk.Frame(self, bg=PAGE_BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        # ---- left: scrollable card grid ----
        left = tk.Frame(body, bg=PAGE_BG, width=460)
        left.pack(side="left", fill="both", expand=False)
        left.pack_propagate(False)

        canvas_wrap = tk.Frame(left, bg=PAGE_BG)
        canvas_wrap.pack(fill="both", expand=True)

        self.grid_canvas = tk.Canvas(canvas_wrap, bg=PAGE_BG, highlightthickness=0)
        vbar = tk.Scrollbar(canvas_wrap, orient="vertical", command=self.grid_canvas.yview)
        self.scroll_frame = tk.Frame(self.grid_canvas, bg=PAGE_BG)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox("all")),
        )
        self.grid_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.grid_canvas.configure(yscrollcommand=vbar.set)
        self.grid_canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")
        self.grid_canvas.bind_all("<MouseWheel>", self._on_scroll)

        # ---- right: editor panel ----
        right = tk.Frame(body, bg=CARD_BG, highlightthickness=1,
                          highlightbackground=BORDER)
        right.pack(side="left", fill="both", expand=True, padx=(20, 0))

        self.editor_wrap = tk.Frame(right, bg=CARD_BG)
        self.editor_wrap.pack(fill="both", expand=True, padx=24, pady=22)

        self._render_empty_editor()

    def _on_scroll(self, event):
        self.grid_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # -------------------------------------------------------------- #
    #  File listing / cards
    # -------------------------------------------------------------- #
    def refresh_files(self):
        self.render_cards()
        self.show_toast("Refreshed", "info")

    def render_cards(self):
        for c in self.cards:
            c.destroy()
        self.cards.clear()

        query = self.search_var.get().lower()
        if query.startswith("🔍"):
            query = ""

        files = sorted(
            [p for p in self.current_dir.iterdir() if p.is_file()],
            key=lambda p: p.name.lower(),
        )
        if query:
            files = [p for p in files if query in p.name.lower()]

        if not files:
            empty = tk.Label(self.scroll_frame, text="No files here yet.\nCreate one to get started →",
                              font=F_SUB, bg=PAGE_BG, fg=MUTED, justify="left")
            empty.grid(row=0, column=0, padx=8, pady=20, sticky="w")
            self.cards.append(empty)
            return

        cols = 2
        for i, path in enumerate(files):
            card = FileCard(self.scroll_frame, path, self.select_file)
            card.grid(row=i // cols, column=i % cols, padx=6, pady=6)
            self.cards.append(card)

    # -------------------------------------------------------------- #
    #  Editor panel states
    # -------------------------------------------------------------- #
    def _clear_editor(self):
        for w in self.editor_wrap.winfo_children():
            w.destroy()

    def _render_empty_editor(self):
        self._clear_editor()
        wrap = tk.Frame(self.editor_wrap, bg=CARD_BG)
        wrap.place(relx=0.5, rely=0.45, anchor="center")
        tk.Label(wrap, text="📂", font=("Segoe UI Emoji", 40), bg=CARD_BG).pack()
        tk.Label(wrap, text="Select a file to view or edit it",
                 font=F_BODY, bg=CARD_BG, fg=MUTED).pack(pady=(6, 14))
        PillButton(wrap, "＋ Create your first file", self.new_file,
                   bg=ACCENT, hover=ACCENT_H, width=230).pack()

    def select_file(self, path):
        self.selected_file = path
        self._clear_editor()

        top = tk.Frame(self.editor_wrap, bg=CARD_BG)
        top.pack(fill="x", pady=(0, 12))

        icon = ICONS.get(path.suffix.lower(), "📄")
        tk.Label(top, text=f"{icon}  {path.name}", font=("Segoe UI", 15, "bold"),
                 bg=CARD_BG, fg=TEXT).pack(side="left")

        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%b %d, %I:%M %p")
        except OSError:
            mtime = "unknown"
        tk.Label(top, text=f"edited {mtime}", font=F_SUB, bg=CARD_BG, fg=MUTED).pack(side="right")

        self.editor_text = tk.Text(self.editor_wrap, font=F_MONO, bg="#FBFAF7",
                                    fg=TEXT, relief="flat", bd=0, wrap="word",
                                    highlightthickness=1, highlightbackground=BORDER,
                                    highlightcolor=ACCENT, padx=14, pady=12)
        self.editor_text.pack(fill="both", expand=True, pady=(0, 14))
        try:
            self.editor_text.insert("1.0", path.read_text())
        except Exception as err:
            self.editor_text.insert("1.0", f"[Could not read file: {err}]")

        btns = tk.Frame(self.editor_wrap, bg=CARD_BG)
        btns.pack(fill="x")

        PillButton(btns, "💾 Save", self.save_current, bg=SUCCESS,
                   hover="#238477", width=110).pack(side="left", padx=(0, 8))
        PillButton(btns, "➕ Append", self.append_current, bg=TEAL,
                   hover="#0f9c8c", width=120).pack(side="left", padx=(0, 8))
        PillButton(btns, "✏️ Rename", self.rename_current, bg="#F1EDE4",
                   fg=TEXT, hover=BORDER, width=120).pack(side="left", padx=(0, 8))
        PillButton(btns, "🗑️ Delete", self.delete_current, bg=DANGER,
                   hover=DANGER_H, width=110).pack(side="right")

    # -------------------------------------------------------------- #
    #  Actions
    # -------------------------------------------------------------- #
    def new_file(self):
        name = simpledialog.askstring("New file", "File name (e.g. notes.txt):", parent=self)
        if not name:
            return
        path = self.current_dir / name.strip()
        if path.exists():
            self.show_toast(f"'{path.name}' already exists", "error")
            return
        try:
            path.write_text("")
            self.render_cards()
            self.select_file(path)
            self.show_toast(f"Created '{path.name}'", "success")
        except Exception as err:
            self.show_toast(f"Error: {err}", "error")

    def save_current(self):
        if not self.selected_file:
            return
        content = self.editor_text.get("1.0", "end-1c")
        try:
            self.selected_file.write_text(content)
            self.render_cards()
            self.show_toast(f"Saved '{self.selected_file.name}'", "success")
        except Exception as err:
            self.show_toast(f"Error: {err}", "error")

    def append_current(self):
        if not self.selected_file:
            return
        extra = simpledialog.askstring("Append text", "Text to append:", parent=self)
        if not extra:
            return
        try:
            with self.selected_file.open("a") as fs:
                fs.write("\n" + extra)
            self.editor_text.insert("end", "\n" + extra)
            self.render_cards()
            self.show_toast("Content appended", "success")
        except Exception as err:
            self.show_toast(f"Error: {err}", "error")

    def rename_current(self):
        if not self.selected_file:
            return
        new_name = simpledialog.askstring("Rename file", "New file name:", parent=self,
                                           initialvalue=self.selected_file.name)
        if not new_name or new_name == self.selected_file.name:
            return
        new_path = self.current_dir / new_name.strip()
        if new_path.exists():
            self.show_toast(f"'{new_path.name}' already exists", "error")
            return
        try:
            self.selected_file.rename(new_path)
            self.render_cards()
            self.select_file(new_path)
            self.show_toast(f"Renamed to '{new_path.name}'", "success")
        except Exception as err:
            self.show_toast(f"Error: {err}", "error")

    def delete_current(self):
        if not self.selected_file:
            return
        if messagebox.askyesno("Delete file", f"Delete '{self.selected_file.name}'? This can't be undone."):
            try:
                self.selected_file.unlink()
                name = self.selected_file.name
                self.selected_file = None
                self.render_cards()
                self._render_empty_editor()
                self.show_toast(f"Deleted '{name}'", "success")
            except Exception as err:
                self.show_toast(f"Error: {err}", "error")

    # -------------------------------------------------------------- #
    #  Toast notifications
    # -------------------------------------------------------------- #
    def show_toast(self, message, kind="info"):
        color = {"success": SUCCESS, "error": DANGER, "info": TEXT}[kind]
        icon = {"success": "✅", "error": "⚠️", "info": "ℹ️"}[kind]

        toast = tk.Label(self, text=f"{icon}  {message}", font=F_BOLD,
                          bg=TEXT, fg="white", padx=18, pady=10)
        toast.place(relx=0.98, rely=0.96, anchor="se")
        self.after(2200, toast.destroy)


if __name__ == "__main__":
    app = FileVaultApp()
    app.mainloop()