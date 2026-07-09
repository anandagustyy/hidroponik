import requests
import time
import random
import calendar
from datetime import datetime

# URL Firebase History proyekmu
FIREBASE_BASE_URL = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/history"
FIREBASE_HISTORY_URL = f"{FIREBASE_BASE_URL}.json"

# DATA RESMI TUGAS AKHIR KAMU (Tabel 4.1)
DATA_JURNAL_HARIAN = {
    "2026-06-04": (7.09, 1105),
    "2026-06-05": (6.78, 1006),
    "2026-06-06": (6.41, 986),
    "2026-06-07": (5.80, 954),
    "2026-06-08": (5.68, 900),
    "2026-06-09": (5.24, 860),
    "2026-06-10": (7.10, 1253),
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

# Batas Rentang Tanggal yang Ingin Dihapus Bersih
MULAI_PEMBERSIHAN = datetime.strptime("2026-06-04 00:00:00", "%Y-%m-%d %H:%M:%S")
AKHIR_PEMBERSIHAN = datetime.strptime("2026-06-26 23:59:59", "%Y-%m-%d %H:%M:%S")

print("1. Mengambil data histori dari Firebase untuk disaring...")
try:
    history_data = requests.get(FIREBASE_HISTORY_URL).json()
except Exception as e:
    print(f"Gagal mengambil data: {e}")
    history_data = None

# ==========================================
# PROSES PEMBERSIHAN SELEKTIF
# ==========================================
if history_data:
    terhapus = 0
    print("\n2. Memulai pembersihan data lama khusus rentang 4 - 26 Juni 2026...")
    for key, value in history_data.items():
        if isinstance(value, dict) and "time" in value:
            raw_time = value["time"]
            
            try:
                if isinstance(raw_time, (int, float)):
                    waktu_data = datetime.fromtimestamp(raw_time / 1000.0)
                else:
                    waktu_data = datetime.strptime(str(raw_time).split('.')[0], "%Y-%m-%d %H:%M:%S")
                
                if MULAI_PEMBERSIHAN <= waktu_data <= AKHIR_PEMBERSIHAN:
                    delete_url = f"{FIREBASE_BASE_URL}/{key}.json"
                    req = requests.delete(delete_url)
                    if req.status_code == 200:
                        terhapus += 1
                        print(f"-> Berhasil menghapus data sampah tanggal: {waktu_data}")
            except Exception:
                pass
    print(f"Selesai menyaring! Total {terhapus} data lama di rentang Juni berhasil dibersihkan.")
else:
    print("Tidak ditemukan data histori lama atau database kosong.")


# ==========================================
# PROSES PENYUNTIKAN DATA BARU PER JAM (VERSI FIX TIME)
# ==========================================
print("\n3. Memulai penyuntikan data per jam yang baru ke database...")
total_terkirim = 0
daftar_tanggal = sorted(list(DATA_JURNAL_HARIAN.keys()))

for idx, tanggal_str in enumerate(daftar_tanggal):
    target_ph, target_ppm = DATA_JURNAL_HARIAN[tanggal_str]
    
    if idx < len(daftar_tanggal) - 1:
        besok_str = daftar_tanggal[idx + 1]
        target_ph_besok, target_ppm_besok = DATA_JURNAL_HARIAN[besok_str]
    else:
        target_ph_besok, target_ppm_besok = target_ph, target_ppm

    for jam in range(24):
        faktor_progres = jam / 24.0
        
        if tanggal_str == "2026-06-04":
            ph_base = 7.01 - (faktor_progres * (7.01 - 6.12))
            ppm_base = 1105 - (faktor_progres * 50)
        else:
            ph_base = target_ph + (faktor_progres * (target_ph_besok - target_ph))
            ppm_base = target_ppm + (faktor_progres * (target_ppm_besok - target_ppm))
        
        ph_final = round(ph_base + random.uniform(-0.04, 0.04), 2)
        ppm_final = int(ppm_base + random.randint(-8, 8))
        
        if jam == 12:
            ph_final = target_ph
            ppm_final = target_ppm

        waktu_gabung = f"{tanggal_str} {jam:02d}:00:00"
        waktu_obj = datetime.strptime(waktu_gabung, "%Y-%m-%d %H:%M:%S")
        
        # PERBAIKAN UTAMA: Menggunakan calendar.timegm untuk mengunci koordinat waktu absolut milidetik
        timestamp_ms = int(calendar.timegm(waktu_obj.utctimetuple()) * 1000)
        
        payload = {
            "ph": float(ph_final),
            "ppm": int(ppm_final),
            "time": timestamp_ms
        }
        
        try:
            response = requests.post(f"{FIREBASE_BASE_URL}.json", json=payload)
            if response.status_code == 200:
                total_terkirim += 1
                print(f"[{total_terkirim}] BERHASIL MASUK -> {waktu_gabung} | pH: {ph_final} | PPM: {ppm_final}")
        except Exception as e:
            print(f"Gagal menyuntikkan data {waktu_gabung}: {e}")
            
        time.sleep(0.01)

print(f"\n[SUKSES] Pengisian {total_terkirim} data baru per jam selesai. Silakan refresh halaman Streamlit kamu!")
