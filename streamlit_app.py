import hashlib
import io
import os
import re
import secrets
import time as _time
from datetime import date, time

import streamlit as st

from rk_data import RK_LIST

# ───────────────────────── Konfigurasi ─────────────────────────
st.set_page_config(page_title="CKP Generator · BPS 1905", page_icon="📋", layout="wide")

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]
TRIWULAN = {"Triwulan I": (1, 2, 3), "Triwulan II": (4, 5, 6),
            "Triwulan III": (7, 8, 9), "Triwulan IV": (10, 11, 12)}
HEADER = ["No", "Tanggal", "Jam", "Rencana Kinerja", "Kegiatan", "Capaian",
          "Bukti Dukung", "Folder Kegiatan"]
FOLDER_MIME = "application/vnd.google-apps.folder"
SHEET_MIME = "application/vnd.google-apps.spreadsheet"

ROOT_FOLDER_ID = st.secrets.get("root_folder_id", "1CXU1j8YEaFw3jdvM1lNttvMJAvB0WZW7")
ALLOWED = [e.lower() for e in st.secrets.get("allowed_emails", [])]
RK_OPTIONS = {f"{r['no']:02d}. {r['rk']}": r for r in RK_LIST}

st.markdown("""
<style>
.block-container{padding-top:1.4rem;max-width:1100px}
.hero{background:linear-gradient(120deg,#0f4c81,#1e88a8);color:#fff;padding:1.1rem 1.4rem;
      border-radius:16px;margin-bottom:1rem}
.hero h2{margin:0;color:#fff}.hero p{margin:.2rem 0 0;opacity:.9}
.chip{display:inline-block;background:#e8f1fb;color:#0f4c81;padding:.15rem .7rem;
      border-radius:999px;font-size:.85rem;margin-right:.4rem}
</style>
""", unsafe_allow_html=True)


# ───────────────────────── OAuth (persetujuan akses Drive) ─────────────────────────
@st.cache_resource
def _pending_states() -> dict:
    return {}


