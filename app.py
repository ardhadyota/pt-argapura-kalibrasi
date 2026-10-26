import os
import io
import requests
import qrcode
import pandas as pd
from datetime import datetime
import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN & LAYOUT UTAMA
# ---------------------------------------------------------
st.set_page_config(
    page_title="PT ARGAPURA - Jidoka Calibration System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. ADVANCED ENTERPRISE CSS STYLING
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Reset & Font Family */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* CSS Penyesuaian Label Metric JIT (Mengecil & Text Wrap) */
    [data-testid="stMetricLabel"] p {
        font-size: 11px !important;
        line-height: 1.2 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }
    
    /* Mengatur padding kartu agar teks panjang muat dengan rapi */
    [data-testid="stMetric"] {
        padding: 12px 10px !important;
    }

    /* Custom Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid #1e293b;
        box-shadow: 4px 0 15px rgba(0,0,0,0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Radio Navigation Item Enhancement */
    div[data-testid="stRadio"] > label {
        display: none;
    }
    
    div[data-testid="stRadio"] > div {
        gap: 8px;
    }
    
    div[data-testid="stRadio"] > div > label {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 10px 14px;
        transition: all 0.25s ease;
        cursor: pointer;
    }
    
    div[data-testid="stRadio"] > div > label:hover {
        background: rgba(56, 189, 248, 0.12) !important;
        border-color: #38bdf8 !important;
        transform: translateX(4px);
    }

    /* Hero Banner Header */
    .hero-banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #0f172a 100%);
        padding: 26px 32px;
        border-radius: 16px;
        color: #ffffff;
        box-shadow: 0 12px 30px -10px rgba(2, 132, 199, 0.4);
        margin-bottom: 28px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 13px;
        color: #bae6fd;
        margin-top: 6px;
        font-weight: 400;
        letter-spacing: 0.2px;
    }

    /* PPDCA Card Component */
    .ppdca-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 25px;
    }
    
    .ppdca-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-top: 3.5px solid #38bdf8;
        border-radius: 12px;
        padding: 14px 16px;
        transition: all 0.3s ease;
    }
    
    .ppdca-box:hover {
        border-top-color: #0284c7;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    .ppdca-tag {
        font-size: 11px;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    
    .ppdca-text {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
        line-height: 1.4;
    }

    /* Custom Metric Styling */
    [data-testid="stMetric"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 14px !important;
        padding: 18px 20px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 30px !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }

    /* Status Connected Box */
    .status-badge {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 10px 14px;
        border-radius: 10px;
        text-align: center;
        font-size: 12px;
        font-weight: 500;
        color: #34d399;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #34d399;
        border-radius: 50%;
        box-shadow: 0 0 8px #34d399;
    }
    
    /* Horizontal Divider Style */
    hr {
        border-color: #334155 !important;
        opacity: 0.6;
        margin: 20px 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. BACKEND DATA FETCHING & PROCESSOR
# ---------------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSN3SuNIyQRzHXo9cRWOXQ72eLoGD_iY5Ays3nCDaw5C_3QAkyIR2_dOcMMPTaqZDTJR5ujZNmRVUXR/pub?gid=646903180&single=true&output=csv"

@st.cache_data(ttl=0)
def load_data(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    lines = response.text.splitlines()
    header_idx = next((i for i, line in enumerate(lines) if "Nomor Register" in line or "Nama Alat" in line), 4)
    clean_csv = "\n".join(lines[header_idx:])
    df = pd.read_csv(io.StringIO(clean_csv), on_bad_lines='skip')
    df.columns = [str(col).strip() for col in df.columns]
    
    reg_col = next((c for c in df.columns if "Register" in c), df.columns[1])
    exp_col = next((c for c in df.columns if "Expired" in c or "2027" in c), df.columns[-1])
    
    df['Nomor_Register'] = df[reg_col].fillna("").astype(str)
    df['Expired_Calibration'] = df[exp_col].fillna("").astype(str)
    df = df[df['Nomor_Register'].str.contains("AGP|AUP|AUL|AUW", case=False, na=False)]
    
    df['Expired_Date'] = pd.to_datetime(df['Expired_Calibration'], format='%d-%b-%y', errors='coerce')
    mask_nat = df['Expired_Date'].isna()
    if mask_nat.any():
        df.loc[mask_nat, 'Expired_Date'] = pd.to_datetime(df.loc[mask_nat, 'Expired_Calibration'], dayfirst=True, errors='coerce')
        
    return df

def generate_qr(text):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

try:
    data = load_data(SHEET_URL)
    today = pd.Timestamp(datetime.now().date())
    data['Sisa_Hari'] = (data['Expired_Date'] - today).dt.days
    
    status_list = []
    for sisa in data['Sisa_Hari']:
        if pd.isna(sisa):
            status_list.append("Data Tidak Valid")
        elif sisa < 0:
            status_list.append(f"EXPIRED ({abs(int(sisa))} Hari Lewat)")
        elif sisa <= 45:
            status_list.append(f"WARNING ({int(sisa)} Hari Lagi)")
        else:
            status_list.append("OK (Safe)")
    data['Status_Monitoring'] = status_list
except Exception:
    data = pd.DataFrame()



# Persistent State for Kaizen Data
if 'kaizen_logs' not in st.session_state:
    st.session_state['kaizen_logs'] = pd.DataFrame(columns=[
        'Nomor_Register', 'Why1', 'Why2', 'Why3', 'Why4', 'Why5_Akar', 
        'Countermeasure', 'PIC', 'Kategori_Akar', 'Target_Selesai', 'Tanggal_Input'
    ])

# ---------------------------------------------------------
# 4. SIDEBAR NAVIGATION DESIGN
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Centered Logo Wrapper
    col_l, col_logo, col_r = st.columns([1, 2, 1])
    with col_logo:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(BASE_DIR, "logo_argapura.png")
        
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
        else:
            st.image("logo_argapura.png", width=100)

    st.markdown("<h3 style='text-align: center; margin-top: 4px; margin-bottom: 0px; font-weight:700; font-size:18px;'>PT. ARGAPURA</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 11px; color: #38bdf8; font-weight:500; letter-spacing:0.8px; margin-bottom:15px;'>JIDOKA & GEMBA SYSTEM</p>", unsafe_allow_html=True)
    st.divider()
    
    menu = st.radio(
        "MAIN MENU",
        [
            "Dashboard Monitoring", 
            "Genchi Genbutsu (Scan QR)", 
            "Cetak Stiker QR Code",
            "JIT & Vendor Management",
            "Kaizen & 5-Why Analysis",
            "Notifikasi"
        ],
        index=0
    )
    st.divider()
    if st.button("🔄 Refresh Data / Hapus Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Status Connected Indicator
    st.markdown("""
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>System Connected</span>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. HERO HEADER DASHBOARD
# ---------------------------------------------------------
st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">PT ARGAPURA — CONTROL CENTER</div>
        <div class="hero-subtitle">Sistem Terintegrasi untuk Monitoring Kalibrasi Alat Ukur, Pengelolaan Vendor JIT, dan Inspeksi Gemba secara Real-Time</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MENU 1: DASHBOARD MONITORING (WITH LINE FILTER)
# ---------------------------------------------------------
if menu == "Dashboard Monitoring":
    # 1. PPDCA Framework Header
    st.markdown("""
        <div class="ppdca-grid">
            <div class="ppdca-box"><div class="ppdca-tag">1. Plan (Perencanaan)</div><div class="ppdca-text">Jadwal Kalibrasi Digital & PeringatanJatuh Tempo ≤45 hari.</div></div>
            <div class="ppdca-box"><div class="ppdca-tag">2. Do (Pelaksanaan)</div><div class="ppdca-text">Sinkronisasi Google Sheets & Bot WA Fonnte.</div></div>
            <div class="ppdca-box"><div class="ppdca-tag">3. Check (Pengawasan)</div><div class="ppdca-text">Andon Board visual Merah, Kuning, Hijau.</div></div>
            <div class="ppdca-box"><div class="ppdca-tag">4. Act (Jidoka)</div><div class="ppdca-text">Notifikasi otomatis & 5-Why Analysis.</div></div>
        </div>
    """, unsafe_allow_html=True)

    if not data.empty:
        # ---------------------------------------------------------
        # STYLING CUSTOM ANDON CARDS (EYE-CATCHING)
        # ---------------------------------------------------------
        st.markdown("""
        <style>
            .andon-container {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 25px;
            }
            .andon-card {
                border-radius: 12px;
                padding: 18px 20px;
                color: white;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .andon-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 25px rgba(0,0,0,0.4);
            }
            .card-total {
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            .card-expired {
                background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
                border: 1px solid #ef4444;
                box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
            }
            .card-warning {
                background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
                border: 1px solid #f59e0b;
                box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
            }
            .card-safe {
                background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
                border: 1px solid #10b981;
                box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
            }
            .andon-label {
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0.5px;
                opacity: 0.9;
                margin-bottom: 8px;
            }
            .andon-value {
                font-size: 32px;
                font-weight: 800;
                line-height: 1;
            }
            .andon-unit {
                font-size: 16px;
                font-weight: 500;
                opacity: 0.8;
                margin-left: 6px;
            }
        </style>
        """, unsafe_allow_html=True)

        # HITUNG METRIK DATA
        total_alat = len(data)
        total_global_merah = len(data[data['Status_Monitoring'].str.contains("EXPIRED", na=False)])
        total_global_kuning = len(data[data['Status_Monitoring'].str.contains("WARNING|PERINGATAN", na=False)])
        total_global_hijau = len(data[data['Status_Monitoring'].str.contains("OK|SAFE", na=False)])

        # RENDER TAMPILAN ANDON
        st.subheader("Monitoring Status Alat Ukur")
        
        st.markdown(f"""
        <div class="andon-container">
            <div class="andon-card card-total">
                <div class="andon-label">📋 Total Seluruh Alat</div>
                <div class="andon-value">{total_alat}<span class="andon-unit">Alat</span></div>
            </div>
            <div class="andon-card card-expired">
                <div class="andon-label">🚨 Out of Spec / Expired</div>
                <div class="andon-value">{total_global_merah}<span class="andon-unit">Alat</span></div>
            </div>
            <div class="andon-card card-warning">
                <div class="andon-label">⚠️ Peringatan (≤45 Hari)</div>
                <div class="andon-value">{total_global_kuning}<span class="andon-unit">Alat</span></div>
            </div>
            <div class="andon-card card-safe">
                <div class="andon-label">✅ Kondisi Safe (OK)</div>
                <div class="andon-value">{total_global_hijau}<span class="andon-unit">Alat</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()

        # ---------------------------------------------------------
        # BAGIAN 2: FILTER AREA LINE & JUMLAH ALAT TERKALIBRASI PER LINE
        # ---------------------------------------------------------
        loc_col = next((c for c in data.columns if "Lokasi" in c or "PIC" in c or "Line" in c), None)
        
        st.subheader("Analisis Spesifik Per Area Line")
        
        col_select, col_stat = st.columns([2, 1])
        
        with col_select:
            if loc_col:
                daftar_line = ["Semua Line / Lokasi"] + sorted(list(data[loc_col].dropna().unique()))
                pilih_line = st.selectbox("🏭 Pilih Line / Lokasi Alat Ukur:", daftar_line)
            else:
                pilih_line = "Semua Line / Lokasi"
                
        # Saring Data Berdasarkan Line Yang Dipilih
        data_filtered_line = data.copy()
        if pilih_line != "Semua Line / Lokasi" and loc_col:
            data_filtered_line = data_filtered_line[data_filtered_line[loc_col] == pilih_line]
            
        # Hitung Status Alat Khusus di Line Tersebut
        line_merah = len(data_filtered_line[data_filtered_line['Status_Monitoring'].str.contains("EXPIRED", na=False)])
        line_kuning = len(data_filtered_line[data_filtered_line['Status_Monitoring'].str.contains("WARNING", na=False)])
        line_hijau = len(data_filtered_line[data_filtered_line['Status_Monitoring'].str.contains("OK", na=False)])
        
        with col_stat:
            st.metric(
                label=f"📍 Total Alat Terkalibrasi ({pilih_line})", 
                value=f"{len(data_filtered_line)} Alat"
            )
            
        # Tampilkan Ringkasan Status Khusus Line Ini Jika Memilih Spesifik Line
        if pilih_line != "Semua Line / Lokasi":
            st.caption(f"Status Alat di **{pilih_line}**: 🟢 {line_hijau} Safe | 🟡 {line_kuning} Warning | 🔴 {line_merah} Expired")

        st.divider()

        # ---------------------------------------------------------
        # BAGIAN 3: TABEL RINCIAN ALAT DI LINE TERSEBUT
        # ---------------------------------------------------------
        st.subheader(f"Daftar Inventaris Alat Ukur ({pilih_line})")
        selected_status = st.selectbox("Filter Status Alat:", ["Semua Status Alat", "Merah (EXPIRED)", "Kuning (WARNING ≤45 Hari)", "Hijau (OK)"])
        
        filtered_df = data_filtered_line.copy()
        if selected_status == "Merah (EXPIRED)":
            filtered_df = filtered_df[filtered_df['Status_Monitoring'].str.contains("EXPIRED", na=False)]
        elif selected_status == "Kuning (WARNING ≤45 Hari)":
            filtered_df = filtered_df[filtered_df['Status_Monitoring'].str.contains("WARNING", na=False)]
        elif selected_status == "Hijau (OK)":
            filtered_df = filtered_df[filtered_df['Status_Monitoring'].str.contains("OK", na=False)]
            
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)


elif menu == "Genchi Genbutsu (Scan QR)":
    st.subheader("Genchi Genbutsu (Gemba Walk & Mobile Inspection)")
    st.info("Arahkan kamera HP ke stiker QR Code yang tertempel di fisik alat ukur.")
    
    qr_code_val = qrcode_scanner(key="gemba_scanner_pro")
    if qr_code_val:
        st.success(f"✅ QR Code Terdeteksi: **{qr_code_val}**")
        if not data.empty:
            matched = data[data['Nomor_Register'].str.upper() == str(qr_code_val).strip().upper()]
            if not matched.empty:
                row = matched.iloc[0]
                st.markdown("---")
                st.subheader(f"📌 Detail Alat: {row.get('Nama Alat', row.get('Nama_Alat', 'Alat Ukur'))}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Nomor Register", row['Nomor_Register'])
                col2.metric("Expired Date", row['Expired_Calibration'])
                col3.metric("Status Monitoring", row['Status_Monitoring'])
            else:
                st.warning("⚠️ Data alat tidak ditemukan dalam database.")

elif menu == "Cetak Stiker QR Code":
    st.subheader("🖨️ Cetak Stiker QR Code Alat Ukur")
    st.write(
        "Gunakan fitur ini untuk mengunduh stiker QR Code berformat Calibration"
        " Reminder untuk ditempel di fisik alat ukur."
    )

    # Deteksi dataframe yang aktif (df atau data)
    df_active = data if "data" in locals() and not data.empty else df

    if not df_active.empty:
        # Cari nama kolom yang menampung Nomor Register secara otomatis
        reg_col = None
        for col in df_active.columns:
            if (
                "nomor" in str(col).lower()
                or "register" in str(col).lower()
                or "no" in str(col).lower()
            ):
                reg_col = col
                break

        if reg_col is None:
            reg_col = df_active.columns[
                1
            ]  # Default ke Kolom B jika header tidak terdeteksi

        list_alat = df_active[reg_col].dropna().unique()
        pilih_alat = st.selectbox("Pilih Nomor Register Alat:", list_alat)

        # Fungsi pencocokan tanpa menghiraukan spasi dan huruf besar/kecil
        def clean_val(v):
            return str(v).replace(" ", "").strip().lower()

        # Filter baris alat
        matched_rows = df_active[
            df_active[reg_col].apply(clean_val) == clean_val(pilih_alat)
        ]

        if not matched_rows.empty:
            row_data = matched_rows.iloc[0]

            # Fungsi fleksibel: Cari berdasarkan nama header ATAU nomor urut kolom di Spreadsheet
            def get_field(possible_names, col_index_fallback):
                # 1. Cari via nama header
                for name in possible_names:
                    for col in row_data.index:
                        if clean_val(name) in clean_val(col):
                            val = str(row_data[col]).strip()
                            if val and val.lower() != "nan":
                                return val
                # 2. Fallback via nomor kolom spreadsheet (0=A, 1=B, 2=C, 3=D, dst)
                try:
                    val = str(row_data.iloc[col_index_fallback]).strip()
                    if val and val.lower() != "nan":
                        return val
                except:
                    pass
                return "-"

            # Ambil data alat ukur (dengan cadangan posisi kolom A-M)
            nama_alat = get_field(["Nama_Alat", "Nama Alat"], 2)  # Kolom C
            merk = get_field(["Merk"], 3)  # Kolom D
            no_seri = get_field(["No_Seri", "No Seri"], 4)  # Kolom E
            rentang = get_field(
                ["Rentang Pemakaian", "Rentang_Pemakaian"], 6
            )  # Kolom G
            eq_range = get_field(
                ["Equipment_Range", "Equipment Range"], 5
            )  # Kolom F
            cal_date = get_field(
                [
                    "Expired_Calibration",
                    "Calibration Date",
                    "Last_Calibration_SD",
                    "Next Calibration",
                ],
                12,
            )  # Kolom M

            # Format teks stiker
            qr_text = f"""CALIBRATION REMINDER
----------------------------------
Nama Alat        : {nama_alat}
Merk             : {merk}
No. Seri         : {no_seri}
No. Reg          : {pilih_alat}
Rentang Pemakaian: {rentang}
Equipment Range  : {eq_range}
Calibration Date : {cal_date}
----------------------------------
PT ARGAPURA - JIDOKA SYSTEM"""

            col1, col2 = st.columns([1, 2])

            with col1:
                import qrcode
                from io import BytesIO

                qr = qrcode.make(pilih_alat)
                buf = BytesIO()
                qr.save(buf)
                st.image(buf.getvalue(), caption=f"QR Code: {pilih_alat}")

                st.download_button(
                    label="Unduh QR Code (.PNG)",
                    data=buf.getvalue(),
                    file_name=f"QR_{pilih_alat}.png",
                    mime="image/png",
                )

            with col2:
                st.subheader("Informasi Barcode:")
                st.code(qr_text, language="text")
        else:
            st.warning("Data detail tidak ditemukan.")
    else:
        st.error("Data spreadsheet kosong atau tidak terload.")


                
    return "-"

nama_alat = get_val(["Nama_Alat", "Nama Alat"])
merk = get_val(["Merk"])
no_seri = get_val(["No_Seri", "No Seri"])
rentang = get_val(["Rentang Pemakaian", "Rentang_Pemakaian"])
eq_range = get_val(["Equipment_Range", "Equipment Range"])
cal_date = get_val(["Expired_Calibration", "Calibration Date", "Last_Calibration_SD", "Next Calibration"])

# Format teks di dalam QR Code persis seperti stiker fisik (Mitutoyo)
qr_text = f"""CALIBRATION REMINDER
----------------------------------
Nama Alat        : {nama_alat}
Merk             : {merk}
No. Seri         : {no_seri}
No. Reg          : {pilih_alat}
Rentang Pemakaian: {rentang}
Equipment Range  : {eq_range}
Calibration Date : {cal_date}
----------------------------------
PT ARGAPURA - JIDOKA SYSTEM"""


            
            # Generate QR Code dari teks berformat stiker fisik
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_bytes = buf.getvalue()

            col_img, col_btn = st.columns([1, 2])
            with col_img:
                st.image(qr_bytes, caption=f"QR Code: {pilih_alat}", width=180)
            with col_btn:
                st.markdown("**Informasi Barcode:**")
                st.code(qr_text, language="text")
                st.download_button("Unduh QR Code (.PNG)", qr_bytes, file_name=f"QR_{pilih_alat}.png", mime="image/png")

elif menu == "JIT & Vendor Management":
    st.subheader("Just-In-Time (JIT) Tracking & Vendor Lead Time")
    if not data.empty:
        if 'Status_JIT' not in data.columns:
            data['Status_JIT'] = "In Use"
            
        col_j1, col_j2, col_j3, col_j4, col_j5 = st.columns(5)
        col_j1.metric("🟢 In Use", len(data[data['Status_JIT'] == "In Use"]))
        col_j2.metric("🟡 Preparing", len(data[data['Status_JIT'] == "Preparing for Cal"]))
        col_j3.metric("🚚 Sent to Vendor", len(data[data['Status_JIT'] == "Sent to Vendor/Lab"]))
        col_j4.metric("🔬 In Calibration", len(data[data['Status_JIT'] == "In Calibration"]))
        col_j5.metric("✅ Returned & Verified", len(data[data['Status_JIT'] == "Returned & Verified"]))

elif menu == "Kaizen & 5-Why Analysis":
    st.subheader("Kaizen & Root Cause Analysis (5-Why)")
    tab_form, tab_report = st.tabs(["📝 Form Analisis 5-Why", "📊 Laporan & Trend Kaizen"])
    
    with tab_form:
        if not data.empty:
            data_expired = data[data['Status_Monitoring'].str.contains("EXPIRED", na=False)]
            
            if not data_expired.empty:
                st.error(f"🚨 Terdeteksi **{len(data_expired)} alat ukur Expired**. Harap isi analisis 5-Why di bawah ini untuk tindakan pencegahan berulang (Jidoka/Kaizen).")
                
                # Form Input 5-Why
                with st.form("form_5why_kaizen"):
                    st.markdown("### Analisis Akar Masalah")
                    
                    # 1. Pilih Alat Ukur Expired
                    pilih_expired = st.selectbox(
                        "Pilih Nomor Register Alat (Berstatus Expired):", 
                        data_expired['Nomor_Register'].unique()
                    )
                    
                    detail_alat = data_expired[data_expired['Nomor_Register'] == pilih_expired].iloc[0]
                    st.info(f"📌 **Detail Alat Selected**: {detail_alat.get('Nama Alat', detail_alat.get('Nama_Alat', 'Alat Ukur'))} | **Status**: {detail_alat['Status_Monitoring']}")
                    
                    st.divider()
                    
                    # 2. FAKTOR KATEGORI 4M1E PALING ATAS
                    st.markdown("#### Kategori Faktor Utama (4M1E)")
                    kategori_akar = st.selectbox(
                        "Klasifikasi Faktor Penyebab Masalah:", 
                        ["Man", "Machine", "Method", "Material", "Environment"]
                    )
                    
                    st.divider()
                    
                    # 3. VERTICAL DRILL-DOWN 5-WHY ANALYSIS
                    st.markdown("#### 5-Why Analysis")
                    
                    w1 = st.text_input("↓ Why 1")
                    w2 = st.text_input("↓ Why 2")
                    w3 = st.text_input("↓ Why 3")
                    w4 = st.text_input("↓ Why 4")
                    w5 = st.text_input("↓ Why 5")

                    st.divider()
                    
                    # 4. COUNTERMEASURE & ACTION PLAN
                    st.markdown("#### Countermeasure (Rencana Perbaikan & Action Plan)")
                    col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
                    with col_c1:
                        countermeasure = st.text_area("Tindakan Korektif (Countermeasure):", placeholder="Contoh: Mengaktifkan Bot WA Peringatan otomatis H-45 dan sistem stiker QR Code Gemba")
                    with col_c2:
                        pic_target = st.text_input("PIC Penanggung Jawab:", placeholder="Nama PIC QC")
                    with col_c3:
                        target_selesai = st.date_input("Target Selesai Perbaikan:")

                    btn_submit = st.form_submit_button("Simpan")
                    
                    if btn_submit:
                        payload = {
                            'Tanggal_Input': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'Nomor_Register': pilih_expired,
                            'Kategori_Akar': kategori_akar,
                            'Why1': w1, 'Why2': w2, 'Why3': w3, 'Why4': w4, 'Why5_Akar': w5,
                            'Countermeasure': countermeasure,
                            'PIC': pic_target,
                            'Target_Selesai': target_selesai.strftime('%Y-%m-%d')
                        }
                        
                        # 1. Simpan ke memory lokal (Dashboard Chart)
                        new_log = pd.DataFrame([payload])
                        st.session_state['kaizen_logs'] = pd.concat([st.session_state['kaizen_logs'], new_log], ignore_index=True)
                        
                        # 2. Kirim ke Google Sheets via Webhook
                        WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxUpzxbPwzKdZaXl46n1GWXeRa7zdr2Tn3DaD1hKyZWtdDJ0tpGxMCzfZFFE1KHa_fQ/exec"
                        
                        try:
                            res = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                            if res.status_code == 200:
                                st.success(f"✅ Analisis 5-Why untuk alat **{pilih_expired}** BERHASIL tersimpan ke Sheet 'Log_Kaizen_5Why' di Google Sheets!")
                            else:
                                st.warning("⚠️ Tersimpan di dashboard, namun gagal terhubung ke Google Sheets.")
                        except Exception as e:
                            st.success(f"✅ Analisis tersimpan lokal di Dashboard.")
                
    with tab_report:
        st.markdown("### 📊 Laporan Record Analisis Akar Masalah")
        logs_df = st.session_state['kaizen_logs']
        if not logs_df.empty:
            col_chart1, col_chart2 = st.columns([1, 2])
            with col_chart1:
                st.markdown("#### Distribusi Akar Masalah (4M1E)")
                st.bar_chart(logs_df['Kategori_Akar'].value_counts())
            with col_chart2:
                st.markdown("#### Tabel Riwayat 5-Why Analysis")
                st.dataframe(logs_df, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Belum ada inputan analisis 5-Why. Laporan akan terupdate otomatis setelah mengisi Form 5-Why di tab sebelah.")

elif menu == "Notifikasi":
    st.subheader("Notifikasi WhatsApp")
    st.text_input("Fonnte API Token:", value="C133Jd1Aiba7EaWvxmrE", type="password")
    st.text_input("Target Group ID / Nomor PIC:")
    st.button("Send")
