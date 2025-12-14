# Habit Tracker (OOP-Based Desktop Application)

Habit Tracker adalah aplikasi desktop sederhana berbasis Python yang digunakan untuk membantu pengguna membangun dan memantau kebiasaan harian. Aplikasi ini dikembangkan dengan menerapkan konsep **Pemrograman Berorientasi Objek (OOP)**, serta memisahkan tanggung jawab antara UI, logika aplikasi, domain, dan penyimpanan data.

---

## ✨ Fitur Utama

- Menambah, mengedit, dan menghapus habit
- Checklist habit berbasis tanggal
- Perhitungan **current streak** dan **longest streak**
- Sistem **freeze** untuk menjaga streak jika satu hari terlewat
- Ringkasan mingguan (weekly summary)
- Badge mingguan berdasarkan progres
- Penyimpanan data menggunakan file JSON
- Export ringkasan mingguan ke file CSV
- Antarmuka grafis menggunakan Tkinter



## 🧠 Konsep OOP yang Diterapkan

Aplikasi ini menerapkan konsep OOP sebagai berikut:

- **Encapsulation**
  - Atribut domain dilindungi menggunakan private (`__`) dan protected (`_`)
  - Akses data dilakukan melalui method getter/setter

- **Inheritance**
  - `DailyHabit` mewarisi class `Habit`
  - `HabitTrackerUI` mewarisi `ttk.Frame`
  - `JsonStorage` mewarisi `BaseStorage`

- **Polymorphism**
  - Method `calculate_weekly_progress()` di-override pada subclass
  - Pembuatan habit tidak bergantung pada subclass spesifik (factory pattern)

- **Separation of Concerns**
  - UI, domain, application service, dan storage dipisahkan ke file berbeda

---

## 🗂️ Struktur Proyek

