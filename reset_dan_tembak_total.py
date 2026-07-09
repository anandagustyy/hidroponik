import requests
import time
import random
import calendar
from datetime import datetime

# URL Firebase History proyekmu
FIREBASE_BASE_URL = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/history"
FIREBASE_HISTORY_URL = f"{FIREBASE_BASE_URL}.json"

print("======================================================================")
print("1. PROSES HAPUS TOTAL: Membersihkan semua data lama di Firebase...")
print("======================================================================")

# Perintah DELETE untuk mengosongkan seluruh isi histori secara mutlak
try:
    req_delete = requests.delete(FIREBASE_HISTORY_URL)
    if req_delete.status_code == 200:
        print("-> BERHASIL! Seluruh data histori lama telah dihapus sampai bersih kosong.")
    else:
        print(f"-> Gagal menghapus, Status Code: {req_delete.status_code}")
except Exception as e:
    print(f"-> Terjadi kesalahan koneksi saat menghapus: {e}")

# DATA RESMI JURNAL KAMU (Tabel 4.1)
DATA_JURNAL_HARIAN = {
    "2026-06-04": (7.09, 1105),
    "2026-06-05": (6.78, 1006),
    "2026-06-06": (6.41, 986),
    "2026-06-07": (5.80, 954),
    "2026-06-08": (5.68, 900),
    "2026-06-09": (5.24, 860),   # Titik Kritis Penurunan
    "2026-06-10": (7.10, 1253),  # Normalisasi (Pemberian pH Up + Nutrisi)
    "2026-06-11": (6.75, 1232),
    "2026-06-12": (6.12, 1192),
    "2026-06-13": (6.98, 1110),
    "2026-06-14": (6.36, 1100),
    "2026-06-15": (7.12, 1002),
    "2026-06-16": (6.80, 991),
    "2026-06-17": (6.47, 940),
    "2026-06-18": (6.15, 908),
    "2026-06-19": (6.97, 876),
    "2026-06-20": (6.63, 1056),
    "2026-06-21": (6.20, 1002),
    "2026-06-22": (7.07, 1000),
    "2026-06-23": (6.56, 982),
    "2026-06-24": (6.22, 964),
    "2026-06-25": (7.06, 930),
    "2026-06-26": (6.97, 922)
}

print("\n======================================================================")
print("2. PROSES TEMBAK BARU: Menyuntikkan data per jam bersih (24 data/hari)...")
print("======================================================================")

total_terkirim = 0
daftar_tanggal = sorted(list(DATA_JURNAL_HARIAN.keys()))

for idx, tanggal_str in enumerate(daftar_tanggal):
    target_ph, target_ppm = DATA_JURNAL_HARIAN[tanggal_str]
    
    # Tren menuju hari esok agar grafik tersambung halus
    if idx < len(daftar_tanggal) - 1:
        besok_str = daftar_tanggal[idx + 1]
        target_ph_besok, target_ppm_besok = DATA_JURNAL_HARIAN[besok_str]
    else:
        target_ph_besok, target_ppm_besok = target_ph, target_ppm

    for jam in range(24):
        faktor_progres = jam / 24.0
        
        # Skenario khusus Tanggal 4 Juni mulai dari pH 7.01 sesuai request kamu
        if tanggal_str == "2026-06-04":
            ph_base = 7.01 - (faktor_progres * (7.01 - 6.12))
            ppm_base = 1105 - (faktor_progres * 50)
        else:
            ph_base = target_ph + (faktor_progres * (target_ph_besok - target_ph))
            ppm_base = target_ppm + (faktor_progres * (target_ppm_besok - target_ppm))
        
        # Mengatur fluktuasi alami kecil
        ph_final = round(ph_base + random.uniform(-0.04, 0.04), 2)
        ppm_final = int(ppm_base + random.randint(-8, 8))
        
        # Kunci nilai tepat pada jam 12:00 agar bernilai persis dengan tabel jurnal utama
        if jam == 12:
            ph_final = target_ph
            ppm_final = target_ppm

        # Format koordinat waktu absolut UTC agar lolos dari cache Streamlit Cloud
        waktu_gabung = f"{tanggal_str} {jam:02d}:00:00"
        waktu_obj = datetime.strptime(waktu_gabung, "%Y-%m-%d %H:%M:%S")
        timestamp_ms = int(calendar.timegm(waktu_obj.utctimetuple()) * 1000)
        
        payload = {
            "ph": float(ph_final),
            "ppm": int(ppm_final),
            "time": timestamp_ms
        }
        
        try:
            response = requests.post(FIREBASE_HISTORY_URL, json=payload)
            if response.status_code == 200:
                total_terkirim += 1
                print(f"[{total_terkirim}] BERHASIL MASUK -> {waktu_gabung} | pH: {ph_final} | PPM: {ppm_final}")
        except Exception as e:
            print(f"Gagal menyuntikkan data {waktu_gabung}: {e}")
            
        # Delay kecil agar proses stabil
        time.sleep(0.01)

print("\n======================================================================")
print(f"[SUKSES TOTAL] Pembersihan mutlak selesai. {total_terkirim} data baru berhasil masuk.")
print("======================================================================")
