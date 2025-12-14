from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, Any, Set
import uuid


def _parse_iso_date(s: str) -> date:
    """
    Parse ISO date string (YYYY-MM-DD) menjadi date object.
    Dipakai SAAT load dari storage.
    """
    return datetime.strptime(s, "%Y-%m-%d").date()


def _date_to_iso(d: date) -> str:
    """
    Convert date object menjadi ISO string.
    Dipakai SAAT save ke storage.
    """
    return d.isoformat()


class Habit:
    """
    Habit = Domain Entity

    Prinsip utama:
    - Semua aturan streak & freeze ADA DI SINI
    - Tidak tahu UI
    - Tidak tahu storage
    - Tidak tahu tracker

    Kalau suatu saat UI diganti,
    logic di sini TIDAK BOLEH berubah.
    """

    # domain rule maksimal freeze yang boleh dipakai dalam satu minggu
    FREEZE_MAX_PER_WEEK = 1  

    def __init__(self, habit_id: str, name: str, created_at: date, is_active: bool = True) -> None:
        self.__id = habit_id

        # nama bisa berubah lewat setter
        self.__name = name 

        self._created_at = created_at
        self.__is_active = is_active

        self._completion_dates: Set[date] = set()
        self._frozen_dates: Set[date] = set()


    # ---------- Factory ----------
    @staticmethod
    def new(name: str) -> Habit:
        """
        Factory method.
        karena:
        - Habit ID HARUS di-generate oleh domain
        - UI / Tracker tidak boleh bikin ID sendiri
        """

        hid = str(uuid.uuid4())
        return Habit(hid, name, date.today(), True)

    # ---------- GETTERS / SETTERS ----------
    def get_id(self) -> str:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def set_name(self, new_name: str) -> None:
        new_name = (new_name or "").strip()
        if len(new_name) < 2:
            raise ValueError("Nama habit minimal 2 karakter.")
        self.__name = new_name

    def is_active(self) -> bool:
        return self.__is_active

    def set_active(self, active: bool) -> None:
        self.__is_active = bool(active)

    # ---------- Completion ----------
    # tndai habit selesai di tanggal tertentu
    def mark_done(self, on_date: date) -> None:
        if not self.is_active():
            raise ValueError("Habit non-aktif tidak bisa dicentang.")
        self._completion_dates.add(on_date)

    # Batalkan checklist pada tanggal tertentu
    def unmark_done(self, on_date: date) -> None:
        self._completion_dates.discard(on_date)

    def is_done_on(self, d: date) -> bool:
        return d in self._completion_dates

    # ---------- Freeze logic ----------
    def is_frozen_on(self, d: date) -> bool:
        return d in self._frozen_dates

    # hitung sisa freeze token dalam minggu ref_date
    def freeze_remaining_for_week(self, ref: date) -> int:
        ws = self._week_start(ref)
        used = sum(1 for fd in self._frozen_dates if self._week_start(fd) == ws)
        return max(0, self.FREEZE_MAX_PER_WEEK - used)

    def try_freeze_date(self, missed_date: date) -> bool:
        """
        Coba apply freeze ke tanggal yang terlewat.
        Return:
        - True  → freeze berhasil / sudah ada
        - False → tidak ada token tersisa
        """
        # sudah frozen → aman, tidak consume token lagi
        if missed_date in self._frozen_dates:
            return True

        # cek token minggu tersebut
        if self.freeze_remaining_for_week(missed_date) > 0:
            self._frozen_dates.add(missed_date)
            return True

        return False

    def auto_freeze_yesterday_if_needed(self, ref_date: date) -> bool:
        """
        Auto-freeze (streak psychology):
        Jika:
        - hari ini done
        - kemarin bolong
        - kemarin belum frozen
        Maka: coba freeze kemarin (jika token ada)

        Tracker yang memanggil method ini,
        bukan UI
        """
        yesterday = ref_date - timedelta(days=1)
        if (
            self.is_done_on(ref_date)
            and not self.is_done_on(yesterday)
            and not self.is_frozen_on(yesterday)
        ):
            return self.try_freeze_date(yesterday)
        return False

    # ---------- Streak ----------
    def current_streak(self, ref_date: date) -> int:
        """
        Hitung streak aktif hingga ref_date.

        Streak berlanjut jika:
        - hari itu done
        - ATAU hari itu frozen
        """
        streak = 0
        d = ref_date

        while self.is_done_on(d) or self.is_frozen_on(d):
            streak += 1
            d -= timedelta(days=1)

        return streak

    def longest_streak(self) -> int:
        """
        Hitung streak terpanjang sepanjang histori.

        Menggabungkan:
        - completion_dates
        - frozen_dates
        """
        if not self._completion_dates and not self._frozen_dates:
            return 0

        all_days = sorted(self._completion_dates | self._frozen_dates)
        best = run = 1

        for i in range(1, len(all_days)):
            if all_days[i] == all_days[i - 1] + timedelta(days=1):
                run += 1
                best = max(best, run)
            else:
                run = 1

        return best

    # ---------- Weekly progress ----------
    def calculate_weekly_progress(self, week_start: date) -> Dict[str, Any]:
        """
        Hitung progress mingguan dasar

        Method ini sengaja dibuat: GENERIC, OVERRIDABLE (polymorphism)
        """
        days = [week_start + timedelta(days=i) for i in range(7)]
        done = sum(1 for d in days if self.is_done_on(d))
        rate = (done / 7) * 100
        return {
            "done_days": done,
            "target_days": 7,
            "completion_rate": round(rate, 2),
        }

    # ---------- Serialization ----------
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize domain object menjadi dict mentah.
        Yang dipakai oleh storage.
        """
        return {
            "type": "Habit",
            "id": self.get_id(),
            "name": self.get_name(),
            "created_at": _date_to_iso(self._created_at),
            "is_active": self.is_active(),
            "completion_dates": sorted(_date_to_iso(d) for d in self._completion_dates),
            "frozen_dates": sorted(_date_to_iso(d) for d in self._frozen_dates),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Habit:       # Rebuild domain object dari dict mentah
        habit_type = data.get("type", "Habit")
        habit_id = data["id"]
        name = data["name"]
        created_at = _parse_iso_date(data["created_at"])
        is_active = bool(data.get("is_active", True))

        # polymorphism saat load
        if habit_type == "DailyHabit":
            habit = DailyHabit(habit_id, name, created_at, is_active)
        else:
            habit = Habit(habit_id, name, created_at, is_active)

        for s in data.get("completion_dates", []):
            habit._completion_dates.add(_parse_iso_date(s))

        for s in data.get("frozen_dates", []):
            habit._frozen_dates.add(_parse_iso_date(s))

        return habit

    # ---------- internal Helper ----------
    def _week_start(self, d: date) -> date:
        return d - timedelta(days=d.weekday())


# ===== CHILD CLASS: DailyHabit =====
class DailyHabit(Habit):
    """
    Child class: adds weekly badge logic only.
    """

    def calculate_weekly_progress(self, week_start: date) -> Dict[str, Any]:
        base = super().calculate_weekly_progress(week_start)
        done = base["done_days"]

        # streak psychology via badge
        if done == 7:
            badge = "Perfect Week 🏆"
        elif done >= 5:
            badge = "Great Week ⭐"
        elif done >= 3:
            badge = "Good Momentum 👍"
        else:
            badge = "Keep Going 💪"

        base["badge"] = badge
        return base
