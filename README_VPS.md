# 🦅 PANDUAN LENGKAP BOT 24/7 (VPS / LINUX)

Panduan ini berisi cara Menyalakan, Memantau, dan Mematikan bot di server VPS/Docker.

---

## 🛠️ 1. Persiapan Awal (Hanya Sekali)

Sebelum memulai, kita harus memberikan "Surat Izin Mengemudi" ke script kita.

Copy-paste perintah ini ke terminal:

```bash
chmod +x run_forever.sh stop_bot.sh
```

---

## 🧠 2. Update Otak Bot (Jika ada perubahan fitur)

Jika Anda baru saja update coding atau ingin bot lebih pintar, jalankan training ulang.

```bash
python train_xgboost.py
```

_Tunggu sampai muncul "Training Complete"._

---

## 🚀 3. START BOT (Mode Hantu / Background)

Bot akan jalan terus meskipun Anda menutup laptop/browser.

Jalankan perintah ini:

```bash
nohup ./run_forever.sh > bot.log 2>&1 &
```

_(Tidak akan muncul apa-apa di layar. Ini Normal. Bot sudah jalan di belakang layar)_

---

## 📺 4. MONITORING (Mengintip Bot)

Untuk melihat apa yang sedang dilakukan bot (Profit/Loss, Volume):

```bash
tail -f bot.log
```

_Tahan tombol `Ctrl` lalu tekan `C` untuk keluar dari mode intip._
_(Bot TETAP JALAN di background setelah Anda keluar)_

---

## 🛑 5. STOP BOT (Untuk Maintenance / Edit)

Jika ingin mematikan bot sepenuhnya (misal mau ganti Config):

```bash
./stop_bot.sh
```

_Ini akan mematikan script penjaga dan bot utamanya._

---

## ⚡ CHEAT SHEET (Rangkuman Commmand)

**START (Nyalakan):**

```bash
nohup ./run_forever.sh > bot.log 2>&1 &
```

**MONITOR (Lihat Log):**

```bash
tail -f bot.log
```

**STOP (Matikan):**

```bash
./stop_bot.sh
```
