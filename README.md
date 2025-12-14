# Habit Tracker 

Habit Tracker adalah aplikasi desktop sederhana berbasis Python yang digunakan untuk membantu pengguna membangun dan memantau kebiasaan harian. Aplikasi ini dikembangkan dengan menerapkan konsep **Pemrograman Berorientasi Objek (OOP)**, serta memisahkan tanggung jawab antara UI, logika aplikasi, domain, dan penyimpanan data.


## Fitur Utama
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


## 🗂️ Struktur Proyek
```sql

habit-tracker/
│
├── main.py        -- Entry point aplikasi
├── ui.py          -- UI layer (Tkinter)
├── tracker.py     -- Application service / orchestrator
├── habit.py       -- Domain entity & business rules
├── storage.py     -- Persistence layer (JSON storage)
├── habits.json    -- File data habit
└── README.md      -- Dokumentasi proyek
```

## ✨ Cara Penggunaan Aplikasi
```
1. **Menambah Habit**  
   Klik tombol **Tambah**, lalu masukkan nama habit melalui dialog input.
2. **Checklist Habit Harian**  
   Centang checkbox untuk menandai habit telah dilakukan pada tanggal aktif.
3. **Edit dan Hapus Habit**  
   Pilih habit pada daftar, lalu klik **Edit** untuk mengganti nama atau **Hapus** untuk menghapus habit.
4. **Mengubah Tanggal**  
   - Klik **Pilih Tanggal**, lalu masukkan tanggal dengan format `YYYY-MM-DD`  
   - Atau klik **Hari Ini** untuk kembali ke tanggal sekarang
5. **Melihat Ringkasan Mingguan**  
   Panel kanan menampilkan ringkasan mingguan berupa:
   - Persentase penyelesaian
   - Current streak
   - Longest streak
   - Badge mingguan
   - Sisa freeze
6. **Export Data**  
   Klik **Export CSV** untuk menyimpan ringkasan mingguan ke file CSV.
```

## 💾 Penyimpanan Data
- Data habit disimpan secara otomatis di file `habits.json`
- Data akan dimuat ulang saat aplikasi dijalankan
- Jika file tidak ditemukan atau rusak, aplikasi tetap dapat berjalan dengan data kosong

## 🚀 Pengembangan Lanjutan
Beberapa pengembangan yang dapat dilakukan di masa depan:
- Mengganti JSON dengan **database SQL** (SQLite / MySQL) agar data tersimpan lebih aman dan terstruktur
- Menambahkan **date picker / kalender interaktif** agar pengguna tidak perlu mengetik tanggal manual (`YYYY-MM-DD`)
- Menambahkan grafik visualisasi progres habit
- Sistem notifikasi atau reminder harian
- Dukungan multi-user
- Migrasi aplikasi ke platform web atau mobile

## 📸 Tampilan Aplikasi
<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/224c7250-6825-4fda-9761-8f94c8076774" />




<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" height="25" alt="python badge" />
  <img src="https://img.shields.io/badge/Tkinter-GUI-1f6feb?style=for-the-badge" height="25" alt="tkinter badge" />
  <img src="https://img.shields.io/badge/Storage-JSON-000000?style=for-the-badge&logo=json&logoColor=white" height="25" alt="json badge" />
</div>
