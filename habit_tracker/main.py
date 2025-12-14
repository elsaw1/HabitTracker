import os
import tkinter as tk

from storage import JsonStorage
from tracker import HabitTracker
from ui import HabitTrackerUI


def main() -> None:
    """
    Application entry point.

    Tanggung jawab main():
    - Menentukan konfigurasi aplikasi
    - Menghubungkan semua layer (composition root)
    - Memulai event loop UI

    main() TIDAK:
    - Menghitung streak
    - Mengelola habit
    - Menyentuh data mentah
    """
    # Tentukan lokasi file data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "habits.json")

    storage = JsonStorage(json_path)    # Setup Persistence Layer
    tracker = HabitTracker(storage)     # Setup Application Service
    tracker.load()                      # Load state awal dari storage

    root = tk.Tk()                      # Setup UI
    HabitTrackerUI(root, tracker)       # UI menerima tracker (dependency injection)
    root.mainloop()                     # Start application loop


if __name__ == "__main__":              # Python entry guard
    main()

    
