from __future__ import annotations

from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from habit import Habit, DailyHabit


class HabitTracker:
    """
    Prinsip di HabitTracker:
    - UI HANYA boleh bicara ke class ini
    - Storage TIDAK tahu apa-apa soal logic
    - Habit adalah domain entity (punya logic sendiri)

    Tracker bertugas:
    - mengorkestrasi alur eksekusi
    - menjaga urutan yang BENAR (misalnya: freeze → hitung streak)
    - menjadi satu-satunya pintu masuk UI ke domain
    """

    def __init__(self, storage) -> None:
        """
        storage:
        - instance dari BaseStorage (JsonStorage sekarang, SqlStorage nanti)
        """
        self._storage = storage             # protected: hanya tracker & subclass
        self.__habits: List[Habit] = []     # private: UI tidak boleh sentuh kesini

    # -------- Load / Save --------
    def load(self) -> None:
        raw = self._storage.load()
        habits_raw = raw.get("habits", [])
        self.__habits = [Habit.from_dict(h) for h in habits_raw]

    def save(self) -> None:
        payload = {"habits": [h.to_dict() for h in self.__habits]}
        self._storage.save(payload)

    # -------- Habit CRUD --------
    # mengambil list habit
    def list_habits(self, active_only: bool = False) -> List[Habit]:
        if not active_only:
            return list(self.__habits)
        return [h for h in self.__habits if h.is_active()]

    # menambah habit baru
    def add_habit(self, name: str) -> Habit:
        name = (name or "").strip()
        if len(name) < 2:
            raise ValueError("Nama habit minimal 2 karakter.")

        '''Polymorphism:
        - Tracker tahu habit apa yang dibuat,
        - UI tidak perlu tahu subclass-nya'''
        habit = DailyHabit.new(name)  # type: ignore[attr-defined]
        self.__habits.append(habit)
        self.save()
        return habit

    def edit_habit(self, habit_id: str, new_name: str) -> None:
        habit = self._require_habit(habit_id)
        habit.set_name(new_name)
        self.save()

    def delete_habit(self, habit_id: str) -> None:
        self.__habits = [h for h in self.__habits if h.get_id() != habit_id]
        self.save()

    def set_habit_active(self, habit_id: str, active: bool) -> None:
        habit = self._require_habit(habit_id)
        habit.set_active(active)
        self.save()

    # -------- Checklist (Tanggal Bebas) --------
    def get_checklist_for_date(self, target_date: date) -> List[Tuple[str, str, bool]]:
        result = []
        for h in self.list_habits(active_only=True):
            result.append((h.get_id(), h.get_name(), h.is_done_on(target_date)))
        return result

    def set_done_on_date(self, habit_id: str, target_date: date, done: bool) -> None:
        habit = self._require_habit(habit_id)
        if done:
            habit.mark_done(target_date)
        else:
            habit.unmark_done(target_date)
        self.save()

    # -------- Analytics --------
    # Hitung tanggal awal minggu (Senin)
    def week_start(self, ref: Optional[date] = None) -> date:
        ref = ref or date.today()
        return ref - timedelta(days=ref.weekday())

    def weekly_summary(self, ref: Optional[date] = None) -> Dict[str, Any]:
        """
        Weekly summary seluruh habit
        Dengan urutan eksekusi:
        - Auto-freeze diterapkan dulu
        - Baru hitung progress & streak

        Tracker bertugas MENJAGA URUTAN INI.
        """
        ref = ref or date.today()
        start = self.week_start(ref)
        habits = self.list_habits(active_only=True)

        per_habit = []
        total_done = 0
        total_target = _toggle = 0

        # mencari best streak
        best_longest = 0
        best_current = 0
        best_longest_name = "-"
        best_current_name = "-"

        for h in habits:
            # ---- AUTO FREEZE ---- 
            # (Side effect boleh disini karena: idempotent dan domain yang menentukan)
            if h.auto_freeze_yesterday_if_needed(ref):
                self.save()

            # ---- PROGRESS & STREAK ----
            progress = h.calculate_weekly_progress(start)
            current = h.current_streak(ref)
            longest = h.longest_streak()

            per_habit.append({
                "id": h.get_id(),
                "name": h.get_name(),
                **progress,
                "current_streak": current,
                "longest_streak": longest,
                "freeze_left": h.freeze_remaining_for_week(ref),
            })

            total_done += progress["done_days"]
            total_target += progress["target_days"]

            # best streak calculation
            if longest > best_longest:
                best_longest = longest
                best_longest_name = h.get_name()

            if current > best_current:
                best_current = current
                best_current_name = h.get_name()

        overall_rate = (total_done / total_target) * 100 if total_target else 0.0

        return {
            "week_start": start.isoformat(),
            "week_end": (start + timedelta(days=6)).isoformat(),
            "overall_completion_rate": round(overall_rate, 2),
            "habits": per_habit,
            "best_longest": {"name": best_longest_name, "days": best_longest},
            "best_current": {"name": best_current_name, "days": best_current},
        }

    # -------- Export --------
    def export_week_csv(self, filepath: str, ref: Optional[date] = None) -> None:
        import csv
        """
        Export weekly summary ke CSV

        tapi:
        - CSV hanyalah VIEW dari data
        - Tidak ada logic baru di sini
        """

        summary = self.weekly_summary(ref)
        rows = summary["habits"]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["week_start", summary["week_start"], "week_end", summary["week_end"]])
            w.writerow([])
            w.writerow([
                "Habit",
                "Done Days",
                "Target Days",
                "Completion Rate",
                "Badge",
                "Freeze Left",
                "Current Streak",
                "Longest Streak",
            ])
            for r in rows:
                w.writerow([
                    r["name"],
                    r["done_days"],
                    r["target_days"],
                    r["completion_rate"],
                    r.get("badge", ""),
                    r.get("freeze_left", 0),
                    r["current_streak"],
                    r["longest_streak"],
                ])

    # -------- Internal helper --------
    def _require_habit(self, habit_id: str) -> Habit:
        for h in self.__habits:
            if h.get_id() == habit_id:
                return h
        raise ValueError("Habit tidak ditemukan.")
