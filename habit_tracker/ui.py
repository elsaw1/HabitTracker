from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Dict
from datetime import date

from tracker import HabitTracker


class HabitTrackerUI(ttk.Frame):
    """
    UI Layer:
      - UI TIDAK punya business logic
      - UI TIDAK mengolah data mentah
      - UI hanya mengirim intent user ke HabitTracker
      - UI hanya enampilkan hasil dari HabitTracker
    """

    def __init__(self, master: tk.Tk, tracker: HabitTracker) -> None:
        super().__init__(master, padding=12)

        self._tracker = tracker
        self._vars: Dict[str, tk.BooleanVar] = {}       # checkbox state untuk checklist harian
        self._selected_date = date.today()              # tanggal aktif yang sedang dilihat (hari ini / tanggal lain)

        # selection state (MUST exist before refresh)
        self._selected_habit_id: str | None = None      # habit yang sedang dipilih untuk Edit / Hapus
        self._habit_id_map: list[str] = []

        self._build_layout()                            # membangun UI
        self.refresh()                                  # render data awal

    # ---------- UI build ----------
    def _build_layout(self) -> None:
        self.master.title("Habit Tracker (OOP + Tkinter + JSON Storage)")
        self.master.geometry("900x560")

        # layout utama: 2 kolom (kiri: checklist, kanan: summary)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # ================= LEFT PANEL =================
        left = ttk.LabelFrame(self, text="Checklist & Habit Control")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(3, weight=1)

        # ----- Habit selector -----
        selector_frame = ttk.LabelFrame(left, text="Pilih Habit (untuk Edit / Hapus)")
        selector_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        self._habit_listbox = tk.Listbox(
            selector_frame,
            height=4,
            exportselection=False
        )
        self._habit_listbox.pack(fill="x", padx=5, pady=5)
        self._habit_listbox.bind("<<ListboxSelect>>", self._on_select_habit)    # event: user memilih habit

        # ----- Header -----
        header = ttk.Frame(left)
        header.grid(row=1, column=0, sticky="ew", padx=10)
        header.columnconfigure(0, weight=1)

        # label tanggal aktif
        self._today_label = ttk.Label(
            header,
            text="",
            font=("Segoe UI", 10, "bold"),
        )
        self._today_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        # tombol-tombol aksi
        btns = ttk.Frame(header)
        btns.grid(row=1, column=0, sticky="w")

        ttk.Button(btns, text="Tambah", command=self._on_add).grid(row=0, column=0, padx=3)
        ttk.Button(btns, text="Edit", command=self._on_edit).grid(row=0, column=1, padx=3)
        ttk.Button(btns, text="Hapus", command=self._on_delete).grid(row=0, column=2, padx=3)
        ttk.Button(btns, text="Pilih Tanggal", command=self._on_pick_date).grid(row=0, column=3, padx=3)
        ttk.Button(btns, text="Hari Ini", command=self._on_today).grid(row=0, column=4, padx=3)

        # ----- Checklist -----
        self._list_frame = ttk.Frame(left)
        self._list_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        self._list_frame.columnconfigure(0, weight=1)

        # ================= RIGHT PANEL =================
        right = ttk.LabelFrame(self, text="Weekly Summary & Streak")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        top = ttk.Frame(right)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        top.columnconfigure(0, weight=1)

        self._summary_head = ttk.Label(top, text="", justify="left")
        self._summary_head.grid(row=0, column=0, sticky="w")

        action = ttk.Frame(top)
        action.grid(row=0, column=1, sticky="e")
        ttk.Button(action, text="Export CSV", command=self._on_export).grid(row=0, column=0, padx=3)
        ttk.Button(action, text="Refresh", command=self.refresh).grid(row=0, column=1, padx=3)

        self._tree = ttk.Treeview(
            right,
            columns=("name", "done", "rate", "badge", "freeze", "cur", "long"),
            show="headings",
            height=12,
        )
        self._tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        for col, w in [
            ("name", 200),
            ("done", 70),
            ("rate", 70),
            ("badge", 180),
            ("freeze", 70),
            ("cur", 70),
            ("long", 70),
        ]:
            self._tree.heading(col, text=col.capitalize())
            self._tree.column(col, width=w, anchor="center" if col != "name" else "w")

        self.pack(fill="both", expand=True)

    # ---------- Refresh ----------
    def refresh(self) -> None:
        import datetime as _dt

        self._today_label.config(
            text=(
                f"📅 Tanggal aktif: {self._selected_date.strftime('%d %B %Y')}   "
                f"(Hari ini: {_dt.date.today().strftime('%d %B %Y')})"
            )
        )

        # ----- rebuild habit selector -----
        self._habit_listbox.delete(0, tk.END)
        self._habit_id_map.clear()
        self._selected_habit_id = None

        for h in self._tracker.list_habits(active_only=True):
            self._habit_listbox.insert(tk.END, h.get_name())
            self._habit_id_map.append(h.get_id())

        # ----- rebuild checklist -----
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._vars.clear()

        for i, (hid, name, done) in enumerate(
            self._tracker.get_checklist_for_date(self._selected_date)):
            var = tk.BooleanVar(value=done)
            self._vars[hid] = var
            cb = ttk.Checkbutton(
                self._list_frame,
                text=name,
                variable=var,
                command=lambda _hid=hid: self._on_toggle(_hid),
            )
            cb.grid(row=i, column=0, sticky="w", pady=3)

        # ----- weekly summary -----
        summary = self._tracker.weekly_summary()
        self._summary_head.config(
            text=(
                f"🗓️ Minggu: {summary['week_start']} → {summary['week_end']}\n"
                f"📈 Overall completion: {summary['overall_completion_rate']}%\n"
                f"🔥 Best current streak: {summary['best_current']['name']} "
                f"({summary['best_current']['days']} hari)\n"
                f"🏅 Longest streak ever: {summary['best_longest']['name']} "
                f"({summary['best_longest']['days']} hari)"
            )
        )

        self._tree.delete(*self._tree.get_children())
        for h in summary["habits"]:
            tag = f"streak_{h['id']}"
            self._tree.insert(
                "",
                "end",
                iid=h["id"],
                values=(
                    h["name"],
                    f"{h['done_days']}/7",
                    h["completion_rate"],
                    h.get("badge") or "⏳ Keep Going",
                    f"🧊 {h.get('freeze_left', 0)}",
                    h["current_streak"],
                    h["longest_streak"],
                ),
                tags=(tag,),
            )
            self._tree.tag_configure(tag, foreground=self._streak_color(h["current_streak"]))

    # ---------- Selection ----------
    def _on_select_habit(self, event) -> None:
        sel = self._habit_listbox.curselection()
        self._selected_habit_id = self._habit_id_map[sel[0]] if sel else None

    def _require_selected_habit(self) -> str:
        if not self._selected_habit_id:
            raise ValueError("Pilih habit terlebih dahulu.")
        return self._selected_habit_id

    # ---------- Actions ----------
    def _on_toggle(self, habit_id: str) -> None:
        self._tracker.set_done_on_date(habit_id, self._selected_date, bool(self._vars[habit_id].get()))
        self.refresh()

    def _on_pick_date(self) -> None:
        s = simpledialog.askstring("Pilih Tanggal", "Masukkan tanggal (YYYY-MM-DD):")
        if s:
            self._selected_date = date.fromisoformat(s)
            self.refresh()

    def _on_today(self) -> None:
        self._selected_date = date.today()
        self.refresh()

    def _on_add(self) -> None:
        name = simpledialog.askstring("Tambah Habit", "Nama habit:")
        if name:
            self._tracker.add_habit(name)
            self.refresh()

    def _on_edit(self) -> None:
        habit_id = self._require_selected_habit()
        name = simpledialog.askstring("Edit Habit", "Nama baru:")
        if name:
            self._tracker.edit_habit(habit_id, name)
            self.refresh()

    def _on_delete(self) -> None:
        habit_id = self._require_selected_habit()
        if messagebox.askyesno("Konfirmasi", "Hapus habit ini?"):
            self._tracker.delete_habit(habit_id)
            self.refresh()

    def _on_export(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Weekly Summary ke CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
        )
        if path:
            self._tracker.export_week_csv(path)

    # ---------- UI helper ----------
    def _streak_color(self, streak: int) -> str:
        if streak >= 7:
            return "#c9a227"
        if streak >= 3:
            return "#2e8b57"
        if streak == 0:
            return "#888888"
        return "#000000"
