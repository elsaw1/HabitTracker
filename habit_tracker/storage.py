from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import os


class BaseStorage(ABC):
    """
    BaseStorage = Abstract Persistence Interface

    Tujuan class ini:
    - Menjadi KONTRAK antara application layer (HabitTracker) dan mekanisme penyimpanan data
    - HabitTracker tidak peduli:
        - data disimpan ke file
        - database
        - cloud
        - memory
    - Selama class ini diimplementasikan, tracker bisa bekerja

    Ini memungkinkan:
    JsonStorage  -> SqlStorage -> ApiStorage
    TANPA mengubah HabitTracker / UI
    """

    @abstractmethod
    def load(self) -> Dict[str, Any]:               # ambil data mentah dari storage
        raise NotImplementedError

    @abstractmethod
    def save(self, data: Dict[str, Any]) -> None:   # simpan snapshot data
        raise NotImplementedError


class JsonStorage(BaseStorage):
    """
    JsonStorage = File-based persistence

    Prinsip desain:
    - JSON HANYA sebagai media penyimpanan
    - Tidak ada:
        - perhitungan
        - validasi habit
        - logic streak / freeze
    - Jika file rusak / hilang:
        aplikasi tetap bisa jalan
    """

    def __init__(self, filepath: str) -> None:
        self._filepath = filepath  # protected

    def load(self) -> Dict[str, Any]:               # Load data dari file JSON
        if not os.path.exists(self._filepath):
            return {"habits": []}

        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, dict):
                return {"habits": []}
            raw.setdefault("habits", [])
            return raw
        except (json.JSONDecodeError, OSError):
            return {"habits": []}

    # simpan data ke file JSON
    def save(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self._filepath) or ".", exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