def _flow():
    from google_auth_oauthlib.flow import Flow
    redirect = st.secrets["google"]["redirect_uri"]
    if redirect.startswith("http://localhost"):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    cfg = {"web": {
        "client_id": st.secrets["google"]["client_id"],
        "client_secret": st.secrets["google"]["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }}
    return Flow.from_client_config(cfg, scopes=SCOPES, redirect_uri=redirect,
                                   autogenerate_code_verifier=False)


def handle_callback():
    qp = st.query_params
    code, state = qp.get("code"), qp.get("state")
    if not code:
        return
    pend = _pending_states()
    if state not in pend or _time.time() - pend.pop(state) > 600:
        st.query_params.clear()
        st.error("Sesi login tidak valid atau kedaluwarsa. Silakan login ulang.")
        return
    flow = _flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    from google.auth.transport.requests import AuthorizedSession
    info = AuthorizedSession(creds).get("https://www.googleapis.com/oauth2/v2/userinfo").json()
    email = info.get("email", "").lower()
    if ALLOWED and email not in ALLOWED:
        st.query_params.clear()
        st.error(f"Akun {email} tidak diizinkan memakai aplikasi ini.")
        return
    st.session_state.creds = creds
    st.session_state.email = email
    st.query_params.clear()
    st.rerun()


def login_gate():
    st.markdown('<div class="hero"><h2>📋 CKP Generator</h2>'
                '<p>BPS Kabupaten Bangka Selatan · Capaian Kinerja Pegawai</p></div>',
                unsafe_allow_html=True)
    handle_callback()
    st.subheader("🔐 Persetujuan Akses Google Drive")
    st.write(
        "Aplikasi membutuhkan izin **Google Drive** dan **Google Sheets** dari akun Anda "
        "untuk membuat folder, mengunggah bukti dukung, dan mengisi rekap CKP. "
        "Link aplikasi saja **tidak cukup**: setiap pengunjung harus login dan menyetujui "
        "izin dengan akun Google-nya sendiri, dan hanya bisa mengakses Drive miliknya."
    )
    flow = _flow()
    state = secrets.token_urlsafe(24)
    _pending_states()[state] = _time.time()
    url, _ = flow.authorization_url(access_type="offline", prompt="consent", state=state,
                                    include_granted_scopes="true")
    st.link_button("✅ Setujui & Masuk dengan Google", url, type="primary")
    st.caption("Izin dapat dicabut kapan saja di myaccount.google.com/permissions")


if "creds" not in st.session_state:
    login_gate()
    st.stop()


# ───────────────────────── Google API helpers ─────────────────────────
@st.cache_resource(show_spinner=False)
def _build(kind: str, version: str, _creds, token_key: str):
    from googleapiclient.discovery import build
    return build(kind, version, credentials=_creds, cache_discovery=False)


def drive():
    return _build("drive", "v3", st.session_state.creds, st.session_state.email)


def sheets():
    return _build("sheets", "v4", st.session_state.creds, st.session_state.email)


def _q(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def find_child(name, parent, mime=None):
    q = f"name='{_q(name)}' and '{parent}' in parents and trashed=false"
    if mime:
        q += f" and mimeType='{mime}'"
    r = drive().files().list(q=q, fields="files(id,webViewLink)", pageSize=1,
                             supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    return (r["files"] or [None])[0]


def get_or_create_folder(name, parent):
    f = find_child(name, parent, FOLDER_MIME)
    if f:
        return f["id"]
    return drive().files().create(
        body={"name": name, "mimeType": FOLDER_MIME, "parents": [parent]},
        fields="id", supportsAllDrives=True).execute()["id"]


def ensure_month(tri: str, year: int, month: int) -> dict:
    """Buat (jika belum ada) Triwulan/Bulan/Spreadsheet. Hasil di-cache di session."""
    cache = st.session_state.setdefault("ctx", {})
    key = (tri, year, month)
    if key in cache:
        return cache[key]
    tri_id = get_or_create_folder(tri, ROOT_FOLDER_ID)
    mon_name = f"Bulan {BULAN[month - 1]} {year}"
    mon_id = get_or_create_folder(mon_name, tri_id)
    sheet_name = f"CKP {BULAN[month - 1]} {year}"
    sh = find_child(sheet_name, mon_id, SHEET_MIME)
    if not sh:
        sh = drive().files().create(
            body={"name": sheet_name, "mimeType": SHEET_MIME, "parents": [mon_id]},
            fields="id,webViewLink", supportsAllDrives=True).execute()
        sid = sh["id"]
        sheets().spreadsheets().values().update(
            spreadsheetId=sid, range="A1:H1", valueInputOption="RAW",
            body={"values": [HEADER]}).execute()
        sheets().spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": [
            {"repeatCell": {"range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1},
                            "cell": {"userEnteredFormat": {"textFormat": {"bold": True},
                                     "backgroundColor": {"red": .85, "green": .92, "blue": .98}}},
                            "fields": "userEnteredFormat(textFormat,backgroundColor)"}},
            {"updateSheetProperties": {"properties": {"sheetId": 0,
                                       "gridProperties": {"frozenRowCount": 1}},
                                       "fields": "gridProperties.frozenRowCount"}},
            {"repeatCell": {"range": {"sheetId": 0, "startRowIndex": 1},
                            "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP",
                                     "verticalAlignment": "TOP"}},
                            "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}},
        ]}).execute()
    ctx = {"month_id": mon_id, "sheet_id": sh["id"],
           "sheet_url": f"https://docs.google.com/spreadsheets/d/{sh['id']}",
           "month_url": f"https://drive.google.com/drive/folders/{mon_id}"}
    cache[key] = ctx
    return ctx


def unique_folder_name(base, parent):
    name, n = base, 0
    while find_child(name, parent, FOLDER_MIME):
        n += 1
        name = f"{base}_{n}"
    return name


def clean(s: str, limit=90) -> str:
    s = re.sub(r'[\\/:*?"<>|\r\n]+', " ", s).strip()
    return re.sub(r"\s+", " ", s)[:limit].strip()


def drive_id(link: str):
    m = re.search(r"/(?:d|folders)/([\w-]{15,})|[?&]id=([\w-]{15,})", link)
    return (m.group(1) or m.group(2)) if m else None


def fmt_date(d: date, with_year=True) -> str:
    return f"{d.day:02d}{BULAN[d.month - 1]}" + (f"{d.year}" if with_year else "")


def date_label(d1: date, d2: date) -> str:
    if d1 == d2:
        return fmt_date(d1)
    if (d1.month, d1.year) == (d2.month, d2.year):
        return f"{d1.day:02d}-{fmt_date(d2)}"
    return f"{fmt_date(d1)}-{fmt_date(d2)}"


def save_entry(ctx, rk, kegiatan, d1, d2, jam, files, links):
    from googleapiclient.http import MediaIoBaseUpload
    keg = clean(kegiatan)
    with st.status("Menyimpan ke Google Drive…", expanded=True) as status:
        st.write("📁 Membuat folder kegiatan")
        base = f"{date_label(d1, d2)}_{keg}"
        fname = unique_folder_name(base, ctx["month_id"])
        fid = get_or_create_folder(fname, ctx["month_id"])
        folder_url = f"https://drive.google.com/drive/folders/{fid}"

        urls, n = [], 0
        for name, data, mime in files:
            n += 1
            ext = os.path.splitext(name)[1] or ".png"
            st.write(f"⬆️ Mengunggah bukti {n}")
            media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime, resumable=False)
            f = drive().files().create(
                body={"name": f"Bukti Dukung_{keg}_{n}{ext}", "parents": [fid]},
                media_body=media, fields="webViewLink", supportsAllDrives=True).execute()
            urls.append(f["webViewLink"])
        for link in links:
            tid = drive_id(link)
            if not tid:
                st.warning(f"Link tidak dikenali, dilewati: {link}")
                continue
            n += 1
            st.write(f"🔗 Membuat shortcut bukti {n}")
            f = drive().files().create(
                body={"name": f"Bukti Dukung_{keg}_{n}", "mimeType": "application/vnd.google-apps.shortcut",
                      "parents": [fid], "shortcutDetails": {"targetId": tid}},
                fields="webViewLink", supportsAllDrives=True).execute()
            urls.append(f.get("webViewLink", link))

        st.write("📊 Menambahkan baris ke spreadsheet")
        tgl = d1.strftime("%d/%m/%Y") if d1 == d2 else f"{d1:%d/%m/%Y} - {d2:%d/%m/%Y}"
        row = ["=ROW()-1", tgl, jam or "-", rk["rk"], kegiatan.strip(), rk["capaian"],
               "\n".join(urls) or "-", folder_url]
        sheets().spreadsheets().values().append(
            spreadsheetId=ctx["sheet_id"], range="A1", valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS", body={"values": [row]}).execute()
        status.update(label="Tersimpan ✅", state="complete", expanded=False)
    return folder_url


# ───────────────────────── Sidebar ─────────────────────────
today = date.today()
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.email}**")
    if st.button("Keluar & cabut sesi", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.divider()
    year = st.number_input("Tahun", 2024, 2035, 2026, step=1)
    default_tri = (today.month - 1) // 3
    tri = st.radio("Triwulan", list(TRIWULAN), index=default_tri)
    months = TRIWULAN[tri]
    mdef = months.index(today.month) if today.month in months else 0
    month = st.selectbox("Bulan", months, index=mdef, format_func=lambda m: f"{BULAN[m - 1]} {year}")

st.markdown(f'<div class="hero"><h2>📋 CKP · {BULAN[month - 1]} {year}</h2>'
            f'<p>{tri} · Drive/…/{tri}/Bulan {BULAN[month - 1]} {year}</p></div>',
            unsafe_allow_html=True)

# ───────────────────────── Input ─────────────────────────
tab_input, tab_rekap = st.tabs(["✍️ Input Kegiatan", "📊 Rekap Bulan Ini"])
nonce = st.session_state.setdefault("nonce", 0)
pasted = st.session_state.setdefault("pasted", {})

with tab_input:
    rk_label = st.selectbox("Rencana Kinerja (RK)", list(RK_OPTIONS), index=None,
                            placeholder="Ketik untuk mencari RK…", key=f"rk{nonce}")
    rk = RK_OPTIONS.get(rk_label) if rk_label else None

    # Capaian otomatis terisi mengikuti RK (key berubah per RK → nilai default ikut berganti)
    st.text_area("Capaian", value=rk["capaian"] if rk else "", disabled=rk is None,
                 key=f"cap{nonce}_{rk['no'] if rk else 0}", height=80,
                 placeholder="Terisi otomatis setelah RK dipilih")

    first, last = date(year, month, 1), date(year, month, 28)
    # hari terakhir bulan
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    last = date.fromordinal(nxt.toordinal() - 1)
    dv = min(max(today, first), last)

    c1, c2 = st.columns(2)
    with c1:
        use_range = st.checkbox("Gunakan rentang tanggal", key=f"ur{nonce}")
        if use_range:
            r = st.date_input("Rentang tanggal", (dv, dv), min_value=first, max_value=last,
                              format="DD/MM/YYYY", key=f"dr{nonce}")
            d1, d2 = (r[0], r[-1]) if len(r) else (dv, dv)
        else:
            d1 = d2 = st.date_input("Tanggal", dv, min_value=first, max_value=last,
                                    format="DD/MM/YYYY", key=f"d1{nonce}")
    with c2:
        use_time = st.checkbox("Gunakan rentang jam", key=f"ut{nonce}")
        jam = None
        if use_time:
            t1, t2 = st.columns(2)
            ts = t1.time_input("Mulai (WIB)", time(8, 0), step=600, key=f"ts{nonce}")
            te = t2.time_input("Selesai (WIB)", time(16, 0), step=600, key=f"te{nonce}")
            jam = f"{ts:%H.%M} - {te:%H.%M} WIB"
            if te <= ts:
                st.warning("Jam selesai harus setelah jam mulai.")

    kegiatan = st.text_area("Kegiatan", key=f"keg{nonce}", height=90,
                            placeholder="Contoh: Melakukan Pengawasan SKGB 2026 di Desa Sadai")

    st.markdown("**Bukti Dukung**")
    up = st.file_uploader("Unggah gambar", type=["png", "jpg", "jpeg", "webp"],
                          accept_multiple_files=True, key=f"up{nonce}")
    try:
        from streamlit_paste_button import paste_image_button
        res = paste_image_button("📋 Paste gambar dari clipboard", key=f"pb{nonce}")
        if res.image_data is not None:
            buf = io.BytesIO()
            res.image_data.save(buf, format="PNG")
            data = buf.getvalue()
            pasted.setdefault(hashlib.md5(data).hexdigest(), data)
    except ImportError:
        st.caption("Install `streamlit-paste-button` untuk fitur paste gambar.")
    if pasted:
        st.caption(f"{len(pasted)} gambar tertempel")
        if st.button("Hapus gambar tertempel"):
            pasted.clear()
            st.rerun()
    links_txt = st.text_area("Link Google Drive (satu per baris) → dibuatkan shortcut",
                             key=f"lk{nonce}", height=70,
                             placeholder="https://drive.google.com/file/d/…")

    files = [(f.name, f.getvalue(), f.type or "image/png") for f in up or []]
    files += [(f"paste_{i}.png", b, "image/png") for i, b in enumerate(pasted.values(), 1)]
    links = [l.strip() for l in links_txt.splitlines() if l.strip()]

    if files:
        with st.expander(f"Pratinjau {len(files)} gambar"):
            cols = st.columns(4)
            for i, (n, b, _) in enumerate(files):
                cols[i % 4].image(b, caption=n, width=150)

    ready = rk and kegiatan.strip() and (not use_time or te > ts)
    if st.button("💾 Simpan ke Drive & Spreadsheet", type="primary", disabled=not ready):
        try:
            ctx = ensure_month(tri, int(year), month)
            url = save_entry(ctx, rk, kegiatan, d1, d2, jam, files, links)
            st.success("Kegiatan tersimpan.")
            st.link_button("Buka folder kegiatan", url)
            pasted.clear()
            st.session_state.nonce += 1
            st.session_state.last_saved = url
        except Exception as e:  # noqa: BLE001
            st.error(f"Gagal menyimpan: {e}")
    elif not ready:
        st.caption("Pilih RK dan isi Kegiatan untuk mengaktifkan tombol simpan.")

# ───────────────────────── Rekap (dimuat hanya saat diminta) ─────────────────────────
with tab_rekap:
    if st.button("🔄 Muat rekap"):
        try:
            ctx = ensure_month(tri, int(year), month)
            vals = sheets().spreadsheets().values().get(
                spreadsheetId=ctx["sheet_id"], range="A1:H").execute().get("values", [])
            st.link_button("Buka Spreadsheet", ctx["sheet_url"])
            st.link_button("Buka Folder Bulan", ctx["month_url"])
            if len(vals) > 1:
                import pandas as pd
                rows = [r + [""] * (len(HEADER) - len(r)) for r in vals[1:]]
                df = pd.DataFrame(rows, columns=HEADER)
                st.dataframe(df, use_container_width=True, hide_index=True,
                             column_config={"Folder Kegiatan": st.column_config.LinkColumn(
                                 "Folder Kegiatan", display_text="Buka")})
            else:
                st.info("Belum ada kegiatan pada bulan ini.")
        except Exception as e:  # noqa: BLE001
            st.error(f"Gagal memuat rekap: {e}")
