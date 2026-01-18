# 🚀 PANDUAN START 24/7 (VPS / DOCKER)

Ini adalah langkah **dari 0 sampai selesai** untuk menjalankan bot di VPS/Docker supaya "Gacor" dan nonstop.

---

## 1️⃣ Persiapan Otak (Wajib Sekali Saja)

Sebelum bot jalan, kita harus melatih model ML dengan fitur terbaru kita.

**Copy & Paste command ini di terminal:**

```bash
python train_xgboost.py
```

_Tunggu sekitar 2-3 menit sampai muncul tulisan "Training Complete"._

---

## 2️⃣ Persiapan Script (Sekali Saja)

Kita perlu memberi izin agar script penjaga (`run_forever.sh`) boleh berjalan.

**Command:**

```bash
chmod +x run_forever.sh
```

---

## 3️⃣ Jalankan Bot (Pilih Salah Satu Mode)

### 🅰️ Mode Biasa (Bot mati kalau browser ditutup)

Gunakan ini untuk tes sebentar, melihat log di layar.

```bash
./run_forever.sh
```

_Tekan `Ctrl+C` untuk matikan._

### 🅱️ Mode Background (Bot HIDUP TERUS walau browser ditutup) 🏆

Gunakan ini untuk ditinggal tidur / 24 jam.

**Command:**

```bash
nohup ./run_forever.sh > bot.log 2>&1 &
```

_(Tidak akan muncul apa-apa di layar, karena bot jalan di belakang layar)_

---

## 4️⃣ Cara Memantau Bot (Jika pakai Mode Background)

Karena bot jalan di background, bagaimana cara lihatnya?

**Cek Log (Real-time):**

```bash
tail -f bot.log
```

_Tekan `Ctrl+C` untuk keluar dari mode pantau log (bot TETAP jalan)._

---

## 5️⃣ Cara Mematikan Bot (Stop Total)

Jika ingin update atau stop.

**Command:**

```bash
pkill -f main.py
pkill -f run_forever.sh
```

---

**🔥 Rangkuman Cepat (Copy-Paste Semua):**

```bash
# 1. Train
python train_xgboost.py

# 2. Izin & Jalan Background
chmod +x run_forever.sh
nohup ./run_forever.sh > bot.log 2>&1 &

# 3. Cek Log
tail -f bot.log
```
