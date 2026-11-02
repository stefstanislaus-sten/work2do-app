"""Database Rencana Kinerja (RK) dari SKP Stenislaus Angga Aprianto, S.Tr.Stat. (Hasil Kerja A. Utama)."""

RK_TITLES = [
    "Terlaksananya Pelaksanaan Kegiatan Statistik Sumber Daya Hayati Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Statistik Sosial Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Survei Angkatan Kerja Nasional (SAKERNAS) yang lengkap dan tepat waktu",
    "Terlaksananya Survei Sosial Ekonomi Nasional (SUSENAS) yang lengkap dan tepat waktu",
    "Terlaksananya kegiatan Survei Konversi Gabah ke Beras (SKGB) yang lengkap dan tepat waktu",
    "Terlaksananya kegiatan Statistik Pertanian Palawija (SP Palawija) yang lengkap dan tepat waktu",
    "Terlaksananya kegiatan Survei Kerangka Sampel Area (KSA) yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Ground Check Penerima Bantuan Iuran (PBI) Tahap 1 yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Survei Tahunan Perusahaan Air Bersih yang lengkap dan tepat waktu",
    "Terlaksananya Survei Ekonomi Rumah Tangga Triwulanan (SERUTI) yang lengkap dan tepat waktu",
    "Terlaksananya Pelayanan Front Office yang Tepat Waktu",
    "Terlaksananya kegiatan Statistik Pertanian Hortikultura (SPH) yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Sensus Ekonomi Tahun 2026 yang lengkap dan tepat waktu",
    "Terlaksananya kegiatan Survei Kesejahteraan Petani (SKP) yang sesuai pedoman dan tepat waktu",
    "Terlaksananya Pengumpulan Data Statistik Politik dan Keamanan (STATPOLKAM) yang lengkap dan tepat waktu",
    "Terlaksananya Pendataan Potensi Desa (PODES) yang lengkap dan tepat waktu",
    "Terlaksananya Pelaksanaan Kegiatan Survei Triwulanan Pelaku Usaha (KEK/KI) yang lengkap dan tepat waktu",
    "Terlaksananya Pengolahan Hasil Kegiatan Statistik Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Survei Nasional Literasi dan Inklusi Keuangan (SNLIK) yang lengkap dan tepat waktu",
    "Terlaksananya kegiatan Survei Usaha Hortikultura Lainnya (VN Horti) yang lengkap dan tepat waktu",
    "Terlaksananya pemantauan dan evaluasi kinerja penyelenggaraan pelayanan publik (PEKPPP)",
    "Terlaksananya kegiatan Pencacahan Lengkap Tempat Pelelangan Ikan Triwulanan (PP/TPI) secara lengkap dan tepat waktu",
    "Terlaksananya kegiatan Updating Direktori Perusahaan Pertanian dan Usaha Tani Lainnya (UDPP DUTL) yang lengkap dan tepat waktu",
    "Terlaksananya kegiatan Survei Ubinan yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Reformasi Birokrasi dan Zona Integritas",
    "Terlaksananya kegiatan Survei Perusahaan Perkebunan (SKB) Tahunan yang lengkap dan tepat waktu",
    "Terlaksananya kegiatan Survei Perusahaan Perkebunan Bulanan (Sedapp) yang lengkap dan tepat waktu",
    "Terlaksananya Pengolahan Data Podes Yang Tepat Waktu",
    "Terlaksananya Kegiatan Survei Air Bersih Triwulanan yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Survei Perusahaan Konstruksi Tahunan (SKTH) yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Administrasi Statistik Sumber Daya Mineral dan Konstruksi yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Administrasi Statistik Sumber Daya Hayati yang lengkap dan tepat waktu",
    "Penyusunan Laporan Keuangan Satker Tahun 2026 yang Tepat Waktu",
    "Terlaksananya Kegiatan Updating Direktori Perusahaan Pertambangan dan Energi (UDPE) yang lengkap dan tepat waktu",
    "Terlaksananya Pelaksanaan Kegiatan Statistik Sumber Daya Mineral dan Konstruksi Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Survei Neraca Produksi Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Survei Tahunan Usaha Penggalian Bahan Industri dan Konstruksi (Galian URT) yang lengkap dan tepat waktu",
    "Terlaksananya Pelaksanaan Kegiatan Statistik Industri Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Survei Tahunan Perusahaan Pertambangan Mineral dan Batubara (Non Migas) yang lengkap dan tepat waktu",
    "Terlaksananya Pengelolaan Website Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Pelaksanaan Kegiatan Survei Tahunan perusahaan Industri Manufaktur (STPIM) V-IBS26 yang lengkap dan tepat waktu",
    "Terlaksananya Pembinaan Statistik Sektoral Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Penunjang Pelayanan Publik Lainnya",
    "Terlaksananya Pemenuhan Bukti Dukung Dokumen Implementasi Reformasi Birokrasi dan Zona Integritas yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Survei Captive Power yang lengkap dan tepat waktu",
    "Penyusunan CKP Pegawai yang tepat waktu",
    "Terlaksananya Quality Gates dan Manajemen Risiko lengkap dan tepat waktu",
    "Terlaksananya Pelaksanaan Kegiatan Survei Industri Mikro dan Kecil 2026 (VIMK26) Tahunan yang lengkap dan tepat waktu",
    "Terlaksananya kegiatan melakukan review dan memberikan penilaian konten media sosial BPS Kabupaten Bangka Selatan",
    "Terlaksananya Kegiatan Analisis dan Pengembangan Statistik Lainnya yang lengkap dan tepat waktu",
    "Terlaksana Rekrutmen Petugas Sensus Ekonomi 2026 yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Statistik Distribusi Lainnya yang sesuai jadwal",
    "Terlaksananya Pelaksanaan Kegiatan Updating Direktori Perusahaan Awal Industri Manufaktur (DPA) yang lengkap dan tepat waktu",
    "Terlaksananya Pembinaan Desa Cinta Statistik yang lengkap dan tepat waktu",
    "Terlaksananya Penyusunan Publikasi Kecamatan Dalam Angka yang Tepat Waktu",
    "Terlaksananya Kegiatan Penunjang Pengolahan Data dan Teknologi Informasi Serta Diseminasi Statistik Lainnya yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Pendukung Reformasi Birokrasi dan Zona Integritas yang lengkap dan tepat waktu",
    "Terlaksananya Pengolahan Data SE2026 yang Tepat Waktu",
    "Terlaksananya peran sebagai talent dalam pembuatan konten media sosial BPS Kabupaten Bangka Selatan yang tepat waktu",
    "Terlaksananya Pengelolaan mitra melalui manajemen mitra yang lengkap dan tepat waktu",
    "Terlaksananya Kegiatan Administrasi Statistik Industri yang lengkap dan tepat waktu",
    "Terlaksananya Pemeliharaan Sarana Prasarana Perkantoran Agar Tetap Dalam Kondisi Baik",
    "Tersedianya Sarana Prasarana PPID BPS Kabupaten Bangka Selatan yang Tepat Waktu",
    "Terlaksananya Pengolahan Data Susenas Semester II yang Tepat Waktu",
    "Pemenuhan dokumen SPI yang tepat waktu",
    "Pemeriksaan dan Pencairan Keuangan yang tepat waktu",
]

# Capaian yang berbeda dari pola "Persentase <RK> sebesar 100%" (nomor RK mulai dari 1)
_CAPAIAN_OVERRIDE = {
    27: "Persentase terlaksananya kegiatan Survei Perusahaan Perkebunan Bulanan (Sedapp) yang lengkap dan tepat waktu sebesar 100%",
    33: "Penyusunan Laporan Keuangan Satker Tahun 2026 yang Tepat Waktu terselesaikan 100%",
    46: "Penyusunan CKP Pegawai yang tepat waktu dan selesai 100%",
    65: "Pemenuhan dokumen SPI yang tepat waktu terselesaikan sebesar 100%",
    66: "Pemeriksaan dan Pencairan Keuangan yang tepat waktu selesai sebesar 100%",
}


def _capaian(no: int, title: str) -> str:
    return _CAPAIAN_OVERRIDE.get(no, f"Persentase {title} sebesar 100%")


RK_LIST = [
    {"no": i, "rk": t, "capaian": _capaian(i, t)}
    for i, t in enumerate(RK_TITLES, start=1)
]
