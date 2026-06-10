import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import requests
import sys
from streamlit_option_menu import option_menu
import subprocess
import os
import base64
import io

# ตรวจสอบว่ารันผ่าน Streamlit หรือไม่ ถ้าไม่ใช่ (เช่น กดปุ่ม Run ปกติ) ให้รัน streamlit อัตโนมัติ
if not st.runtime.exists():
    print("กำลังเปิดหน้าเว็บ Streamlit อัตโนมัติ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", sys.argv[0]])
    sys.exit(0)

from read_all_csv import read_all_csv_in_directory, process_pea_data

# ตั้งค่าฟอนต์เริ่มต้นให้กับกราฟ Plotly ทั้งหมด
pio.templates.default = "plotly_white"
pio.templates["plotly_white"].layout.font.family = "'Noto Sans Thai', 'Kanit', 'Leelawadee UI', sans-serif"

# ตั้งค่าหน้าจอ Dashboard
st.set_page_config(page_title="Solar Analytics", layout="wide", initial_sidebar_state="expanded")

# --- ปรับแต่งหน้าตาและ CSS (Global Styling & Fonts) ---
st.markdown("""
<style>
/* โหลดฟอนต์ Noto Sans Thai มาจาก Google Fonts (ต้องอยู่บนสุดเสมอ) */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;600;700&display=swap');

/* ซ่อนเมนู default */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}


/* พื้นหลัง */
.stApp {
    background:
    linear-gradient(
    180deg,
    #ffffff 0%,
    #f8fafc 100%
    );
}

/* บังคับใช้ฟอนต์ Noto Sans Thai กับทุกส่วนของเว็บ */
html, body, div, span, p, h1, h2, h3, h4, h5, h6, button, input, select, textarea, label, [class*="st-"], [class*="css-"] {
    font-family: 'Noto Sans Thai', 'Kanit', 'Prompt', 'Leelawadee UI', 'Sukhumvit Set', sans-serif !important;
}

/* ล็อก Sidebar ให้กางตลอดเวลา (เฉพาะจอคอม/แท็บเล็ต) */
@media (min-width: 768px) {
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
        width: 260px !important;
        transform: none !important;
        visibility: visible !important;
    }
}

/* Sidebar Glass Effect */
section[data-testid="stSidebar"] {
    background:
    linear-gradient(
    180deg,
    #020617 0%,
    #0f172a 45%,
    #172554 100%
    );
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ลด padding */
section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

/* กล่องเมนู */
.st-emotion-cache-1v0mbdj,
.st-emotion-cache-16txtl3{

    background:#0f172a;

    border:none;

    border-radius:0px;

    box-shadow:none;
}

/* โลโก้ */
.logo-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding-top: 10px;
}
.logo-img {
    height: 130px;
    max-width: 100%;
    object-fit: contain;
}
.logo-text {
    font-size: 24px;
    font-weight: 800;
    color: white;
    text-align: center;
}

/* แก้ไขสีตัวอักษรใน Sidebar ให้เป็นสีขาว (สำหรับ Header/Label ของตัวกรอง) */
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: white !important;
}
/* ยกเว้นสีตัวอักษรข้างในกล่อง Select/Multiselect ให้เป็นสีดำตามเดิม */
section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #0f172a !important;
}

/* ตกแต่ง Metric Cards (กล่องตัวเลข) */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    padding: 15px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    border-left: 5px solid #0284c7;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

/* ตกแต่ง Container (แบบ Card 3D) ให้แสดงผลทุกหน้า */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
    background-color: #ffffff;
    box-shadow: 
        0 8px 15px rgba(0,0,0,0.05), 
        0 3px 6px rgba(0,0,0,0.02), 
        inset 0 2px 4px rgba(255,255,255,0.8);
    border: 1px solid #f0f0f0;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 
        0 15px 25px rgba(0,0,0,0.1), 
        0 5px 10px rgba(0,0,0,0.04);
    border-color: #e2e8f0;
}

/* ปุ่มทั่วไป (ปุ่มกด/ปุ่มลิงก์) */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

/* --- HERO SECTION --- */
.hero {
    background: linear-gradient(135deg,#081028,#1e3a8a);
    min-height: 420px;
    border-radius: 35px;
    padding: 70px;
    display: flex;
    align-items: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    color: white;
    margin-bottom: 30px;
}

/* แสงพื้นหลัง */
.hero::before {
    content: "";
    position: absolute;
    width: 500px;
    height: 500px;
    background: rgba(59,130,246,0.15);
    border-radius: 50%;
    top: -200px;
    right: -100px;
    filter: blur(40px);
}

/* badge */
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.1);
    padding: 10px 20px;
    border-radius: 50px;
    color: #dbeafe;
    font-size: 14px;
    margin-bottom: 25px;
    backdrop-filter: blur(10px);
}

/* title */
.hero-title {
    font-size: 64px;
    font-weight: 800;
    line-height: 1.15;
    color: white;
}

/* sub */
.hero-sub {
    margin-top: 25px;
    font-size: 22px;
    color: #dbeafe;
    line-height: 1.8;
    max-width: 850px;
}

/* button */
.hero-button {
    margin-top: 35px;
    display: inline-block;
    background: #2563eb;
    padding: 16px 32px;
    border-radius: 16px;
    color: white;
    font-weight: 700;
    font-size: 18px;
    transition: 0.3s;
    cursor: pointer;
}

.hero-button:hover {
    transform: translateY(-3px);
    background: #3b82f6;
}

/* --- CARD --- */
.card {
    background:rgba(255,255,255,0.8);
    backdrop-filter:blur(10px);
    padding:35px;
    border-radius:28px;
    border:1px solid rgba(255,255,255,0.2);
    box-shadow: 0 8px 32px rgba(15,23,42,0.08);
    transition:0.35s;
    text-align: center;
}
.card:hover {
    transform:translateY(-8px);
    box-shadow: 0 15px 40px rgba(15,23,42,0.15);
}
.card h3 {
    color: #1e3a8a !important;
    margin-bottom: 10px;
}

/* --- KPI CARD --- */
.kpi-card {
    background: white;
    padding: 28px;
    border-radius: 24px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.06);
    transition: 0.3s;
}
.kpi-card:hover {
    transform: translateY(-5px);
}
.kpi-title {
    color: #64748b;
    font-size: 16px;
}
.kpi-value {
    margin-top: 10px;
    font-size: 38px;
    font-weight: 800;
    color: #0f172a;
}

/* ซ่อนแถบด้านบน (Header) สีขาวของ Streamlit */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* ซ่อนไอคอนลูกศรทุกรูปแบบใน st.expander ทั้ง Default Browser และของ Streamlit */
[data-testid="stExpander"] details summary {
    list-style: none !important;
}
[data-testid="stExpander"] details summary::-webkit-details-marker {
    display: none !important;
}
[data-testid="stExpander"] details summary svg,
[data-testid="stExpander"] details summary [data-testid="stIconMaterial"] {
    display: none !important;
}

/* --- RESPONSIVE MOBILE (ปรับขนาดให้พอดีบนโทรศัพท์มือถือ) --- */
@media (max-width: 768px) {
    .hero {
        padding: 30px 20px;
        text-align: center;
        justify-content: center;
        border-radius: 20px;
        min-height: auto;
    }
    .hero-title {
        font-size: 32px !important;
        line-height: 1.3;
    }
    .hero-sub {
        font-size: 16px !important;
        margin-top: 15px;
    }
    .hero-button {
        padding: 12px 24px;
        font-size: 16px;
    }
    .hero::before {
        display: none; /* ซ่อนแสงสะท้อนบนมือถือไม่ให้ล้นจอ */
    }
    .card {
        padding: 20px;
    }
}
</style>
""", unsafe_allow_html=True)


# --- Session State สำหรับจัดการระบบลิงก์ข้ามหน้า ---
menu_options = ["หน้าแรก", "วิเคราะห์ผู้ใช้ไฟ", "ค้นหาเป้าหมาย", "คำนวณโซลาร์", "บริการสินเชื่อ"]
if "active_page" not in st.session_state:
    st.session_state.active_page = "หน้าแรก"
if "menu_key" not in st.session_state:
    st.session_state.menu_key = 0

# ฟังก์ชันค้นหาไฟล์ภาพอัจฉริยะ (ค้นหาทุกโฟลเดอร์ ไม่สนตัวเล็ก/ใหญ่)
def get_image_path(file_name, default_folder=""):
    # อ้างอิงที่อยู่ของไฟล์โค้ดโดยตรง ป้องกันปัญหา Path คลาดเคลื่อนบน Cloud
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. ค้นหาตรงๆ ก่อนเพื่อความรวดเร็ว
    path1 = os.path.join(base_dir, file_name)
    if os.path.exists(path1): return path1
    path2 = os.path.join(base_dir, default_folder, file_name)
    if os.path.exists(path2): return path2
    
    # 2. ค้นหาแบบกวาดทุกโฟลเดอร์
    target = file_name.lower()
    for root, _, files in os.walk(base_dir):
        if ".git" in root or "__pycache__" in root: continue
        for f in files:
            if f.lower() == target:
                return os.path.join(root, f).replace("\\", "/")
                
    # 3. ถ้าหาไม่เจอจริงๆ ให้แสดงเป็นภาพ Placeholder แทน
    return "https://placehold.co/600x400.png?text=Image+Not+Found"

# ฟังก์ชันแปลงรูปภาพในเครื่องเป็น Base64 เพื่อให้แทรกลง HTML ได้
def get_base64_image(file_name, folder_name="Logo"):
    image_path = get_image_path(file_name, folder_name)
    if str(image_path).startswith("http"):
        return image_path
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()
            ext = image_path.split('.')[-1].lower()
            mime = 'jpeg' if ext == 'jpg' else ext
            return f"data:image/{mime};base64,{b64}"
    return ""

# --- เมนูนำทาง (Sidebar Navigation) ---
with st.sidebar:
    st.markdown(f"""
    <div class='logo-container'>
        <img src='{get_base64_image("Logo bannertwo.png", "Banner")}' class='logo-img'>
        <span class='logo-text'>SolarJoy Energy</span>
    </div>
    <br>
    """, unsafe_allow_html=True)

    current_index = menu_options.index(st.session_state.active_page)

    page_selection = option_menu(
        menu_title="เมนูหลัก",
        options=menu_options,
        icons=["house", "bar-chart", "geo-alt", "calculator", "bank"],
        menu_icon="list",
        default_index=current_index,
        key=f"main_menu_{st.session_state.menu_key}",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#0f172a",
            },

            "icon": {
                "color": "white",
                "font-size": "20px",
            },

            "menu-title": {
                "color":"white",
                "font-size":"22px",
                "font-weight":"700",
                "font-family": "system-ui, -apple-system, 'Leelawadee UI', 'Sukhumvit Set', sans-serif",
            },

            "nav-link": {

                "font-size": "18px",

                "text-align": "left",
                "font-family": "system-ui, -apple-system, 'Leelawadee UI', 'Sukhumvit Set', sans-serif",

                "margin":"6px 0",

                "padding":"14px 18px",

                "border-radius":"14px",

                "background-color":"#0f172a",

                "color":"white",

                "--hover-color": "#1e293b",
            },

            "nav-link-selected": {

                "background-color": "#2563eb",

                "color":"white",

                "font-weight":"700",
            },
        }
    )

    # ถ้ายูสเซอร์กดเปลี่ยนเมนูด้วยตัวเอง ให้ทำการอัปเดต State และรีเฟรชหน้า
    if page_selection != st.session_state.active_page:
        st.session_state.active_page = page_selection
        st.session_state.menu_key += 1
        st.rerun()

# Map ชื่อเมนูใหม่กลับไปยังตัวแปรเดิมเพื่อให้โค้ดด้านล่างทำงานได้โดยไม่ต้องแก้ If Conditions
page_map = {
    "หน้าแรก": "หน้าแรก (ข้อมูลบริการและแพ็กเกจ)",
    "วิเคราะห์ผู้ใช้ไฟ": "แดชบอร์ดวิเคราะห์",
    "ค้นหาเป้าหมาย": "ค้นหาลูกค้าเป้าหมาย",
    "คำนวณโซลาร์": "คำนวณโซล่าร์เซลล์ (ด้วยตัวเอง)",
    "บริการสินเชื่อ": "บริการด้านสินเชื่อ"
}
page = page_map[st.session_state.active_page]

st.divider()

# ==========================================
# ส่วนที่ 5: หน้าบริการด้านสินเชื่อ
# ==========================================
if page == "บริการด้านสินเชื่อ":
    st.title("บริการด้านสินเชื่อสำหรับติดตั้งโซล่าร์เซลล์")
    st.markdown("*(ข้อมูลผลิตภัณฑ์สินเชื่อโครงการ PEA SOLAR จากสถาบันการเงินพันธมิตร เพื่อสนับสนุนการเข้าถึงพลังงานสะอาด)*")
    
    st.image("https://images.unsplash.com/photo-1613665813446-82a78c468a1d?q=80&w=1200&h=400&auto=format&fit=crop", use_container_width=True)
    
    st.markdown("""
    การไฟฟ้าส่วนภูมิภาค (PEA) ได้ร่วมมือกับ **6 สถาบันการเงินชั้นนำของประเทศ** เพื่อให้บริการด้านสินเชื่อสำหรับการติดตั้งระบบผลิตไฟฟ้าจากพลังงานแสงอาทิตย์บนหลังคา (Solar Rooftop) 
    ช่วยลดภาระการลงทุนก้อนแรก ทำให้คุณเป็นเจ้าของระบบโซล่าร์เซลล์ได้ง่ายขึ้น ด้วยอัตราดอกเบี้ยพิเศษและระยะเวลาผ่อนชำระที่ยาวนาน คุ้มค่ากับเงินที่ประหยัดได้จากค่าไฟในแต่ละเดือน
    """)
    st.divider()

    # แบ่งเป็น 2 แท็บ: สำหรับบ้านพักอาศัย และ สำหรับภาคธุรกิจ
    tab1, tab2 = st.tabs(["สินเชื่อสำหรับบ้านพักอาศัย", "สินเชื่อสำหรับภาคธุรกิจ (SME & Corporate)"])
    
    with tab1:
        st.subheader("สินเชื่อติดตั้งโซล่าร์เซลล์ สำหรับบ้านพักอาศัย")
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #16a34a; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('กสิกร.png')}' height='30'> ธนาคารกสิกรไทย</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อบ้านเพื่อติดตั้งโซลาร์รูฟท็อป**")
                st.markdown("- **วงเงินกู้สูงสุด:** 100% ของค่าติดตั้ง")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 30 ปี")
                st.markdown("- **จุดเด่น:** รับดอกเบี้ยพิเศษ 0% นาน 3 เดือน พร้อมสิทธิพิเศษ ฟรีค่าสำรวจออกแบบ ฟรีค่าเชื่อมต่อระบบ และฟรีล้างแผงโซลาร์ 2 ปี")
                st.link_button("ดูรายละเอียดบนเว็บไซต์", "https://www.kasikornbank.com/th/personal/loan/home-loan/pages/solar-rooftop.aspx", use_container_width=True)
        with c2:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #0284c7; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('กรุงเทพ.jpg')}' height='30'> ธนาคารกรุงเทพ</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อบัวหลวงพูนผลกรีน**")
                st.markdown("- **วงเงินกู้สูงสุด:** 10 ล้านบาท")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 30 ปี")
                st.markdown("- **จุดเด่น:** อัตราดอกเบี้ยพิเศษตลอดอายุสัญญา (ประมาณ 5.78% - 6.13% ต่อปี) เพื่อปรับปรุงบ้านและประหยัดพลังงาน")
                st.link_button("ดูรายละเอียดบนเว็บไซต์", "https://www.bangkokbank.com/th-TH/Personal/My-Home/Bualuang-Poonpol-Green-Loan", use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #0f172a; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('uob.png')}' height='25'> ธนาคารยูโอบี</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อบ้านรักษ์โลก U-Green**")
                st.markdown("- **วงเงินกู้สูงสุด:** 50 ล้านบาท")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 30 ปี")
                st.markdown("- **จุดเด่น:** สินเชื่อบ้านแลกเงิน (Green Cash to Home) หรือรีไฟแนนซ์ (Green Top Up) ดอกเบี้ยเฉลี่ย 3 ปีแรกเริ่มต้น 3.49%")
                st.link_button("ดูรายละเอียดบนเว็บไซต์", "https://www.uob.co.th/personal/loans/home-loan/u-green.page", use_container_width=True)
        with c4:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #db2777; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('ออมสิน.jpg')}' height='30'> ธนาคารออมสิน</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อ GSB Green Home Loan**")
                st.markdown("- **วงเงินกู้สูงสุด:** 110% (รวมซื้อบ้าน/ตกแต่ง)")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 40 ปี")
                st.markdown("- **จุดเด่น:** สนับสนุนสินเชื่อดอกเบี้ยต่ำเพื่อที่อยู่อาศัยประหยัดพลังงาน เป็นมิตรกับสิ่งแวดล้อม")
                st.link_button("ดูรายละเอียดบนเว็บไซต์", "https://www.gsb.or.th/promotions/gsb-green-home-loan/", use_container_width=True)

    with tab2:
        st.subheader("สินเชื่อติดตั้งโซล่าร์เซลล์ สำหรับภาคธุรกิจและ SME")
        b1, b2 = st.columns(2)
        with b1:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #16a34a; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('กสิกร.png')}' height='30'> ธนาคารกสิกรไทย</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อติดตั้งโซลาร์รูฟท็อปสำหรับธุรกิจ**")
                st.markdown("- **วงเงินกู้สูงสุด:** 100% (หรือสูงสุด 3 ล้านบาท สำหรับ SME ขนาดเล็ก)")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 8 ปี")
                st.markdown("- **จุดเด่น:** ไม่ต้องผ่อนเงินต้นและดอกเบี้ย 6 เดือนแรก อัตราดอกเบี้ยเริ่มต้น 1.99% ต่อปี ใน 2 ปีแรก")
                st.link_button("ดูรายละเอียดบนเว็บไซต์", "https://www.kasikornbank.com/th/business/sme/loan/solar-rooftop/pages/index.aspx", use_container_width=True)
        with b2:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #ea580c; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('ttb.png')}' height='25'> ทีเอ็มบีธนชาต (ttb)</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อธุรกิจเพื่อสิ่งแวดล้อม**")
                st.markdown("- **วงเงินกู้สูงสุด:** 100% ของมูลค่าการติดตั้ง")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 8 ปี")
                st.markdown("- **จุดเด่น:** สนับสนุนผู้ประกอบการมุ่งสู่เศรษฐกิจคาร์บอนต่ำ ช่วยประหยัดต้นทุนค่าไฟอย่างยั่งยืน")
                st.link_button("ดูรายละเอียดบนเว็บไซต์", "https://www.ttbbank.com/th/sme/sme-loan/business-loan/sme-green-loan", use_container_width=True)

        b3, b4 = st.columns(2)
        with b3:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #ca8a04; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('sme.png')}' height='30'> SME D Bank</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อ SME Green Productivity**")
                st.markdown("- **วงเงินกู้สูงสุด:** 10 ล้านบาท")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 10 ปี")
                st.markdown("- **จุดเด่น:** อัตราดอกเบี้ยต่ำเพียง 3% ต่อปี คงที่ 3 ปีแรก เพื่อยกระดับและเพิ่มผลิตภาพธุรกิจสีเขียว")
                st.link_button("ดูรายละเอียดบนเว็บไซต์", "https://www.smebank.co.th/products/sme-green-productivity/", use_container_width=True)
        with b4:
            with st.container(border=True):
                st.markdown("### สนใจขอรับบริการสินเชื่อ")
                st.markdown("ลูกค้าที่สนใจสามารถแจ้งความประสงค์ผ่านสำนักงานการไฟฟ้าส่วนภูมิภาค (PEA) ที่ดูแลโครงการ หรือติดต่อสาขาของธนาคารพันธมิตรทั่วประเทศ")
                st.info("เงื่อนไขการอนุมัติสินเชื่อ วงเงิน และอัตราดอกเบี้ย เป็นไปตามที่แต่ละธนาคารกำหนด")
                st.link_button("ดูข้อมูลโครงการ PEA SOLAR หน้าหลัก", "https://peasolar.pea.co.th/", use_container_width=True)

    st.divider()
    
    # เพิ่มเครื่องคำนวณยอดผ่อนชำระเบื้องต้น
    st.subheader("เครื่องคำนวณยอดผ่อนชำระสินเชื่อเบื้องต้น")
    st.markdown("*(ประเมินค่างวดรายเดือนแบบลดต้นลดดอก (Effective Rate) เพื่อเปรียบเทียบกับค่าไฟที่ประหยัดได้)*")
    
    calc_col1, calc_col2 = st.columns([1, 1])
    with calc_col1:
        with st.container(border=True):
            loan_amount = st.number_input("วงเงินที่ต้องการกู้ (ราคาแพ็กเกจ)", min_value=10000, max_value=5000000, value=200000, step=10000)
            interest_rate = st.number_input("อัตราดอกเบี้ยเฉลี่ย (% ต่อปี)", min_value=0.0, max_value=20.0, value=5.5, step=0.1)
            loan_years = st.number_input("ระยะเวลาผ่อนชำระ (ปี)", min_value=1, max_value=40, value=7, step=1)
            
    with calc_col2:
        with st.container(border=True):
            if interest_rate > 0:
                # คำนวณแบบลดต้นลดดอก
                monthly_rate = (interest_rate / 100) / 12
                total_months = loan_years * 12
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**total_months) / ((1 + monthly_rate)**total_months - 1)
                total_payment = monthly_payment * total_months
                total_interest = total_payment - loan_amount
            else:
                total_months = loan_years * 12
                monthly_payment = loan_amount / total_months
                total_payment = loan_amount
                total_interest = 0
                
            st.markdown("<div style='text-align: center; color: #64748B;'>ยอดผ่อนชำระต่อเดือนประมาณ</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 2.5rem; font-weight: bold; color: #0284C7; margin-bottom: 10px;'>฿ {monthly_payment:,.2f}</div>", unsafe_allow_html=True)
            st.divider()
            st.markdown(f"- ยอดเงินต้น: **฿ {loan_amount:,.0f}**")
            st.markdown(f"- ดอกเบี้ยรวมตลอดสัญญา: **฿ {total_interest:,.0f}**")
            st.markdown(f"- ยอดชำระรวมทั้งหมด: **฿ {total_payment:,.0f}**")
            
            st.info("**คำแนะนำ:** นำ 'ยอดผ่อนชำระนี้' ไปเทียบกับ 'ค่าไฟที่ประหยัดได้' หากยอดผ่อนน้อยกว่าค่าไฟที่ลดได้ แสดงว่าคุณได้กำไรตั้งแต่เดือนแรกที่ติดตั้ง!")
    
    st.stop() # บล็อกโค้ดตรงนี้เด็ดขาด ไม่ให้โค้ดส่วนค้นหาเป้าหมายหรือแผนที่ข้างล่างทำงานได้
# ==========================================
# ส่วนที่ 4: หน้าคำนวณโซล่าร์เซลล์จากเครื่องใช้ไฟฟ้า (แยกออกมาให้ทำงานอิสระได้)
# ==========================================
if page == "คำนวณโซล่าร์เซลล์ (ด้วยตัวเอง)":
    st.title("คำนวณขนาดโซล่าร์เซลล์ที่เหมาะสม")
    st.markdown("*(ประเมินขนาดแผงโซล่าร์เซลล์ On-Grid เพื่อช่วยลดค่าไฟในช่วงเวลากลางวันอย่างคุ้มค่า)*")
    
    st.markdown("### วิธีที่ 1: ประเมินแบบด่วนจากบิลค่าไฟ")
    st.info("นำตัวเลข **'หน่วยการใช้ไฟฟ้ารวม (kWh)'** จากบิลค่าไฟเดือนล่าสุดของคุณมากรอก (หากระบุค่าในช่องนี้ ระบบจะใช้ค่านี้คำนวณเป็นหลักทันที)")
    
    c1, c2 = st.columns(2)
    with c1:
        manual_monthly_kwh = st.number_input("ระบุหน่วยการใช้ไฟรวมต่อเดือน (kWh)", min_value=0.0, value=0.0, step=100.0)
    with c2:
        day_ratio_pct = st.number_input("สัดส่วนการใช้ไฟกลางวัน (%)", min_value=0, max_value=100, value=50, step=5, help="ระบุเปอร์เซ็นต์การใช้ไฟในช่วง 08:00 - 17:00 น. (ตัวอย่างเช่น บ้านทั่วไป 40-50%, โฮมออฟฟิศ 60-70%)")
        
    day_ratio = day_ratio_pct / 100.0
    total_daily_kwh_manual = (manual_monthly_kwh / 30.0) * day_ratio if manual_monthly_kwh > 0 else 0.0
    
    st.markdown("---")
    st.markdown("### วิธีที่ 2: ประเมินแบบละเอียดจากเครื่องใช้ไฟฟ้า")
    st.info("**คำแนะนำ:** กรุณากรอกเฉพาะชั่วโมงการใช้งานในช่วงที่ **มีแสงแดด (ประมาณ 08:00 - 17:00 น.)** เท่านั้น เนื่องจากระบบไม่มีแบตเตอรี่สำรองไฟ")
    
    # รายการเครื่องใช้ไฟฟ้าเริ่มต้น
    initial_appliances = [
        {"name": "แอร์ 9,000 BTU", "watts": 800, "qty": 0, "hrs": 0.0},
        {"name": "แอร์ 12,000 BTU", "watts": 1000, "qty": 0, "hrs": 0.0},
        {"name": "แอร์ 18,000 BTU", "watts": 1500, "qty": 0, "hrs": 0.0},
        {"name": "ตู้เย็น (ทำงานตลอดวัน)", "watts": 150, "qty": 1, "hrs": 8.0},
        {"name": "ทีวี", "watts": 100, "qty": 0, "hrs": 0.0},
        {"name": "คอมพิวเตอร์ / โน้ตบุ๊ก", "watts": 200, "qty": 0, "hrs": 0.0},
        {"name": "หลอดไฟ", "watts": 15, "qty": 0, "hrs": 0.0},
        {"name": "พัดลม", "watts": 50, "qty": 0, "hrs": 0.0},
        {"name": "เครื่องซักผ้า", "watts": 400, "qty": 0, "hrs": 0.0},
        {"name": "ปั๊มน้ำ", "watts": 300, "qty": 0, "hrs": 0.0},
        {"name": "อื่นๆ", "watts": 100, "qty": 0, "hrs": 0.0},
    ]
    if "calc_appliances" not in st.session_state:
        st.session_state.calc_appliances = initial_appliances
    
    other_appliances_options = {
        "อื่นๆ (ระบุกำลังไฟเอง)": 100,
        "ไมโครเวฟ": 800,
        "กาต้มน้ำร้อน": 1500,
        "หม้อหุงข้าว": 600,
        "เตาแม่เหล็กไฟฟ้า": 1500,
        "เครื่องทำน้ำอุ่น": 3500,
        "ไดร์เป่าผม": 1200,
        "เตารีด": 1000,
        "เครื่องดูดฝุ่น": 1200,
        "เครื่องฟอกอากาศ": 400,
        "เตาอบไฟฟ้า": 2000,
        "ปั๊มลม": 1500
    }
    
    total_daily_wh = 0
    
    # หัวตาราง
    cols = st.columns([3, 2, 2, 2])
    cols[0].write("**เครื่องใช้ไฟฟ้า**")
    cols[1].write("**กำลังไฟ (วัตต์)**")
    cols[2].write("**จำนวน (เครื่อง)**")
    cols[3].write("**ใช้งานกลางวัน (ชม.)**")
    st.markdown("<hr style='margin-top: 0; margin-bottom: 10px;'>", unsafe_allow_html=True)
    
    # แถวรับข้อมูล
    for i, app in enumerate(st.session_state.calc_appliances):
        row = st.columns([3, 2, 2, 2])
        
        if "อื่นๆ" in app['name']:
            selected_other = row[0].selectbox(f"app_select_{i}", options=list(other_appliances_options.keys()), label_visibility="collapsed")
            if selected_other == "อื่นๆ (ระบุกำลังไฟเอง)":
                custom_w = row[1].number_input(f"w_{i}", min_value=0, max_value=10000, value=int(app.get('watts', 100)), step=100, label_visibility="collapsed")
                app['watts'] = custom_w
            else:
                row[1].markdown(f"<div style='padding-top: 10px; color: #6b7280;'>~ {other_appliances_options[selected_other]} W</div>", unsafe_allow_html=True)
                app['watts'] = other_appliances_options[selected_other]
        else:
            row[0].markdown(f"<div style='padding-top: 10px;'>{app['name']}</div>", unsafe_allow_html=True)
            row[1].markdown(f"<div style='padding-top: 10px; color: #6b7280;'>~ {app['watts']} W</div>", unsafe_allow_html=True)
            
        qty = row[2].number_input(f"qty_{i}", min_value=0, max_value=100, value=int(app.get('qty', 0)), label_visibility="collapsed")
        hrs = row[3].number_input(f"hrs_{i}", min_value=0.0, max_value=12.0, value=float(app.get('hrs', 0.0)), step=0.5, label_visibility="collapsed")
        
        app['qty'] = qty
        app['hrs'] = hrs
        
        total_daily_wh += (app['watts'] * qty * hrs)
        
    # --- ปุ่มเพิ่ม/ลบ เครื่องใช้ไฟฟ้า ---
    st.markdown("<br>", unsafe_allow_html=True) # เพิ่มช่องว่างด้านบนปุ่ม
    add_col1, add_col2, add_col3 = st.columns([2, 2, 2])
    with add_col1: # ปุ่มเพิ่ม
        if st.button("เพิ่มรายการ 'อื่นๆ'", use_container_width=True):
            st.session_state.calc_appliances.append({"name": "อื่นๆ", "watts": 100, "qty": 0, "hrs": 0.0})
            st.rerun()
    with add_col2: # ปุ่มล้างข้อมูลทั้งหมด
        if st.button("ล้างข้อมูลทั้งหมด", use_container_width=True, help="รีเซ็ตจำนวนและชั่วโมงการใช้งานทั้งหมดเป็น 0 รวมถึงลบแถว 'อื่นๆ' ที่เพิ่มมา"):
            # สร้างรายการเริ่มต้นใหม่ โดยตั้งค่า qty เป็น 0 (จำนวนเต็ม) และ hrs เป็น 0.0 (ทศนิยม)
            st.session_state.calc_appliances = [
                {**app, 'qty': 0, 'hrs': 0.0} for app in initial_appliances
            ]
            st.rerun()
    with add_col3: # ปุ่มลบรายการล่าสุด
        if len(st.session_state.calc_appliances) > 11:
            if st.button("ลบรายการล่าสุด", use_container_width=True):
                st.session_state.calc_appliances.pop()
                st.rerun()
                
    total_daily_kwh_table = total_daily_wh / 1000
    
    # เลือกใช้ค่าจากการกรอกบิลไฟเป็นหลัก หากไม่กรอกถึงจะใช้ค่าจากตารางเครื่องใช้ไฟฟ้า
    total_daily_kwh = total_daily_kwh_manual if manual_monthly_kwh > 0 else total_daily_kwh_table
    
    st.divider()
    st.subheader("ผลการประเมินและขนาดที่แนะนำ")
    
    # 1 kW แผงโซล่าร์เซลล์ ผลิตไฟได้ประมาณ 4 หน่วย (kWh) ต่อวัน
    recommended_kw = total_daily_kwh / 4.0
    
    if recommended_kw > 0:
        def rec_pkg(kw):
            if kw <= 3: return "3 kW", 145000
            elif kw <= 5: return "5 kW", 200000
            elif kw <= 10: return "10 kW", 329000
            elif kw <= 15: return "15 kW", 454900
            else: return ">15 kW", max(550000, kw * 27500)
        
        pkg_name, pkg_price = rec_pkg(recommended_kw)
        
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            with st.container(border=True):
                st.metric("การใช้ไฟกลางวันรวม", f"{total_daily_kwh:,.1f} หน่วย/วัน")
        with rc2:
            with st.container(border=True):
                st.metric("ขนาดติดตั้งขั้นต่ำที่ต้องการ", f"{recommended_kw:,.2f} kW")
        with rc3:
            with st.container(border=True):
                st.metric("แพ็กเกจที่ครอบคลุม", f"{pkg_name}")
        
        st.success(f"จากพฤติกรรมการใช้งานของคุณ ขอแนะนำให้พิจารณา **แพ็กเกจ {pkg_name}** (ราคาประเมิน ฿ {pkg_price:,.0f})")
        
        st.info('''
        **หลักการคำนวณเบื้องต้น:**
        - **สูตรคำนวณ:** `หน่วยไฟรวม (kWh) ÷ 4 ชั่วโมง (แสงแดดเฉลี่ย/วัน)`
        - ในประเทศไทย แผงโซล่าร์เซลล์ขนาด 1 kW สามารถผลิตกระแสไฟฟ้าได้เฉลี่ยวันละ 4 หน่วย (ครอบคลุม Loss แล้ว)
        - ตัวเลขนี้เป็นเพียงการประเมินเบื้องต้นสำหรับการติดระบบ On-Grid เพื่อลดค่าไฟกลางวันเท่านั้น
        ''')
    else:
        st.warning("กรุณาระบุจำนวนเครื่องใช้ไฟฟ้าและชั่วโมงการเปิดใช้งาน เพื่อเริ่มต้นการคำนวณ")
        
    st.stop() # บล็อกโค้ดตรงนี้เด็ดขาด ไม่ให้โค้ดส่วนค้นหาเป้าหมายหรือแผนที่ข้างล่างทำงานได้

# โหลดและเตรียมข้อมูล (ใช้ Cache เพื่อไม่ให้ต้องโหลดไฟล์ใหม่ทุกครั้งที่ขยับเมาส์)
@st.cache_data
def load_data():
    # ดึงฟังก์ชันอ่านไฟล์จาก read_all_csv.py ที่เราเขียนไว้
    raw_data = read_all_csv_in_directory(".", combine=True)
    if isinstance(raw_data, pd.DataFrame):
        return process_pea_data(raw_data)
    return None

df = load_data()

if df is not None:
    
    # ==========================================
    # ส่วนที่ 1: หน้าแรก (Home Page)
    # ==========================================
    if page == "หน้าแรก (ข้อมูลบริการและแพ็กเกจ)":
        
        # ---------------- HERO BANNER ----------------
        st.markdown("""
        <div class="hero">
        
        <div class="hero-left">
        
        <div class="hero-badge">SOLAR ANALYTICS</div>
        
        <div class="hero-title">
        ระบบวิเคราะห์ผู้ใช้ไฟ
        <br>
        เพื่อแนะนำการติดตั้งโซลาร์เซลล์
        </div>
        
        <div class="hero-sub">
        วิเคราะห์พฤติกรรมการใช้ไฟฟ้าแบบอัจฉริยะ
        แนะนำขนาดระบบที่เหมาะสม พร้อมคำนวณ ROI
        และระยะเวลาคืนทุนอัตโนมัติ
        </div>
        
        </div>
        
        </div>
        """, unsafe_allow_html=True)

        if st.button("เริ่มคำนวณโซลาร์ →", type="primary"):
            st.session_state.active_page = "คำนวณโซลาร์"
            st.session_state.menu_key += 1
            st.rerun()

        st.write("")
        
        # ---------------- ABOUT US ----------------
        st.markdown("## รู้จักกับเรา (About Us)")
        ab1, ab2 = st.columns([3, 2])
        with ab1:
            st.markdown("""
            <div style="background-color: #f8fafc; padding: 30px; border-radius: 16px; border-left: 6px solid #2563eb; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <p style="font-size: 18px; color: #334155; margin: 0; line-height: 1.6;">
                    เราคือผู้ให้บริการออกแบบและติดตั้งระบบผลิตไฟฟ้าจากพลังงานแสงอาทิตย์ (Solar Rooftop) แบบครบวงจร 
                    ที่นำเทคโนโลยี <b>AI Analytics</b> มาใช้ในการประเมินพฤติกรรมการใช้ไฟฟ้าของคุณ เพื่อให้ได้ขนาดระบบที่เหมาะสมที่สุด 
                    มุ่งเน้นความคุ้มค่าในการลงทุน ความปลอดภัย และการดูแลระยะยาว เพื่อช่วยให้คุณประหยัดค่าไฟและก้าวสู่การใช้พลังงานสะอาดอย่างยั่งยืน
                </p>
            </div>
            """, unsafe_allow_html=True)
        with ab2:
            st.image("https://images.unsplash.com/photo-1592833159155-c62df1b65634?q=80&w=800&h=480&auto=format&fit=crop", use_container_width=True)

        # ---------------- WHY CHOOSE US ----------------
        st.markdown("## ทำไมต้องติดตั้งโซล่าร์เซลล์กับเรา?")
        w1, w2, w3, w4 = st.columns(4)
        with w1:
            st.markdown("""
            <div class="card" style="padding: 20px;">
                <h4 style="color: #1e3a8a; margin-top: 10px;">วิศวกรเชี่ยวชาญ</h4>
                <p style="font-size: 14px; color: #64748b;">ออกแบบและติดตั้งโดยทีมวิศวกรไฟฟ้าที่มีใบอนุญาต ถูกต้องตามมาตรฐาน</p>
            </div>
            """, unsafe_allow_html=True)
        with w2:
            st.markdown("""
            <div class="card" style="padding: 20px;">
                <h4 style="color: #1e3a8a; margin-top: 10px;">รับประกันยาวนาน</h4>
                <p style="font-size: 14px; color: #64748b;">รับประกันแผง 25 ปี อินเวอร์เตอร์ 10 ปี และดูแลงานติดตั้งสูงสุด 2 ปี</p>
            </div>
            """, unsafe_allow_html=True)
        with w3:
            st.markdown("""
            <div class="card" style="padding: 20px;">
                <h4 style="color: #1e3a8a; margin-top: 10px;">วิเคราะห์ด้วย AI</h4>
                <p style="font-size: 14px; color: #64748b;">ระบบประเมินจุดคุ้มทุนและเสนอแพ็กเกจที่แม่นยำจากบิลค่าไฟจริงของคุณ</p>
            </div>
            """, unsafe_allow_html=True)
        with w4:
            st.markdown("""
            <div class="card" style="padding: 20px;">
                <h4 style="color: #1e3a8a; margin-top: 10px;">รองรับสินเชื่อ</h4>
                <p style="font-size: 14px; color: #64748b;">เป็นพันธมิตรกับธนาคารชั้นนำ ช่วยยื่นกู้และพร้อมเสนออัตราดอกเบี้ยพิเศษ</p>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.write("")

        # ---------------- SERVICES ----------------
        st.markdown("## บริการที่คุณจะได้รับ (One-Stop Service)")
        s1, s2 = st.columns(2)
        with s1:
            st.info("**บริการสำรวจและออกแบบฟรี**\n\nลงพื้นที่สำรวจหน้างาน ประเมินโครงสร้างหลังคา และใช้โปรแกรมจำลองทิศทางรับแสงที่ดีที่สุด")
            st.info("**อุปกรณ์ระดับ Tier 1**\n\nเลือกใช้แผงโซล่าร์เซลล์และอินเวอร์เตอร์คุณภาพสูงระดับโลก ที่ได้รับการยอมรับด้านความปลอดภัย")
        with s2:
            st.info("**ดำเนินการขออนุญาตฟรีทุกขั้นตอน**\n\nจัดการเอกสารกับ กฟภ./กฟน. และหน่วยงานราชการที่เกี่ยวข้องให้ทั้งหมดจนกว่าจะขนานไฟสำเร็จ")
            st.info("**บริการหลังการขายแบบมืออาชีพ**\n\nมีบริการล้างแผง ตรวจเช็คระบบไฟฟ้าประจำปี และตรวจสอบการทำงานผ่านแอปพลิเคชันออนไลน์ 24 ชม.")

        st.write("")
        st.divider()
        
        st.image("https://images.unsplash.com/photo-1497440001374-f26997328c1b?q=80&w=1200&h=300&auto=format&fit=crop&v=new", use_container_width=True)
        st.subheader("แพ็กเกจการติดตั้งมาตรฐาน (ราคาโดยประมาณ)")
        
        # ฟังก์ชันสำหรับเปิดหน้าต่าง Modal/Dialog แสดงรายละเอียดแพ็กเกจแบบกว้าง
        @st.dialog("รายละเอียดแพ็กเกจการติดตั้ง", width="large")
        def show_details(pkg_name, size, price, details, models=None, panel_models=None):
            st.markdown(f"## {pkg_name} ({size})")
            st.subheader(f"ราคาเริ่มต้นประมาณ: {price}")
            st.divider()
            st.markdown("### อุปกรณ์และบริการที่รวมในแพ็กเกจ:")
            st.markdown(details)
            
            # --- ส่วนแสดงรูปภาพแผงโซล่าร์เซลล์ ---
            if panel_models:
                st.divider()
                st.markdown("### เลือกรุ่นแผงโซล่าร์เซลล์ Tier 1:")
                st.info("**เกร็ดความรู้เรื่องราคา:** แผงโซล่าร์เซลล์ระดับ Tier 1 (เช่น Jinko, LONGi) จะมีต้นทุนมาตรฐานใกล้เคียงกัน บริษัทส่วนใหญ่จึงเปิดให้ลูกค้า **สามารถเลือกแบรนด์แผงโซล่าร์เซลล์ได้อิสระ โดยไม่ทำให้ราคาแพ็กเกจเปลี่ยนแปลง** (ราคาแพ็กเกจแบบครบชุด จะถูกกำหนดความถูก-แพง จาก 'แบรนด์อินเวอร์เตอร์' ที่ลูกค้าเลือกด้านล่างครับ)")
                p_cols = st.columns(len(panel_models))
                for i, p_model in enumerate(panel_models):
                    with p_cols[i]:
                        with st.container(border=True):
                            if 'image' in p_model:
                                if str(p_model['image']).startswith("http") or os.path.exists(p_model['image']):
                                    img_cols = st.columns([1, 5, 1]) # สร้างคอลัมน์ซ้อนเพื่อบีบขนาดรูป
                                    with img_cols[1]:
                                        st.image(p_model['image'], use_container_width=True)
                                else:
                                    st.warning(f"ไม่พบรูปภาพ: {p_model['image']}")
                            st.markdown(f"""
                            <div style="background-color: #F3F4F6; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; border: 2px dashed #D8B4FE;">
                                <div style="font-size: 16px; font-weight: bold; color: #4C1D95;">{p_model['name']}</div>
                                <div style="color: #6B7280; font-size: 12px; margin-top: 5px;">แผงคุณภาพสูง (Tier 1)</div>
                                <div style="font-size: 14px; color: #7C3AED; font-weight: bold; margin-top: 10px; padding: 5px; background-color: #F3E8FF; border-radius: 8px;">รวมอยู่ในราคาแพ็กเกจแล้ว</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # เพิ่มคำอธิบายจุดเด่นของแผงแต่ละยี่ห้อ
                            if 'description' in p_model:
                                st.markdown(f"<p style='font-size: 13px; color: #4a5568; text-align: left; min-height: 100px; border-left: 3px solid #c084fc; padding-left: 10px;'>{p_model['description']}</p>", unsafe_allow_html=True)

                            if st.button(f"เลือกแผง {p_model['name']}", key=f"select_panel_{pkg_name}_{i}", use_container_width=True):
                                st.success(f"คุณสนใจแผงโซล่าร์เซลล์รุ่น {p_model['name']} (รวมอยู่ในราคาแพ็กเกจด้านล่างแล้ว ไม่มีบวกเพิ่ม)")

            # --- ส่วนแสดงรูปภาพอินเวอร์เตอร์ / มิตเตอร์แต่ละรุ่น ---
            if models:
                st.divider()
                st.markdown("### เลือกแบรนด์อินเวอร์เตอร์ (ราคานี้รวมแผงโซลาร์เซลล์ อินเวอร์เตอร์ สมาร์ทมิเตอร์ และอุปกรณ์ติดตั้งครบชุดแล้ว):")
                cols = st.columns(len(models))
                for i, model in enumerate(models):
                    with cols[i]:
                        with st.container(border=True):
                            if 'image' in model:
                                if str(model['image']).startswith("http") or os.path.exists(model['image']):
                                    img_cols = st.columns([1, 5, 1]) # สร้างคอลัมน์ซ้อนเพื่อบีบขนาดรูป
                                    with img_cols[1]:
                                        st.image(model['image'], use_container_width=True)
                                else:
                                    st.warning(f"ไม่พบรูปภาพ: {model['image']}")
                            st.markdown(f"""
                                <div style="background-color: #F8FAFC; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; border: 2px dashed #93C5FD;">
                                    <div style="font-size: 16px; font-weight: bold; color: #0369A1;">เซ็ตอุปกรณ์ {model['name']}</div>
                                    <div style="font-size: 14px; color: #0284C7; font-weight: bold; margin-top: 10px; padding: 5px; background-color: #E0F2FE; border-radius: 8px;">ราคารวมทั้งแพ็กเกจ: {model['price']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                            # เพิ่มคำอธิบายจุดเด่นของอินเวอร์เตอร์แต่ละยี่ห้อ
                            if 'description' in model:
                                st.markdown(f"<p style='font-size: 13px; color: #4a5568; text-align: left; min-height: 120px; border-left: 3px solid #60a5fa; padding-left: 10px;'>{model['description']}</p>", unsafe_allow_html=True)

                            if st.button(f"สนใจแพ็กเกจ {model['name']}", key=f"select_{pkg_name}_{i}", use_container_width=True):
                                st.success(f"คุณสนใจแพ็กเกจแบบครบชุด เซ็ต {model['name']} ในราคารวม {model['price']}")

            st.divider()
            st.info("หมายเหตุ: ราคาอาจมีการเปลี่ยนแปลงขึ้นอยู่กับการประเมินหน้างาน โครงสร้างหลังคา และรุ่นอุปกรณ์ที่เลือก")

        # รายชื่อแผงโซล่าร์เซลล์มาตรฐาน (Tier 1) ที่ใช้กับทุกแพ็กเกจ
        panel_models_std = [ 
            {"name": "Jinko Tiger Pro 550W", "image": get_image_path("Jiinko_550w.jpg", "package3kW"), "description": "แบรนด์ยอดขายอันดับ 1 ของโลก มีชื่อเสียงด้านเทคโนโลยี N-Type TOPCon ที่ให้ประสิทธิภาพสูงและทนทานต่อสภาพอากาศร้อนได้ดีเยี่ยม"},
            {"name": "LONGI Hi-MO 5 550W", "image": get_image_path("Longi550w.png", "package3kW"), "description": "ผู้ผลิตแผงโซล่าเซลล์รายใหญ่ที่สุดของโลก โดดเด่นด้านนวัตกรรมเซลล์แสงอาทิตย์แบบ Mono-crystalline ที่ให้กำลังการผลิตสูงและเสถียร"}
        ]

        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #FFD6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">3 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("เหมาะสำหรับ: บ้านพักอาศัยขนาดเล็ก\n\nราคารวมติดตั้งเริ่มต้น: **135,000 บาท**\n\n*(ราคารวมแผง, อินเวอร์เตอร์ และอุปกรณ์ครบชุด)*")
                if st.button("ดูรายละเอียด", key="btn_s", use_container_width=True):
                    models_s = [
                        {"name": "Huawei SUN2000-3KTL-L1", "price": "145,000 บาท", "image": get_image_path("SUN2000-3KTL-L1..webp", "package3kW"), "description": "แบรนด์ชั้นนำระดับโลก โดดเด่นด้านเทคโนโลยี AI, ระบบป้องกันฟ้าผ่า, และฟีเจอร์ AFCI ป้องกันไฟไหม้ มาพร้อมแอปพลิเคชัน FusionSolar ที่เสถียรและใช้งานง่าย"},
                        {"name": "Growatt MIN 3000TL-X", "price": "135,000 บาท", "image": get_image_path("Growatt-MIN-3000-TL-X.webp", "package3kW"), "description": "แบรนด์ยอดนิยมในไทยและทั่วโลก มีจุดเด่นที่ราคาคุ้มค่า ประสิทธิภาพสูง และมีศูนย์บริการในประเทศไทยที่ดูแลและให้บริการหลังการขายได้รวดเร็ว"}
                    ]
                    show_details("แพ็กเกจ", "3 kW", "135,000 - 145,000 บาท", "- แผงโซล่าร์เซลล์ (550W) จำนวน 5-6 แผง\n- อินเวอร์เตอร์ 1 เฟส จำนวน 1 ตัว พร้อมสมาร์ทมิเตอร์\n- ฟรี! ค่าดำเนินการขออนุญาตขนานไฟกับการไฟฟ้า\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี\n- รับประกันงานติดตั้ง 1 ปี", models=models_s, panel_models=panel_models_std)
        with col2:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #E7C6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">5 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("เหมาะสำหรับ: บ้านพักอาศัยขนาดกลาง-ใหญ่\n\nราคารวมติดตั้งเริ่มต้น: **189,000 บาท**\n\n*(ราคารวมแผง, อินเวอร์เตอร์ และอุปกรณ์ครบชุด)*")
                if st.button("ดูรายละเอียด", key="btn_m", use_container_width=True):
                    models_m = [
                        {"name": "Huawei SUN2000-5KTL-L1", "price": "200,000 บาท", "image": get_image_path("SUN2000-5KTL-L1-01.webp", "package3kW"), "description": "แบรนด์ชั้นนำระดับโลก โดดเด่นด้านเทคโนโลยี AI, ระบบป้องกันฟ้าผ่า, และฟีเจอร์ AFCI ป้องกันไฟไหม้ มาพร้อมแอปพลิเคชัน FusionSolar ที่เสถียรและใช้งานง่าย"},
                        {"name": "Growatt MIN 5000TL-X", "price": "189,000 บาท", "image": get_image_path("growatt-min-5000tl-x.jpg", "package3kW"), "description": "แบรนด์ยอดนิยมในไทยและทั่วโลก มีจุดเด่นที่ราคาคุ้มค่า ประสิทธิภาพสูง และมีศูนย์บริการในประเทศไทยที่ดูแลและให้บริการหลังการขายได้รวดเร็ว"}
                    ]
                    show_details("แพ็กเกจ", "5 kW", "189,000 - 200,000 บาท", "- แผงโซล่าร์เซลล์ (550W) จำนวน 8-10 แผง\n- อินเวอร์เตอร์ 1 เฟส จำนวน 1 ตัว พร้อมสมาร์ทมิเตอร์\n- ฟรี! ค่าดำเนินการขออนุญาตขนานไฟกับการไฟฟ้า\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี\n- รับประกันงานติดตั้ง 1 ปี", models=models_m, panel_models=panel_models_std)
        with col3:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #C8B6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">10 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("เหมาะสำหรับ: โฮมออฟฟิศ, กิจการขนาดเล็ก\n\nราคารวมติดตั้งเริ่มต้น: **315,000 บาท**\n\n*(ราคารวมแผง, อินเวอร์เตอร์ และอุปกรณ์ครบชุด)*")
                if st.button("ดูรายละเอียด", key="btn_l", use_container_width=True):
                    models_l = [
                        {"name": "Huawei SUN2000-10KTL-M1", "price": "329,000 บาท", "image": get_image_path("SUN2000-10KTL-M1-01.webp", "package3kW"), "description": "แบรนด์ชั้นนำระดับโลก โดดเด่นด้านเทคโนโลยี AI, ระบบป้องกันฟ้าผ่า, และฟีเจอร์ AFCI ป้องกันไฟไหม้ มาพร้อมแอปพลิเคชัน FusionSolar ที่เสถียรและใช้งานง่าย"},
                        {"name": "Growatt MOD 10KTL3-X", "price": "315,000 บาท", "image": get_image_path("growatt-mod-10ktl3-x.jpg", "package3kW"), "description": "แบรนด์ยอดนิยมในไทยและทั่วโลก มีจุดเด่นที่ราคาคุ้มค่า ประสิทธิภาพสูง และมีศูนย์บริการในประเทศไทยที่ดูแลและให้บริการหลังการขายได้รวดเร็ว"}
                    ]
                    show_details("แพ็กเกจ", "10 kW", "315,000 - 329,000 บาท", "- แผงโซล่าร์เซลล์ (550W) จำนวน 14-18 แผง\n- อินเวอร์เตอร์ 3 เฟส จำนวน 1 ตัว พร้อมสมาร์ทมิเตอร์\n- ฟรี! ค่าดำเนินการขออนุญาตขนานไฟกับการไฟฟ้า\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี\n- รับประกันงานติดตั้ง 2 ปี", models=models_l, panel_models=panel_models_std)
            
        # แถวที่ 2 แบ่ง 3 คอลัมน์เหมือนเดิมแต่ปล่อยคอลัมน์สุดท้ายว่างไว้เพื่อให้การ์ดขนาดเท่ากัน
        col4, col5, col6 = st.columns(3)
        with col4:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #B8C0FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">15 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("เหมาะสำหรับ: โรงงาน, กิจการขนาดกลาง\n\nราคารวมติดตั้งเริ่มต้น: **439,000 บาท**\n\n*(ราคารวมแผง, อินเวอร์เตอร์ และอุปกรณ์ครบชุด)*")
                if st.button("ดูรายละเอียด", key="btn_xl", use_container_width=True):
                    models_xl = [
                        {"name": "Huawei SUN2000-15KTL-M2", "price": "454,900 บาท", "image": get_image_path("Huawei-SUN2000-15KTL-M2.jpg", "package3kW"), "description": "แบรนด์ชั้นนำระดับโลก โดดเด่นด้านเทคโนโลยี AI, ระบบป้องกันฟ้าผ่า, และฟีเจอร์ AFCI ป้องกันไฟไหม้ มาพร้อมแอปพลิเคชัน FusionSolar ที่เสถียรและใช้งานง่าย"},
                        {"name": "Growatt MID 15KTL3-X", "price": "439,000 บาท", "image": get_image_path("Growatt MID 15KTL3-X.webp", "package3kW"), "description": "แบรนด์ยอดนิยมในไทยและทั่วโลก มีจุดเด่นที่ราคาคุ้มค่า ประสิทธิภาพสูง และมีศูนย์บริการในประเทศไทยที่ดูแลและให้บริการหลังการขายได้รวดเร็ว"}
                    ]
                    show_details("แพ็กเกจ", "15 kW", "439,000 - 454,900 บาท", "- แผงโซล่าร์เซลล์ (550W) จำนวน 20-28 แผง\n- อินเวอร์เตอร์ 3 เฟส พร้อมสมาร์ทมิเตอร์\n- บริการสำรวจและประเมินโครงสร้างหลังคาฟรี\n- ฟรี! ค่าดำเนินการขออนุญาตขนานไฟกับการไฟฟ้า\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี", models=models_xl, panel_models=panel_models_std)
        with col5:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #BBD0FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">>15 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("เหมาะสำหรับ: โรงงานใหญ่, อุตสาหกรรม\n\nราคารวมติดตั้งเริ่มต้น: **500,000 บาทขึ้นไป**\n\n*(ราคารวมแผง, อินเวอร์เตอร์ และอุปกรณ์ครบชุด)*")
                if st.button("ดูรายละเอียด", key="btn_xxl", use_container_width=True):
                    models_xxl = [
                        {"name": "Huawei SUN2000-30KTL-M3", "price": "550,000 บาท", "image": get_image_path("SUN2000-30KTL-M3.2.webp", "package3kW"), "description": "แบรนด์ชั้นนำระดับโลก โดดเด่นด้านเทคโนโลยี AI, ระบบป้องกันฟ้าผ่า, และฟีเจอร์ AFCI ป้องกันไฟไหม้ มาพร้อมแอปพลิเคชัน FusionSolar ที่เสถียรและใช้งานง่าย"},
                        {"name": "Growatt MID 30KTL3-X", "price": "520,000 บาท", "image": get_image_path("Growatt MID 30KTL3-X.webp", "package3kW"), "description": "แบรนด์ยอดนิยมในไทยและทั่วโลก มีจุดเด่นที่ราคาคุ้มค่า ประสิทธิภาพสูง และมีศูนย์บริการในประเทศไทยที่ดูแลและให้บริการหลังการขายได้รวดเร็ว"},
                        {"name": "Solis 30K-5G", "price": "500,000 บาท", "image": get_image_path("Solis 30K-5G.jpg", "package3kW"), "description": "อินเวอร์เตอร์คุณภาพสูงที่ได้รับความนิยมในยุโรปและออสเตรเลีย มีชื่อเสียงด้านความทนทานและประสิทธิภาพการแปลงไฟที่ยอดเยี่ยมในราคาที่เข้าถึงง่าย"}
                    ]
                    show_details("แพ็กเกจ", ">15 kW", "500,000 - 550,000 บาทขึ้นไป", "- แผงโซล่าร์เซลล์ (550W) จำนวน 30 แผงขึ้นไป\n- อินเวอร์เตอร์ 3 เฟส พร้อมสมาร์ทมิเตอร์\n- ออกแบบระบบและประเมินโหลดตามการใช้งานจริง\n- บริการสำรวจและประเมินโครงสร้างหลังคาฟรี\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี", models=models_xxl, panel_models=panel_models_std)
            
        st.divider()
        
        # ---------------- BATTERY PACKAGES ----------------
        st.markdown("## แพ็กเกจอัปเกรดแบตเตอรี่ (Energy Storage System)")
        st.markdown("*(สำหรับลูกค้าที่สนใจเก็บไฟไว้ใช้ตอนกลางคืน หรือต้องการระบบสำรองไฟตอนไฟดับ อุปกรณ์และแบรนด์ได้รับการขึ้นทะเบียนมาตรฐานจาก PEA)*")
        
        bat1, bat2, bat3 = st.columns(3)
        with bat1:
            with st.container(border=True):
                st.markdown(f"""
                <div style="display: flex; flex-direction: column; height: 100%;">
                    <div style="height: 180px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px;">
                        <img src="{get_base64_image('LUNA2000.webp', 'Battery')}" style="max-height: 100%; max-width: 100%; object-fit: contain;">
                    </div>
                    <div style="background-color: #FFD6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #3B0764; font-size: 20px;">Huawei LUNA2000</h3>
                        <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">ความจุ 5 kWh</span>
                    </div>
                    <div style="flex-grow: 1; min-height: 150px; color: #4a5568; font-size: 14px; line-height: 1.6;">
                        <b>เหมาะสำหรับ:</b> เปิดแอร์ 9,000 BTU 1 ตัว (ได้นาน ~4-5 ชม.)<br><br>
                        <b>ราคาเริ่มต้น:</b> <b style="color: #0f172a; font-size: 16px;">159,000 บาท</b><br><br>
                        <i>(แบรนด์พรีเมียม ดีไซน์สวยงามและปลอดภัยสูง)</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("ดูรายละเอียด", key="btn_bat_huawei", use_container_width=True):
                    show_details("แพ็กเกจแบตเตอรี่ Huawei LUNA2000", "5 kWh", "159,000 บาท", "- แบตเตอรี่ Lithium Iron Phosphate (LiFePO4) ความจุ 5 kWh\n- ระบบจัดการแบตเตอรี่อัจฉริยะ (BMS) ระดับเซลล์ในตัว\n- ดีไซน์สวยงาม ติดตั้งง่าย สามารถซื้อเพิ่มเพื่อขยายความจุได้ในอนาคต\n- มาตรฐานความปลอดภัยระดับสูง ป้องกันไฟไหม้\n- อุปกรณ์ขึ้นทะเบียนและรับรองโดย กฟภ. (PEA)\n- รับประกันสินค้า 10 ปีเต็ม")

        with bat2:
            with st.container(border=True):
                st.markdown(f"""
                <div style="display: flex; flex-direction: column; height: 100%;">
                    <div style="height: 180px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px;">
                        <img src="{get_base64_image('growatt-5-1-kwh.webp', 'Battery')}" style="max-height: 100%; max-width: 100%; object-fit: contain;">
                    </div>
                    <div style="background-color: #E7C6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #3B0764; font-size: 20px;">Growatt ARK</h3>
                        <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">ความจุ 5.1 kWh</span>
                    </div>
                    <div style="flex-grow: 1; min-height: 150px; color: #4a5568; font-size: 14px; line-height: 1.6;">
                        <b>เหมาะสำหรับ:</b> เปิดแอร์และตู้เย็น (ได้นาน ~4-5 ชม.)<br><br>
                        <b>ราคาเริ่มต้น:</b> <b style="color: #0f172a; font-size: 16px;">135,000 บาท</b><br><br>
                        <i>(คุ้มค่าต่อการลงทุน ขยายความจุได้ง่าย)</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("ดูรายละเอียด", key="btn_bat_growatt", use_container_width=True):
                    show_details("แพ็กเกจแบตเตอรี่ Growatt ARK", "5.1 kWh", "135,000 บาท", "- แบตเตอรี่ Lithium Iron Phosphate (LiFePO4) ความจุ 5.1 kWh\n- รองรับการใช้งานร่วมกับอินเวอร์เตอร์ Growatt แบบ Hybrid\n- ดีไซน์แบบโมดูล วางซ้อนกันได้ ประหยัดพื้นที่การติดตั้ง\n- อายุการใช้งานยาวนาน (Cycle Life สูง)\n- อุปกรณ์ขึ้นทะเบียนและรับรองโดย กฟภ. (PEA)\n- รับประกันสินค้า 10 ปีเต็ม")

        with bat3:
            with st.container(border=True):
                st.markdown(f"""
                <div style="display: flex; flex-direction: column; height: 100%;">
                    <div style="height: 180px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px;">
                        <img src="{get_base64_image('Deye  Dyness.png', 'Battery')}" style="max-height: 100%; max-width: 100%; object-fit: contain;">
                    </div>
                    <div style="background-color: #C8B6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #3B0764; font-size: 20px;">Deye / Dyness</h3>
                        <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">ความจุ 10 kWh</span>
                    </div>
                    <div style="flex-grow: 1; min-height: 150px; color: #4a5568; font-size: 14px; line-height: 1.6;">
                        <b>เหมาะสำหรับ:</b> เปิดแอร์ 2 ตัว หรือบ้านที่ใช้ไฟกลางคืนเยอะ<br><br>
                        <b>ราคาเริ่มต้น:</b> <b style="color: #0f172a; font-size: 16px;">180,000 บาท</b><br><br>
                        <i>(ความจุสูงจัดเต็ม ราคาต่อหน่วยคุ้มค่าที่สุด)</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("ดูรายละเอียด", key="btn_bat_deye", use_container_width=True):
                    show_details("แพ็กเกจแบตเตอรี่ Deye / Dyness", "10 kWh", "180,000 บาท", "- แบตเตอรี่ Lithium Iron Phosphate (LiFePO4) ความจุขนาดใหญ่ 10 kWh\n- นิยมใช้คู่กับอินเวอร์เตอร์ Hybrid แบรนด์ยอดนิยม\n- ตอบโจทย์บ้านที่ใช้ไฟกลางคืนเยอะ และต้องการไฟสำรองยาวนานเมื่อไฟดับ\n- คุ้มค่าที่สุดเมื่อเทียบราคาต่อความจุ (kWh)\n- อุปกรณ์ขึ้นทะเบียนและรับรองโดย กฟภ. (PEA)\n- รับประกันสินค้า 10 ปีเต็ม")

        st.divider()
        
        # ---------------- NEWS & ARTICLES ----------------
        st.markdown("## ข่าวสารและสาระน่ารู้เกี่ยวกับโซล่าร์เซลล์")
        n1, n2, n3 = st.columns(3)
        with n1:
            with st.container(border=True):
                st.markdown('<a href="https://peasolar.pea.co.th/" target="_blank"><img src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=600&h=350&auto=format&fit=crop" class="news-img"></a>', unsafe_allow_html=True)
                st.markdown("#### กฟภ. หนุนประชาชนติดตั้ง Solar Rooftop")
                st.markdown("การไฟฟ้าส่วนภูมิภาค (PEA) ส่งเสริมให้ประชาชนและภาคธุรกิจติดตั้งระบบผลิตไฟฟ้าจากพลังงานแสงอาทิตย์บนหลังคา เพื่อลดภาระค่าใช้จ่ายระยะยาว...")
                st.write("")
                st.link_button("อ่านเพิ่มเติม", "https://peasolar.pea.co.th/", use_container_width=True)
        with n2:
            with st.container(border=True):
                st.markdown('<a href="https://www.thaigov.go.th/" target="_blank"><img src="https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?q=80&w=600&h=350&auto=format&fit=crop" class="news-img"></a>', unsafe_allow_html=True)
                st.markdown("#### รัฐส่งเสริมโซล่าเซลล์ราคาประหยัด")
                st.markdown("รัฐบาลเตรียมลดภาระค่าไฟฟ้าประชาชน ส่งเสริมใช้โซล่าเซลล์ราคาถูก พร้อมพัฒนาอินเวอร์เตอร์และปรับกฎหมายให้เข้าถึงพลังงานสะอาดได้ง่ายขึ้น...")
                st.write("")
                st.link_button("อ่านเพิ่มเติม", "https://www.thaigov.go.th/", use_container_width=True)
        with n3:
            with st.container(border=True):
                st.markdown('<a href="https://www.scb.co.th/th/personal-banking/loans/home-loans/green-energy-loan.html" target="_blank"><img src="https://images.unsplash.com/photo-1613665813446-82a78c468a1d?q=80&w=600&h=350&auto=format&fit=crop" class="news-img"></a>', unsafe_allow_html=True)
                st.markdown("#### ธนาคารเร่งออกสินเชื่อ Green Energy")
                st.markdown("หลายธนาคารชั้นนำ เปิดตัวสินเชื่อติดตั้งโซลาร์เซลล์ทั้งในบ้านและธุรกิจ ด้วยเงื่อนไขยืดหยุ่นและอัตราดอกเบี้ยพิเศษเพื่อลดรายจ่ายระยะยาว...")
                st.write("")
                st.link_button("อ่านเพิ่มเติม", "https://www.scb.co.th/th/personal-banking/loans/home-loans/green-energy-loan.html", use_container_width=True)
                
        st.write("")
        st.write("")
        
        # ---------------- CONTACT US ----------------
        st.markdown("## สนใจติดตั้ง / ติดต่อเรา (Contact Us)")
        st.markdown("ทีมวิศวกรของเราพร้อมให้คำปรึกษาและประเมินหน้างานเบื้องต้น **ฟรี!** ไม่มีค่าใช้จ่าย ติดต่อเราได้ผ่านช่องทางด้านล่างนี้")
        
        c_contact1, c_contact2, c_contact3, c_contact4 = st.columns(4)
        with c_contact1:
            with st.container(border=True):
                line_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="45" height="45"><path fill="#00C300" d="M24 10.3c0-5.7-5.4-10.3-12-10.3S0 4.6 0 10.3c0 5 4.3 9.3 10.1 10.1 1 .2 2.4.6 2.7 1.4.2.6.2 1.5-.1 2.6-.2.9-.8 2.8-.8 2.8s-.3.9 1.3.1c1.5-.8 8.1-4.7 10.2-9 1-2.4 1.2-4.9.6-7z"/><path fill="#FFF" d="M6 13h-2.1c-.2 0-.4-.2-.4-.4V8.4c0-.2.2-.4.4-.4h.8c.2 0 .4.2.4.4v3.4h.9c.2 0 .4.2.4.4v.4c0 .2-.2.4-.4.4zm3.9 0h-.8c-.2 0-.4-.2-.4-.4V8.4c0-.2.2-.4.4-.4h.8c.2 0 .4.2.4.4v4.2c0 .2-.2.4-.4.4zm3.8-3.4v3.1c0 .2-.2.4-.4.4h-.8c-.2 0-.4-.2-.4-.4V8.4c0-.2.2-.4.4-.4h.8c.2 0 .4.2.4.4v1.8l1.7-2c.1-.2.3-.2.5-.2h.9c.2 0 .2.3.1.5L14.7 10l1.8 2.5c.2.2.1.5-.1.5h-1c-.2 0-.4-.1-.5-.3l-1.2-1.7zm5.9 3.4h-2.1c-.2 0-.4-.2-.4-.4V8.4c0-.2.2-.4.4-.4h2.1c.2 0 .4.2.4.4v.4c0 .2-.2.4-.4.4H18v.8h1.2c.2 0 .4.2.4.4v.4c0 .2-.2.4-.4.4H18v.8h1.6c.2 0 .4.2.4.4v.4c0 .2-.2.4-.4.4z"/></svg>'''
                st.markdown(f"<div style='text-align:center; height: 50px; margin-bottom: 5px; display: flex; align-items: center; justify-content: center;'>{line_svg}</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; color: #16a34a; font-weight: bold;'>LINE Official</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; color: #64748b; margin-bottom: 15px;'>@SolarJoyEnergy</div>", unsafe_allow_html=True)
                st.link_button("แอดไลน์", "https://line.me/th/", use_container_width=True)
        with c_contact2:
            with st.container(border=True):
                fb_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="45" height="45"><path fill="#1877F2" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.469h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.469h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>'''
                st.markdown(f"<div style='text-align:center; height: 50px; margin-bottom: 5px; display: flex; align-items: center; justify-content: center;'>{fb_svg}</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; color: #0284c7; font-weight: bold;'>Facebook Page</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; color: #64748b; margin-bottom: 15px;'>SolarJoy Energy</div>", unsafe_allow_html=True)
                st.link_button("ทักแชท", "https://facebook.com/", use_container_width=True)
        with c_contact3:
            with st.container(border=True):
                phone_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="45" height="45"><path fill="#ea580c" d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>'''
                st.markdown(f"<div style='text-align:center; height: 50px; margin-bottom: 5px; display: flex; align-items: center; justify-content: center;'>{phone_svg}</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; color: #ea580c; font-weight: bold;'>โทรศัพท์ (Hotline)</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; color: #64748b; margin-bottom: 15px;'>02-123-4567</div>", unsafe_allow_html=True)
                st.link_button("โทรติดต่อ", "tel:021234567", use_container_width=True)
        with c_contact4:
            with st.container(border=True):
                email_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="45" height="45"><path fill="#6d28d9" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>'''
                st.markdown(f"<div style='text-align:center; height: 50px; margin-bottom: 5px; display: flex; align-items: center; justify-content: center;'>{email_svg}</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; color: #6d28d9; font-weight: bold;'>อีเมล (Email)</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center; color: #64748b; margin-bottom: 15px;'>hello@solarjoy.com</div>", unsafe_allow_html=True)
                st.link_button("ส่งอีเมล", "mailto:hello@solarjoy.com", use_container_width=True)
                
        st.write("")
        st.write("")

        # ---------------- FOOTER ----------------
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #cbd5e1; padding: 40px 20px; border-radius: 24px; margin-top: 60px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 15px;">
                <h2 style="color: white; margin: 0; font-weight: 700;">SolarJoy Energy</h2>
            </div>
            <p style="font-size: 15px; margin-bottom: 25px; color: #94a3b8; max-width: 500px; margin-left: auto; margin-right: auto;">
                ยกระดับการใช้พลังงานของคุณด้วยระบบวิเคราะห์อัจฉริยะ 
                ให้การติดตั้งโซลาร์เซลล์เป็นเรื่องง่าย คุ้มค่า และยั่งยืน
            </p>
            <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 30px; flex-wrap: wrap;">
                <a href="#" style="color: #38bdf8; text-decoration: none; font-weight: 500; transition: color 0.2s;">หน้าแรก</a>
                <a href="#" style="color: #38bdf8; text-decoration: none; font-weight: 500; transition: color 0.2s;">บริการของเรา</a>
                <a href="#" style="color: #38bdf8; text-decoration: none; font-weight: 500; transition: color 0.2s;">แพ็กเกจ</a>
                <a href="#" style="color: #38bdf8; text-decoration: none; font-weight: 500; transition: color 0.2s;">ติดต่อเรา</a>
            </div>
            <hr style="border: none; border-top: 1px solid #334155; margin: 0 auto 20px auto; max-width: 800px;">
            <p style="font-size: 13px; color: #64748b; margin: 0;">
                &copy; 2026 Solar Analytics Platform. All rights reserved. | พัฒนาด้วยความใส่ใจ เพื่อพลังงานสะอาด
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.stop() # หยุดการทำงานสคริปต์ตรงนี้ เพื่อไม่ให้แสดงผลหน้าอื่นซ้อนกัน

    # --- Sidebar สำหรับฟิลเตอร์ (ตัวกรอง) ---
    st.sidebar.header("ตัวกรองข้อมูล")
    selected_types = st.sidebar.multiselect(
        "เลือกประเภทผู้ใช้งานเป้าหมาย",
        options=df['user_type_name'].unique(),
        default=df['user_type_name'].unique()
    )
    
    # กรองข้อมูลตามประเภทที่เลือก
    filtered_df = df[df['user_type_name'].isin(selected_types)]
    
    # --- ดึงคอลัมน์หมายเลขผู้ใช้ไฟ (ทำครั้งเดียวเพื่อใช้กับทุกหน้า) ---
    customer_col = None
    for col in ['หมายเลขผู้ใช้ไฟ', 'c', 'ca', 'ca_no', 'pea_no', 'customer_id', 'contract_account']:
        if col in filtered_df.columns:
            customer_col = col
            break
            
    if customer_col is None and len(filtered_df.columns) >= 3:
        customer_col = filtered_df.columns[2]

    if customer_col:
        filtered_df = filtered_df.copy()
        filtered_df[customer_col] = filtered_df[customer_col].astype(str).str.replace(r'\.0$', '', regex=True)
        filtered_df[customer_col] = filtered_df[customer_col].str.lstrip('0').str.strip()
        filtered_df.loc[filtered_df[customer_col].isin(['nan', 'NaN', '']), customer_col] = None

    # ==========================================
    # ส่วนที่ 2: หน้าแดชบอร์ดวิเคราะห์ภาพรวม
    # ==========================================
    if page == "แดชบอร์ดวิเคราะห์":
        st.title("แดชบอร์ดวิเคราะห์พฤติกรรมการใช้ไฟฟ้า")
        st.markdown("*(สำหรับวิเคราะห์ภาพรวมการใช้ไฟฟ้า แนวโน้ม และพฤติกรรมของแต่ละกลุ่มลูกค้า)*")
        
        # --- KPI Section ---
        st.subheader("สรุปภาพรวม (KPIs) ของกลุ่มที่เลือก")
        col1, col2, col3 = st.columns(3)
        
        total_kwh = filtered_df['kwh_total'].sum()
        total_amt = filtered_df['amt_invoice'].sum()
        avg_rate = total_amt / total_kwh if total_kwh > 0 else 0
        
        col1.metric("ปริมาณการใช้ไฟรวม (kWh)", f"{total_kwh:,.2f} หน่วย")
        col2.metric("ค่าไฟฟ้ารวม (บาท)", f"฿ {total_amt:,.2f}")
        col3.metric("ค่าไฟเฉลี่ยต่อหน่วย", f"฿ {avg_rate:,.2f} / kWh")
        
        st.divider()
        
        # --- ข้อมูลพื้นฐานสำหรับวิเคราะห์กลุ่มลูกค้า ---
        st.subheader("ข้อมูลพื้นฐานสำหรับวิเคราะห์กลุ่มลูกค้า")
        st.markdown("*(ใช้ดูพฤติกรรมรายบุคคล/รายบิล เพื่อประเมินว่าแต่ละรายใช้ไฟเยอะพอที่จะคุ้มทุนในการเสนอโปรเจกต์หรือไม่)*")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        if customer_col:
            unique_customers = filtered_df[customer_col].nunique()
            info_col1.metric("จำนวนครัวเรือนรวม (ครัวเรือน)", f"{unique_customers:,}")
            
            avg_kwh_per_customer = total_kwh / unique_customers if unique_customers > 0 else 0
            info_col2.metric("การใช้ไฟเฉลี่ยต่อครัวเรือน", f"{avg_kwh_per_customer:,.2f} kWh")
            
            avg_amt_per_customer = total_amt / unique_customers if unique_customers > 0 else 0
            info_col3.metric("ค่าไฟเฉลี่ยต่อครัวเรือน", f"฿ {avg_amt_per_customer:,.2f}")
            
            # ใช้ภาษาอังกฤษใน agg() ก่อน เพื่อป้องกันปัญหาคอลัมน์หายจาก Keyword Arguments ภาษาไทย
            customer_group_summary = filtered_df.groupby('user_type_name').agg(
                count_customers=(customer_col, 'nunique'),
                sum_kwh=('kwh_total', 'sum'),
                sum_amt=('amt_invoice', 'sum')
            ).reset_index()
            
            # เปลี่ยนชื่อคอลัมน์กลับเป็นภาษาไทยเพื่อการแสดงผล
            customer_group_summary = customer_group_summary.rename(columns={
                'count_customers': 'จำนวนครัวเรือน',
                'sum_kwh': 'ใช้ไฟรวม_kWh',
                'sum_amt': 'ค่าไฟรวม_บาท'
            })
            customer_group_summary['ค่าไฟเฉลี่ยต่อครัวเรือน_บาท'] = customer_group_summary['ค่าไฟรวม_บาท'] / customer_group_summary['จำนวนครัวเรือน']
        else:
            total_bills = len(filtered_df)
            info_col1.metric("จำนวนบิล/รายการรวม", f"{total_bills:,}")
            
            avg_kwh_per_bill = total_kwh / total_bills if total_bills > 0 else 0
            info_col2.metric("การใช้ไฟเฉลี่ยต่อบิล", f"{avg_kwh_per_bill:,.2f} kWh")
            
            avg_amt_per_bill = total_amt / total_bills if total_bills > 0 else 0
            info_col3.metric("ค่าไฟเฉลี่ยต่อบิล", f"฿ {avg_amt_per_bill:,.2f}")
            
            customer_group_summary = filtered_df.groupby('user_type_name').agg(
                count_bills=('kwh_total', 'count'),
                sum_kwh=('kwh_total', 'sum'),
                sum_amt=('amt_invoice', 'sum')
            ).reset_index()
            
            customer_group_summary = customer_group_summary.rename(columns={
                'count_bills': 'จำนวนบิล',
                'sum_kwh': 'ใช้ไฟรวม_kWh',
                'sum_amt': 'ค่าไฟรวม_บาท'
            })
            customer_group_summary['ค่าไฟเฉลี่ยต่อบิล_บาท'] = customer_group_summary['ค่าไฟรวม_บาท'] / customer_group_summary['จำนวนบิล']

        st.markdown("**ตารางสรุปพฤติกรรมเชิงลึกแบ่งตามกลุ่มลูกค้า**")
        
        format_dict_summary = {col: '{:,.2f}' for col in ['ใช้ไฟรวม_kWh', 'ค่าไฟรวม_บาท', 'ค่าไฟเฉลี่ยต่อครัวเรือน_บาท', 'ค่าไฟเฉลี่ยต่อบิล_บาท'] if col in customer_group_summary.columns}
        st.dataframe(customer_group_summary.style.format(format_dict_summary), use_container_width=True)

        # --- ข้อมูลสรุปรายเดือน (นำมาแสดงในข้อมูลพื้นฐาน) ---
        if customer_col:
            monthly_trend = filtered_df.groupby(['year', 'month']).agg(
                kwh_total=('kwh_total', 'sum'),
                amt_invoice=('amt_invoice', 'sum'),
                customer_count=(customer_col, 'nunique')
            ).reset_index()
            cust_label = "จำนวนครัวเรือน"
        else:
            monthly_trend = filtered_df.groupby(['year', 'month']).agg(
                kwh_total=('kwh_total', 'sum'),
                amt_invoice=('amt_invoice', 'sum'),
                customer_count=('kwh_total', 'count')
            ).reset_index()
            cust_label = "จำนวนบิล (ใบ)"
            
        monthly_trend['period_label'] = monthly_trend['year'] + "-" + monthly_trend['month']
        
        st.markdown(f"**ตารางสรุป{cust_label}และการใช้ไฟในแต่ละเดือน**")
        monthly_display = monthly_trend[['period_label', 'customer_count', 'kwh_total', 'amt_invoice']].rename(columns={
            'period_label': 'เดือน-ปี',
            'customer_count': cust_label,
            'kwh_total': 'ใช้ไฟรวม_kWh',
            'amt_invoice': 'ค่าไฟรวม_บาท'
        })
        
        format_dict_monthly = {'ใช้ไฟรวม_kWh': '{:,.2f}', 'ค่าไฟรวม_บาท': '{:,.2f}'}
        st.dataframe(monthly_display.style.format(format_dict_monthly), use_container_width=True)

        st.divider()

        # --- Charts Section ---

        st.subheader("เปรียบเทียบหน่วยการใช้ไฟฟ้า ปี 2025 - 2026 (ม.ค. - มี.ค.)")
        st.markdown("*(ใช้เปรียบเทียบการเปลี่ยนแปลงของปริมาณการใช้ไฟฟ้าในช่วงเดือนมกราคมถึงมีนาคมของปี 2025 และ 2026)*")
        
        # กรองข้อมูลเฉพาะปี 2025-2026 และเดือน 01-03
        target_years = ['2025', '2026']
        target_months = ['01', '02', '03']
        
        yearly_compare_df = monthly_trend[
            monthly_trend['year'].astype(str).isin(target_years) & 
            monthly_trend['month'].astype(str).str.zfill(2).isin(target_months)
        ].copy()
        
        if not yearly_compare_df.empty:
            # เปลี่ยนรหัสเดือนเป็นชื่อเดือนภาษาไทย
            month_map = {'01': 'มกราคม', '02': 'กุมภาพันธ์', '03': 'มีนาคม'}
            yearly_compare_df['ชื่อเดือน'] = yearly_compare_df['month'].astype(str).str.zfill(2).map(month_map)
            
            fig_trend = px.bar(
                yearly_compare_df, 
                x='ชื่อเดือน', 
                y='kwh_total', 
                color='year',
                barmode='group', 
                text_auto='.2s',
                title="เปรียบเทียบหน่วยการใช้ไฟ (kWh) ระหว่างปี 2025 และ 2026",
                labels={'ชื่อเดือน': 'เดือน', 'kwh_total': 'การใช้ไฟ (kWh)', 'year': 'ปี'}
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("ตารางวิเคราะห์การเติบโต (Year-over-Year)")
            st.markdown("*(เปรียบเทียบจำนวนบ้านและการใช้ไฟของปี 2025 และ 2026)*")
            
            # สร้าง Pivot Table เพื่อเทียบปี 2025 กับ 2026
            pivot_df = yearly_compare_df.pivot(index=['month', 'ชื่อเดือน'], columns='year', values=['customer_count', 'kwh_total']).reset_index()
            
            # ยุบ MultiIndex columns ให้เรียกใช้ง่ายๆ
            pivot_df.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in pivot_df.columns]
            
            # ตรวจสอบคอลัมน์ว่ามีทั้ง 2025 และ 2026 หรือไม่
            if 'kwh_total_2025' in pivot_df.columns and 'kwh_total_2026' in pivot_df.columns and 'customer_count_2025' in pivot_df.columns and 'customer_count_2026' in pivot_df.columns:
                pivot_df['การเติบโตหน่วยไฟ (%)'] = ((pivot_df['kwh_total_2026'] - pivot_df['kwh_total_2025']) / pivot_df['kwh_total_2025']) * 100
                pivot_df['ผลต่างจำนวนบ้าน'] = pivot_df['customer_count_2026'] - pivot_df['customer_count_2025']
                
                # จัดเตรียม DataFrame สำหรับแสดงผล
                display_growth = pivot_df[['ชื่อเดือน', 'customer_count_2025', 'customer_count_2026', 'ผลต่างจำนวนบ้าน', 'kwh_total_2025', 'kwh_total_2026', 'การเติบโตหน่วยไฟ (%)']].copy()
                display_growth = display_growth.rename(columns={
                    'customer_count_2025': 'จำนวนบ้าน ปี 2025',
                    'customer_count_2026': 'จำนวนบ้าน ปี 2026',
                    'kwh_total_2025': 'การใช้ไฟ ปี 2025 (kWh)',
                    'kwh_total_2026': 'การใช้ไฟ ปี 2026 (kWh)'
                })
                
                format_growth = {
                    'จำนวนบ้าน ปี 2025': '{:,.0f}',
                    'จำนวนบ้าน ปี 2026': '{:,.0f}',
                    'ผลต่างจำนวนบ้าน': '{:+,.0f}',
                    'การใช้ไฟ ปี 2025 (kWh)': '{:,.2f}',
                    'การใช้ไฟ ปี 2026 (kWh)': '{:,.2f}',
                    'การเติบโตหน่วยไฟ (%)': '{:+,.2f}%'
                }
                
                st.dataframe(display_growth.style.format(format_growth), use_container_width=True)
                
                # เพิ่มสรุปผลกราฟที่ 1
                total_growth_kwh = ((pivot_df['kwh_total_2026'].sum() - pivot_df['kwh_total_2025'].sum()) / pivot_df['kwh_total_2025'].sum()) * 100 if pivot_df['kwh_total_2025'].sum() > 0 else 0
                total_growth_cust = pivot_df['customer_count_2026'].sum() - pivot_df['customer_count_2025'].sum()
                trend_text = "เพิ่มขึ้น" if total_growth_kwh > 0 else "ลดลง"
                st.success(f"**สรุปผลการเปรียบเทียบ (YoY):** จากข้อมูลพบว่าแนวโน้มการใช้ไฟฟ้ารวมในช่วงต้นปี 2026 **{trend_text} {abs(total_growth_kwh):.2f}%** เมื่อเทียบกับปี 2025 "
                           f"และการเปลี่ยนแปลงของจำนวนผู้ใช้ไฟทั้งหมด **{total_growth_cust:+,.0f} ราย** ซึ่งสะท้อนให้เห็นถึงแนวโน้มความต้องการใช้พลังงาน (Demand) ในตลาดที่{trend_text}")
            else:
                st.info("ข้อมูลไม่เพียงพอสำหรับการเปรียบเทียบการเติบโตระหว่างปี 2025 และ 2026 (อาจมีข้อมูลเพียงปีเดียว)")
        else:
            st.info("ยังไม่มีข้อมูลการใช้ไฟของเดือน มกราคม-มีนาคม ในปี 2025 และ 2026 ในระบบ")

        # --- สร้างกราฟแท่งความเคลื่อนไหวรายเดือน (New vs Lost) ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("วิเคราะห์การเพิ่มขึ้นและลดลงของผู้ใช้ไฟ (New vs Lost Users)")
        
        if customer_col:
            temp_df = filtered_df[[customer_col, 'year', 'month']].copy()
            
            temp_df['period_label_sort'] = temp_df['year'].astype(str) + "-" + temp_df['month'].astype(str).str.zfill(2)
            
            # 1. คำนวณข้อมูลจาก df ทั้งหมดเพื่อให้ความถูกต้องเรื่อง "ผู้ใช้ใหม่"
            monthly_users_series = temp_df.groupby('period_label_sort')[customer_col].apply(lambda x: set(x.dropna().astype(str)))
            all_sorted_months = monthly_users_series.index.tolist()
            
            full_stats = []
            seen_so_far = set()
            
            # 2. วนลูปเปรียบเทียบข้อมูลรายเดือน
            for i, month_val in enumerate(all_sorted_months):
                current_set = monthly_users_series[month_val]
                if i == 0:
                    new_cnt = len(current_set)
                    lost_cnt = 0
                else:
                    prev_month = all_sorted_months[i-1]
                    prev_set = monthly_users_series[prev_month]
                    
                    # ผู้ใช้ใหม่: อยู่ในเดือนนี้แต่ไม่เคยเห็นในเดือนก่อนหน้าทั้งหมด (seen_so_far)
                    new_cnt = len(current_set - seen_so_far)
                    # ผู้ใช้ที่หายไป: เคยอยู่ในเดือนที่แล้วแต่หายไปในเดือนนี้
                    lost_cnt = len(prev_set - current_set)
                    
                # แปลงรหัสเดือนเป็นชื่อเดือนภาษาไทยเพื่อให้กราฟอ่านง่ายขึ้น
                year, month = month_val.split('-')
                month_map = {
                    '01': 'มกราคม', '02': 'กุมภาพันธ์', '03': 'มีนาคม',
                    '04': 'เมษายน', '05': 'พฤษภาคม', '06': 'มิถุนายน',
                    '07': 'กรกฎาคม', '08': 'สิงหาคม', '09': 'กันยายน',
                    '10': 'ตุลาคม', '11': 'พฤศจิกายน', '12': 'ธันวาคม'
                }
                display_m = f"{month_map.get(month, month)} {year}"

                full_stats.append({
                    "Month_Year": display_m,
                    "ผู้ใช้ใหม่ (New)": new_cnt,
                    "ผู้ใช้ที่หายไป (Lost)": -lost_cnt # เก็บเป็นค่าลบสำหรับตรรกะเบื้องต้น
                })
                seen_so_far.update(current_set)
                
            # 3. เตรียม DataFrame สำหรับแสดงผล
            comparison_df = pd.DataFrame(full_stats)
            
            if not comparison_df.empty:
                # 4. ส่วนการสร้างกราฟ Interactive
                st.write("**วิเคราะห์การเพิ่มขึ้นและลดลงของผู้ใช้ไฟ (Interactive)**")
                
                # แปลงค่า Lost เป็นค่าบวก (Absolute) เพื่อให้นำเสนอแท่งกราฟในแกนบวกคู่กัน
                comparison_df["ผู้ใช้ที่หายไป (Lost)"] = comparison_df["ผู้ใช้ที่หายไป (Lost)"].abs()
                
                # สร้างกราฟด้วย Plotly
                fig = go.Figure()

                # แท่งกราฟผู้ใช้ใหม่ (สีเขียว)
                fig.add_trace(go.Bar(
                    x=comparison_df["Month_Year"],
                    y=comparison_df["ผู้ใช้ใหม่ (New)"],
                    name='ผู้ใช้ใหม่ (New)',
                    marker_color='#28a745',
                    hovertemplate='<b>%{x}</b><br>New Users: %{y:,}<extra></extra>'
                ))

                # แท่งกราฟผู้ใช้ที่หายไป (สีแดง)
                fig.add_trace(go.Bar(
                    x=comparison_df["Month_Year"],
                    y=comparison_df["ผู้ใช้ที่หายไป (Lost)"],
                    name='ผู้ใช้ที่หายไป (Lost)',
                    marker_color='#dc3545',
                    hovertemplate='<b>%{x}</b><br>Lost Users: %{y:,}<extra></extra>'
                ))
                
                # ตั้งค่า Layout ของกราฟ
                fig.update_layout(
                    title='New vs Lost Users Trend',
                    xaxis_title='Month',
                    yaxis_title='Number of Users',
                    yaxis=dict(tickformat=","), # แสดงลูกน้ำคั่นหลักพัน
                    barmode='group', # วางแท่งกราฟข้างกัน
                    template='plotly_white',
                    hovermode='x unified',
                    height=500
                )

                # แสดงผลกราฟใน Streamlit
                st.plotly_chart(fig, use_container_width=True)

                st.info("**ผู้ใช้ใหม่** คือคนที่ไม่เคยเห็นรหัสนี้มาก่อนในข้อมูลเดือนก่อนหน้า | **ผู้ใช้ที่หายไป** คือคนที่มีชื่อเดือนที่แล้วแต่ไม่มีในเดือนนี้")
                
                # เพิ่มสรุปผลกราฟที่ 2
                total_new = comparison_df["ผู้ใช้ใหม่ (New)"].sum()
                total_lost = comparison_df["ผู้ใช้ที่หายไป (Lost)"].sum()
                net_change = total_new - total_lost
                status_text = "เติบโตเพิ่มขึ้น" if net_change >= 0 else "หดตัวลง"
                st.success(f"**สรุปความเคลื่อนไหวรายเดือน:** ตลอดช่วงเวลาที่วิเคราะห์ พบว่ามีฐานลูกค้าใหม่เข้ามาในระบบสะสม **{total_new:,} ราย** และหายไป **{total_lost:,} ราย** (สุทธิแล้วฐานลูกค้า**{status_text} {abs(net_change):,} ราย**) ข้อมูลนี้ช่วยให้มองเห็นอัตราการเข้าออกของลูกค้า (Churn Rate) และสามารถนำไปวางแผนขยายฐานลูกค้าใหม่เพื่อนำเสนอโครงการได้")
            else:
                st.info("ข้อมูลไม่เพียงพอสำหรับสร้างกราฟความเคลื่อนไหวรายเดือน")
        else:
            st.warning("ไม่สามารถสร้างกราฟความเคลื่อนไหวได้ เนื่องจากไม่พบคอลัมน์หมายเลขผู้ใช้ไฟ")

        st.divider()

        col_pie1, col_pie2 = st.columns(2)
        
        with col_pie1:
            st.subheader("สัดส่วนการใช้ไฟ (kWh)")
            st.markdown("*(ใช้ดูว่ากลุ่มลูกค้าไหนมีการใช้พลังงานไฟฟ้าเยอะที่สุด)*")
            type_summary_kwh = filtered_df.groupby('user_type_name')['kwh_total'].sum().reset_index()
            fig_pie_kwh = px.pie(type_summary_kwh, values='kwh_total', names='user_type_name', 
                                 title="สัดส่วนปริมาณการใช้ไฟ (kWh) ตามกลุ่มลูกค้า", hole=0.4)
            st.plotly_chart(fig_pie_kwh, use_container_width=True)
            
        with col_pie2:
            st.subheader("สัดส่วนค่าไฟ (บาท)")
            st.markdown("*(ใช้หา Target Group ว่ากลุ่มไหนคือลูกค้ารายใหญ่ที่สุดที่ควรเข้าไปคุยเสนอโปรเจกต์)*")
            type_summary_amt = filtered_df.groupby('user_type_name')['amt_invoice'].sum().reset_index()
            fig_pie_amt = px.pie(type_summary_amt, values='amt_invoice', names='user_type_name', 
                                 title="สัดส่วนเม็ดเงินค่าไฟ (บาท) ตามกลุ่มลูกค้า", hole=0.4)
            st.plotly_chart(fig_pie_amt, use_container_width=True)

        st.write("")
        if not type_summary_amt.empty and not type_summary_kwh.empty:
            top_kwh_group = type_summary_kwh.sort_values(by='kwh_total', ascending=False).iloc[0]
            top_amt_group = type_summary_amt.sort_values(by='amt_invoice', ascending=False).iloc[0]
            st.success(f"**สรุปสัดส่วนกลุ่มเป้าหมาย:** กลุ่มลูกค้าที่มีปริมาณการใช้ไฟฟ้าสุทธิสูงสุดคือ **{top_kwh_group['user_type_name']}** "
                       f"แต่กลุ่มที่สร้างเม็ดเงินค่าไฟ (มูลค่าตลาด) รวมสูงสุดคือ **{top_amt_group['user_type_name']}** "
                       f"ดังนั้นในเชิงกลยุทธ์การขาย บริษัทควรจัดลำดับความสำคัญในการเข้าไปเสนอโปรเจกต์กับกลุ่ม **{top_amt_group['user_type_name']}** เป็นอันดับแรก เพื่อผลตอบแทนรวมที่สูงที่สุด")

        st.divider()
        st.stop() # จบหน้าแดชบอร์ดตรงนี้

    # ==========================================
    # ส่วนที่ 3: หน้าค้นหาและวิเคราะห์ลูกค้าเป้าหมาย
    # ==========================================
    if page == "ค้นหาลูกค้าเป้าหมาย" or page == "ค้นหาลูกค้าเป้าหมาย":
        st.title("ค้นหาและวิเคราะห์กลุ่มลูกค้าเป้าหมาย")
        st.markdown("*(เจาะลึกพฤติกรรมรายบุคคล ดูตำแหน่งแผนที่ และตารางประเมินความคุ้มค่าแบบ Real-Time)*")
        
        # --- แผนที่ตำแหน่งลูกค้า ---
        st.subheader("แผนที่แสดงเป้าหมายลูกค้าที่ควรติดโซล่าร์เซลล์")
        st.markdown("*(แสดงจุดพิกัดของลูกค้าเพื่อประเมินศักยภาพในการเสนอโปรเจกต์)*")

    show_only_hot_leads = st.toggle("🔥 แสดงเฉพาะกลุ่มโอกาสปิดการขายสูง (Hot Leads)", value=False, help="กรองเฉพาะลูกค้าที่คืนทุนไว ประหยัดเยอะ และบริษัทได้กำไรจากการติดตั้ง")

    # ดึงคอลัมน์พิกัด G และ H ที่ถูกกำหนดชื่อมาจาก read_all_csv.py
    x_col = 'x_coord' if 'x_coord' in filtered_df.columns else None
    y_col = 'y_coord' if 'y_coord' in filtered_df.columns else None
    
    # หากไม่มีคอลัมน์ที่ตั้งไว้ ให้บังคับดึงจากตำแหน่งคอลัมน์ G (Index 6) และ H (Index 7) โดยตรง
    if x_col is None and len(filtered_df.columns) >= 8:
        x_col = filtered_df.columns[6]
        y_col = filtered_df.columns[7]
        
    if x_col and y_col:
        # เตรียมคอลัมน์ที่จำเป็น รวมถึงข้อมูลเพิ่มเติมสำหรับแสดงตอนเอาเมาส์ชี้ (Hover) บนแผนที่
        cols_to_keep = [x_col, y_col]
        if customer_col: cols_to_keep.append(customer_col)
        if 'amt_invoice' in filtered_df.columns: cols_to_keep.append('amt_invoice')
        if 'kwh_total' in filtered_df.columns: cols_to_keep.append('kwh_total') # เพิ่มเพื่อคำนวณความคุ้มค่า
        if 'user_type_name' in filtered_df.columns: cols_to_keep.append('user_type_name') # เพิ่มเพื่อใช้แยกกลุ่มบนแผนที่
        
        cols_to_keep = list(dict.fromkeys(cols_to_keep)) # ลบชื่อคอลัมน์ที่ซ้ำกันออก
        map_df = filtered_df[cols_to_keep].copy()
        
        # ทำความสะอาดข้อมูล (ลบเครื่องหมายลูกน้ำ และช่องว่างที่อาจติดมา)
        map_df[x_col] = map_df[x_col].astype(str).str.replace(',', '').str.strip()
        map_df[y_col] = map_df[y_col].astype(str).str.replace(',', '').str.strip()
        
        # แปลงข้อมูลเป็นตัวเลขและตัดค่าว่างทิ้ง
        map_df[x_col] = pd.to_numeric(map_df[x_col], errors='coerce')
        map_df[y_col] = pd.to_numeric(map_df[y_col], errors='coerce')
        map_df = map_df.dropna(subset=[x_col, y_col])
        
        if not map_df.empty:
            map_df = map_df.rename(columns={y_col: 'latitude', x_col: 'longitude'})
            
            # ยุบรวมพิกัดที่ซ้ำกันของลูกค้าคนเดียวกัน และคำนวณสถานะการแนะนำ
            color_col = None
            color_map = None
            hover_data = ["amt_invoice"] if "amt_invoice" in map_df.columns else None
            
            if customer_col and 'amt_invoice' in map_df.columns and 'kwh_total' in map_df.columns:
                agg_dict = {
                    'latitude': ('latitude', 'first'),
                    'longitude': ('longitude', 'first'),
                    'total_kwh': ('kwh_total', 'sum'),
                    'total_amt': ('amt_invoice', 'sum'),
                    'bill_count': ('kwh_total', 'count')
                }
                if 'user_type_name' in map_df.columns:
                    agg_dict['user_type'] = ('user_type_name', 'first')
                    
                map_summary = map_df.groupby(customer_col).agg(**agg_dict).reset_index()
                
                # คำนวณความคุ้มค่าแบบเดียวกับตารางด้านล่าง
                map_summary['ค่าไฟเฉลี่ย/เดือน'] = (map_summary['total_amt'] / map_summary['bill_count']).round(2)
                avg_kwh = map_summary['total_kwh'] / map_summary['bill_count']
                
                def get_map_day_ratio(u_type):
                    u_str = str(u_type)
                    if "บ้าน" in u_str: return 0.5
                    elif "กิจการ" in u_str: return 0.7
                    else: return 0.85
                map_summary['day_ratio'] = map_summary['user_type'].apply(get_map_day_ratio) if 'user_type' in map_summary.columns else 0.85
                actual_kw = np.ceil((avg_kwh * map_summary['day_ratio'] / 120) / 0.55) * 0.55
                avg_rate = np.where(avg_kwh > 0, map_summary['ค่าไฟเฉลี่ย/เดือน'] / avg_kwh, 4.5)
                solar_produced = actual_kw * (120 * 0.931) # หักประสิทธิภาพฝุ่นเมฆ (ให้ตรงกับช่องค้นหา)
                kwh_saved = np.minimum(solar_produced, avg_kwh)
                monthly_savings = np.minimum(kwh_saved * avg_rate, map_summary['ค่าไฟเฉลี่ย/เดือน'])
                
                # อิงราคาเงินลงทุนตามขนาดแพ็กเกจจริง
                inv_conds = [actual_kw <= 3, actual_kw <= 5, actual_kw <= 10, actual_kw <= 15]
                inv_vals = [145000, 200000, 329000, 454900]
                investment_map = np.select(inv_conds, inv_vals, default=np.maximum(550000, actual_kw * 27500))
                
                payback_years = np.where(monthly_savings > 0, investment_map / (monthly_savings * 12), 99)
                
                map_summary['payback_years'] = payback_years
                
                def eval_map_status(row):
                    if row['payback_years'] > 7:
                        return "ยังไม่คุ้มทุน"
                    
                    avg_bill = row['ค่าไฟเฉลี่ย/เดือน']
                    u_type = str(row.get('user_type', ''))
                    
                    if "ชั่วคราว" in u_type:
                        return "ยังไม่คุ้มทุน"
                    
                    if "กิจการขนาดใหญ่" in u_type:
                        if avg_bill >= 30000: return "ควรติด (กิจการขนาดใหญ่)"
                    elif "กิจการขนาดกลาง" in u_type:
                        if avg_bill >= 15000: return "ควรติด (กิจการขนาดกลาง)"
                    else:
                        # บ้านอยู่อาศัย, กิจการขนาดเล็ก, กิจการเฉพาะอย่าง หรืออื่นๆ
                        if avg_bill >= 3000: return "ควรติด (บ้าน/ขนาดเล็ก)"
                        
                    return "ยังไม่คุ้มทุน"
                    
                map_summary['สถานะ'] = map_summary.apply(eval_map_status, axis=1)

                # --- ประเมินโอกาสปิดการขายสูง (Hot Leads) สำหรับแผนที่ ---
                map_summary['monthly_savings'] = monthly_savings
                cost_vals_map = [actual_kw * 35000, actual_kw * 28000, actual_kw * 24000, actual_kw * 22000]
                cost_map = np.select(inv_conds, cost_vals_map, default=actual_kw * 20000)
                map_summary['company_profit'] = investment_map - cost_map
                
                def eval_map_hot_lead(row):
                    if row['สถานะ'] == "ยังไม่คุ้มทุน" or row['company_profit'] <= 0: 
                        return False
                    score = 0
                    if row['payback_years'] <= 4.5: score += 3
                    elif row['payback_years'] <= 5.5: score += 2
                    elif row['payback_years'] <= 6.5: score += 1
                    if row['monthly_savings'] >= 5000: score += 3
                    elif row['monthly_savings'] >= 3000: score += 2
                    elif row['monthly_savings'] >= 1500: score += 1
                    return score >= 5
                    
                map_summary['is_hot_lead'] = map_summary.apply(eval_map_hot_lead, axis=1)
                
                # เตรียมข้อมูลเพิ่มเติมสำหรับแสดงตอนชี้เมาส์ (Hover)
                map_summary['ประเภทผู้ใช้ไฟ'] = map_summary.get('user_type', 'ไม่ระบุ')
                map_summary['ค่าไฟเฉลี่ย (บาท/เดือน)'] = map_summary['ค่าไฟเฉลี่ย/เดือน']
                map_summary['ค่าไฟเฉลี่ยหลังติด (บาท/เดือน)'] = (map_summary['ค่าไฟเฉลี่ย/เดือน'] - monthly_savings).round(2)
                map_summary['คืนทุน (ปี)'] = np.round(payback_years, 1)
                map_summary['โอกาสปิดการขาย'] = np.where(map_summary['is_hot_lead'], "🔥 สูงมาก (Hot Lead)", "ทั่วไป")

                # กรองให้เหลือเฉพาะเป้าหมายที่ควรเสนอโครงการ (ควรติดโซล่าร์เซลล์)
                map_summary = map_summary[map_summary['สถานะ'] != "ยังไม่คุ้มทุน"]
                if show_only_hot_leads:
                    map_summary = map_summary[map_summary['is_hot_lead']]

                map_df = map_summary
                color_col = 'สถานะ'
                color_map = {
                    "ควรติด (บ้าน/ขนาดเล็ก)": "#00E676", 
                    "ควรติด (กิจการขนาดกลาง)": "#D500F9", 
                    "ควรติด (กิจการขนาดใหญ่)": "#2979FF"  
                }
                # ซ่อน Latitude และ Longitude จาก Hover
                hover_data = {
                    "latitude": False,
                    "longitude": False,
                    "ประเภทผู้ใช้ไฟ": True,
                    "ค่าไฟเฉลี่ย (บาท/เดือน)": True,
                    "ค่าไฟเฉลี่ยหลังติด (บาท/เดือน)": True,
                    "คืนทุน (ปี)": True,
                    "โอกาสปิดการขาย": True
                }

            # ตรวจสอบว่าพิกัดเป็น Lat/Lon ที่สลับแกนกันมาหรือไม่ (X ควรเป็น Lon ~100, Y ควรเป็น Lat ~13)
            if (map_df['longitude'].abs() < 200).all() and (map_df['latitude'].abs() < 200).all():
                if map_df['longitude'].mean() < map_df['latitude'].mean():
                    # สลับแกนให้ถูกต้องอัตโนมัติ
                    map_df['latitude'], map_df['longitude'] = map_df['longitude'].copy(), map_df['latitude'].copy()
                is_utm = False
            else:
                # ถ้ามีค่าเกิน 200 แสดงว่าเป็นระบบพิกัด UTM แน่นอน
                is_utm = True
            
            if is_utm:
                try:
                    from pyproj import Transformer
                    # ใช้ EPSG code สำหรับ UTM Zone 47N (ครอบคลุมพื้นที่ส่วนใหญ่ของไทย) อัตโนมัติ
                    transformer = Transformer.from_crs("epsg:32647", "epsg:4326", always_xy=True)
                    map_df['longitude'], map_df['latitude'] = transformer.transform(
                        map_df['longitude'].values, 
                        map_df['latitude'].values
                    )
                    st.success("ระบบตรวจพบพิกัด UTM และได้แปลงเป็นพิกัดบนแผนที่สากล (Lat/Lon) อัตโนมัติ")
                except ImportError:
                    st.error("พบพิกัดรูปแบบ UTM แต่ไม่สามารถแสดงแผนที่ได้เนื่องจากขาดเครื่องมือแปลงพิกัด (`pyproj`)")
                    st.info("**วิธีแก้ไข:** ให้เปิด Terminal แล้วพิมพ์คำสั่ง `python -m pip install pyproj` จากนั้นกด Refresh หน้าเว็บ")
            
            # กรองให้เหลือเฉพาะพิกัดในประเทศไทย (Lat: 5-21, Lon: 97-106) เพื่อป้องกันแผนที่ซูมออกไปที่อื่น
            valid_map = map_df[(map_df['latitude'].between(5, 21)) & (map_df['longitude'].between(97, 106))]
            
            if not valid_map.empty:
                # ใช้ Plotly เพื่อวาดแผนที่แบบมีรายละเอียดภาพถ่ายถนน (OpenStreetMap) 
                fig_map = px.scatter_mapbox(
                    valid_map, 
                    lat="latitude", 
                    lon="longitude", 
                    hover_name=customer_col if customer_col else None,
                    hover_data=hover_data,
                    color=color_col,
                    color_discrete_map=color_map,
                    color_discrete_sequence=["#FF5722"] if not color_col else None,
                    center={"lat": 13.7367, "lon": 100.5231}, # บังคับให้แผนที่โฟกัสที่ประเทศไทยเป็นหลัก
                    zoom=5, height=550
                )
                fig_map.update_layout(
                    mapbox_style="open-street-map", 
                    margin={"r":0,"t":0,"l":0,"b":0},
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(
                        title_text="", 
                        bgcolor="rgba(255,255,255,0.8)",
                        yanchor="top", 
                        y=0.98, 
                        xanchor="left", 
                        x=0.02
                    )
                )
                st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True, "displayModeBar": False})
                
                if len(valid_map) < len(map_df):
                    st.warning(f"ซ่อนจุดพิกัด {len(map_df) - len(valid_map):,} จุด เนื่องจากอยู่นอกเขตประเทศไทย หรือพิกัดผิดพลาด")
            else:
                st.info("ไม่มีจุดพิกัดบนแผนที่ (ไม่มีลูกค้าเข้าเกณฑ์ 'ควรติดโซล่าร์เซลล์' หรือข้อมูลพิกัดผิดพลาด)")
        else:
            st.warning(f"พบคอลัมน์เป้าหมาย ({x_col}, {y_col}) แต่ไม่สามารถแปลงให้เป็นตัวเลขพิกัดได้เลย")
            st.write("ตัวอย่างข้อมูลดิบ (Raw Data):", filtered_df[[x_col, y_col]].head())
    else:
        st.info("ไม่พบคอลัมน์พิกัด X (คอลัมน์ G) และ Y (คอลัมน์ H) ในชุดข้อมูล")

    st.divider()

    # --- ค้นหารายบุคคล ---
    st.subheader("ค้นหาพฤติกรรมการใช้ไฟฟ้ารายบุคคล")
    st.markdown("*(ค้นหาหมายเลขผู้ใช้ไฟเพื่อดูกราฟค่าไฟรายเดือนของลูกค้ารายนั้นๆ)*")

    if customer_col:
        # ดึงรายการหมายเลขผู้ใช้ไฟทั้งหมดตามลำดับที่ปรากฏในไฟล์
        customer_list = list(filtered_df[customer_col].dropna().astype(str).unique())
        
        # คำนวณสถานะความคุ้มค่าคร่าวๆ เพื่อใช้ทำสัญลักษณ์ใน Dropdown
        quick_summary = filtered_df.groupby(customer_col).agg(
            avg_amt=('amt_invoice', 'mean'),
            avg_kwh=('kwh_total', 'mean'),
            user_type=('user_type_name', 'first')
        ).reset_index()
        
        def eval_quick_status(row):
            avg_amt = row['avg_amt']
            avg_kwh = row['avg_kwh']
            if pd.isna(avg_kwh) or avg_kwh <= 0 or pd.isna(avg_amt): 
                return False
            
            u_type = str(row['user_type'])
            if "ชั่วคราว" in u_type:
                return False
                
            if "กิจการขนาดใหญ่" in u_type and avg_amt < 30000: return False
            if "กิจการขนาดกลาง" in u_type and avg_amt < 15000: return False
            if "กิจการขนาดใหญ่" not in u_type and "กิจการขนาดกลาง" not in u_type and avg_amt < 3000: return False

            day_r = 0.5 if "บ้าน" in u_type else (0.7 if "กิจการ" in u_type else 0.85)
            
            target_kw = (avg_kwh * day_r) / 120
            panels = np.ceil(target_kw / 0.55) if target_kw > 0 else 0
            actual_kw = panels * 0.55
            avg_rate = avg_amt / avg_kwh if avg_kwh > 0 else 4.5
            
            # ใช้ประสิทธิภาพ 93.1% เสมือนถูกหักลบจากสภาพอากาศเริ่มต้น เพื่อให้ตรงกับรายละเอียดด้านใน
            solar_produced = actual_kw * (120 * 0.931)
            kwh_saved = min(solar_produced, avg_kwh)
            monthly_savings = min(kwh_saved * avg_rate, avg_amt)
            investment = 145000 if actual_kw <= 3 else (200000 if actual_kw <= 5 else (329000 if actual_kw <= 10 else (454900 if actual_kw <= 15 else max(550000, actual_kw * 27500))))
            payback = investment / (monthly_savings * 12) if monthly_savings > 0 else 99
            
            return payback <= 7

        quick_summary['should_install'] = quick_summary.apply(eval_quick_status, axis=1)
        recommended_customers = set(quick_summary[quick_summary['should_install']][customer_col].astype(str))
        not_recommended_customers = set(quick_summary[~quick_summary['should_install']][customer_col].astype(str))
        
        if len(customer_list) > 0:
            # --- เพิ่มตัวกรองสถานะลูกค้า ---
            filter_search_status = st.radio(
                "ตัวกรองสถานะการแนะนำ:",
                options=["แสดงทั้งหมด", "✅ ควรติด", "❌ ยังไม่คุ้ม"],
                horizontal=True
            )
            
            # กรองรายการหมายเลขผู้ใช้ไฟตามตัวกรองที่เลือก
            display_customer_list = []
            for cust in customer_list:
                if filter_search_status == "✅ ควรติด" and cust in recommended_customers:
                    display_customer_list.append(cust)
                elif filter_search_status == "❌ ยังไม่คุ้ม" and cust in not_recommended_customers:
                    display_customer_list.append(cust)
                elif filter_search_status == "แสดงทั้งหมด":
                    display_customer_list.append(cust)

            # ฟังก์ชันสำหรับจัดรูปแบบข้อความในช่องค้นหา (เพิ่มสัญลักษณ์สี)
            def format_customer_display(cust_no):
                if cust_no == "-- โปรดเลือกหมายเลขผู้ใช้ไฟ --":
                    return cust_no
                if cust_no in recommended_customers:
                    return f"✅ {cust_no} (ควรติด)"
                elif cust_no in not_recommended_customers:
                    return f"❌ {cust_no} (ยังไม่คุ้ม)"
                return f"⚪ {cust_no} (ไม่มีข้อมูล)"

            # ใช้ selectbox ซึ่งสามารถคลิกแล้วพิมพ์ค้นหาตัวเลขได้เลย
            selected_customer = st.selectbox(
                "พิมพ์เพื่อค้นหาหรือเลือกหมายเลขผู้ใช้ไฟ:", 
                options=["-- โปรดเลือกหมายเลขผู้ใช้ไฟ --"] + display_customer_list,
                format_func=format_customer_display
            )
            
            if selected_customer != "-- โปรดเลือกหมายเลขผู้ใช้ไฟ --":
                # กรองข้อมูลเฉพาะลูกค้ารายนี้
                cust_df = filtered_df[filtered_df[customer_col].astype(str) == selected_customer].copy()
                
                # สร้าง label สำหรับแกน X และจัดเรียงเดือน-ปีให้ถูกต้อง
                cust_df['period_label'] = cust_df['year'].astype(str) + "-" + cust_df['month'].astype(str)
                cust_df = cust_df.sort_values(by=['year', 'month'])
                
                # คำนวณสรุปข้อมูลเบื้องต้นของลูกค้ารายนี้
                cust_total_amt = cust_df['amt_invoice'].sum()
                cust_avg_amt = cust_df['amt_invoice'].mean()
                cust_max_amt = cust_df['amt_invoice'].max()
                
                scol1, scol2, scol3 = st.columns(3)
                scol1.metric("ค่าไฟฟ้ารวมตลอดช่วง", f"฿ {cust_total_amt:,.2f}")
                scol2.metric("ค่าไฟฟ้าเฉลี่ยต่อเดือน", f"฿ {cust_avg_amt:,.2f}")
                scol3.metric("ค่าไฟสูงสุดที่เคยจ่าย", f"฿ {cust_max_amt:,.2f}")
                
                # --- เพิ่มข้อมูลและรายละเอียดเชิงลึกของลูกค้ารายบุคคล ---
                st.markdown("#### รายละเอียดและคำแนะนำการติดตั้งโซล่าร์เซลล์ (เฉพาะราย)")
                
                cust_avg_kwh = cust_df['kwh_total'].mean()
                user_type = cust_df['user_type_name'].iloc[0] if 'user_type_name' in cust_df.columns else "ไม่ระบุ"
                
                # 1. หาระยะเวลาใช้งานกลางวัน
                if "บ้าน" in str(user_type): day_r = 0.5
                elif "กิจการ" in str(user_type): day_r = 0.7
                else: day_r = 0.85
                
                # 2. ดึงพิกัดและข้อมูลสิ่งแวดล้อม (Real-time) สำหรับลูกค้ารายนี้
                x_col = 'x_coord' if 'x_coord' in cust_df.columns else (cust_df.columns[6] if len(cust_df.columns) >= 8 else None)
                y_col = 'y_coord' if 'y_coord' in cust_df.columns else (cust_df.columns[7] if len(cust_df.columns) >= 8 else None)
                
                lat, lon = 0.0, 0.0
                if x_col and y_col:
                    try:
                        x_val = pd.to_numeric(str(cust_df[x_col].iloc[0]).replace(',', '').strip())
                        y_val = pd.to_numeric(str(cust_df[y_col].iloc[0]).replace(',', '').strip())
                        if abs(x_val) > 200:
                            from pyproj import Transformer
                            t = Transformer.from_crs("epsg:32647", "epsg:4326", always_xy=True)
                            lon, lat = t.transform(x_val, y_val)
                        else:
                            lat = x_val if x_val < y_val else y_val
                            lon = y_val if x_val < y_val else x_val
                    except:
                        pass
                
                pm25, cloud = 20.0, 20.0
                if lat != 0.0 and lon != 0.0:
                    try:
                        owm_api_key = "0f5d49af1e876c2b86df0df789f5f02b"
                        aqi_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={owm_api_key}"
                        w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={owm_api_key}"
                        req_aqi = requests.get(aqi_url, timeout=5)
                        req_w = requests.get(w_url, timeout=5)
                        if req_aqi.status_code == 200:
                            pm25 = float(req_aqi.json().get('list', [{}])[0].get('components', {}).get('pm2_5', 20.0))
                        if req_w.status_code == 200:
                            cloud = float(req_w.json().get('clouds', {}).get('all', 20.0))
                    except:
                        pass
                        
                d_imp = min(pm25 / 10, 15.0)
                l_imp = min(cloud / 4, 25.0)
                eff_factor = (1 - (d_imp / 100)) * (1 - (l_imp / 100))
                kwh_per_kw = 120 * eff_factor
                
                # 3. คำนวณความคุ้มค่า
                target_kw = (cust_avg_kwh * day_r) / 120
                panels = np.ceil(target_kw / 0.55) if target_kw > 0 else 0
                actual_kw = panels * 0.55
                avg_rate = cust_avg_amt / cust_avg_kwh if cust_avg_kwh > 0 else 4.5
                
                solar_produced = actual_kw * kwh_per_kw
                kwh_saved = min(solar_produced, cust_avg_kwh)
                monthly_savings = min(kwh_saved * avg_rate, cust_avg_amt)
                
                if actual_kw <= 3:
                    investment = 145000
                    company_cost = actual_kw * 35000
                elif actual_kw <= 5:
                    investment = 200000
                    company_cost = actual_kw * 28000
                elif actual_kw <= 10:
                    investment = 329000
                    company_cost = actual_kw * 24000
                elif actual_kw <= 15:
                    investment = 454900
                    company_cost = actual_kw * 22000
                else:
                    investment = max(550000, actual_kw * 27500)
                    company_cost = actual_kw * 20000
                
                company_profit = investment - company_cost
                
                payback = investment / (monthly_savings * 12) if monthly_savings > 0 else 99
                
                if cust_avg_amt >= 3000 and payback <= 7:
                    status_text = "ควรติดโซล่าร์เซลล์ (คุ้มทุนเหมาะสม)"
                    status_color = "#dcfce7"
                    status_font = "#166534"
                else:
                    status_text = "ยังไม่แนะนำ (ใช้ไฟน้อยไปหรือคืนทุนช้า)"
                    status_color = "#fee2e2"
                    status_font = "#991b1b"
                
                # แสดงผล UI
                dcol1, dcol2, dcol3, dcol4 = st.columns(4)
                with dcol1:
                    with st.container(border=True):
                        st.markdown(f"<div style='text-align:center'><b>ขนาดติดตั้งแนะนำ</b><br><span style='font-size: 1.2em; color: #0369a1;'>{actual_kw:,.2f} kW</span><br>({int(panels)} แผง)</div>", unsafe_allow_html=True)
                with dcol2:
                    with st.container(border=True):
                        st.markdown(f"<div style='text-align:center'><b>คาดการณ์ประหยัดเงิน</b><br><span style='font-size: 1.2em; color: #15803d;'>฿ {monthly_savings:,.2f}</span><br>ต่อเดือน</div>", unsafe_allow_html=True)
                with dcol3:
                    with st.container(border=True):
                        st.markdown(f"<div style='text-align:center'><b>ระยะเวลาคืนทุน</b><br><span style='font-size: 1.2em; color: #b45309;'>{payback:,.1f} ปี</span><br>(ลงทุน ฿ {investment:,.0f} | กำไร ฿ {company_profit:,.0f})</div>", unsafe_allow_html=True)
                with dcol4:
                    with st.container(border=True):
                        st.markdown(f"<div style='text-align:center'><b>สภาพแวดล้อม (Real-Time)</b><br><span style='font-size: 0.75em; color: #6b7280;'>พิกัด: {lat:.4f}, {lon:.4f}</span><br><span style='font-size: 0.9em; color: #6b7280;'>ฝุ่น PM2.5: {pm25:.1f} μg/m³<br>ความเข้มแสง: {100 - cloud:.0f}%</span></div>", unsafe_allow_html=True)

                st.markdown(f'''
                <div style="background-color: {status_color}; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                    <strong style="color: {status_font}; font-size: 16px;">สถานะการประเมิน: {status_text}</strong>
                </div>
                ''', unsafe_allow_html=True)
                
                # --- ส่วนแสดงเปรียบเทียบ ก่อน-หลัง (Before & After) ---
                kwh_after = cust_avg_kwh - kwh_saved
                amt_after = cust_avg_amt - monthly_savings
                
                st.markdown("##### เปรียบเทียบก่อนและหลังติดตั้ง (หักลบผลกระทบฝุ่นและเมฆแล้ว)")
                c1, c2, c3 = st.columns(3)
                with c1:
                    with st.container(border=True):
                        st.info(f"**ก่อนติดตั้ง (เฉลี่ยเดิม)**\n\nใช้ไฟ: **{cust_avg_kwh:,.2f}** หน่วย/เดือน\n\nค่าไฟ: **฿ {cust_avg_amt:,.2f}** /เดือน")
                with c2:
                    with st.container(border=True):
                        st.success(f"**โซล่าร์เซลล์ช่วยลดได้**\n\nลดการใช้ไฟ: **{kwh_saved:,.2f}** หน่วย/เดือน\n\nประหยัดเงิน: **฿ {monthly_savings:,.2f}** /เดือน")
                with c3:
                    with st.container(border=True):
                        st.warning(f"**หลังติดตั้ง (ต้องจ่ายการไฟฟ้า)**\n\nเหลือการใช้ไฟ: **{max(0, kwh_after):,.2f}** หน่วย/เดือน\n\nจ่ายค่าไฟ: **฿ {max(0, amt_after):,.2f}** /เดือน")
                        
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("ดูรายการคำนวณทีละขั้นตอน 9 ข้อ (อิงจากหน่วยไฟและค่าไฟจริงของลูกค้ารายนี้)"):
                    pkg_rec = "3 kW" if actual_kw <= 3 else "5 kW" if actual_kw <= 5 else "10 kW" if actual_kw <= 10 else "15 kW" if actual_kw <= 15 else ">15 kW"
                    produced_before = actual_kw * 120
                    lost_kwh = produced_before - solar_produced
                    
                    st.markdown(f"""
                    **ข้อมูลตั้งต้นของลูกค้ารายนี้:**
                    - การใช้ไฟเฉลี่ย (`kwh_total`): **{cust_avg_kwh:,.2f} หน่วย/เดือน**
                    - ค่าไฟเฉลี่ย (`amt_invoice`): **{cust_avg_amt:,.2f} บาท/เดือน**
                    - อัตราค่าไฟเฉลี่ย: **{avg_rate:,.2f} บาท/หน่วย**
                    - สภาพแวดล้อม ณ พิกัดบ้าน ({lat:.4f}, {lon:.4f}): ฝุ่น PM2.5 = {pm25:.1f} (ลดทอน {d_imp:.1f}%), ความเข้มแสง = {100 - cloud:.0f}% (เมฆลดทอน {l_imp:.1f}%)

                    **ผลการคำนวณ 9 ขั้นตอน:**
                    1. **ขนาดระบบโซลาร์เซลล์ที่เหมาะสม:** ขั้นต่ำ `{target_kw:,.2f} kW` *(ประเมินให้ครอบคลุมการใช้ไฟกลางวัน {day_r*100:.0f}%)*
                    2. **จำนวนแผงที่ต้องใช้:** `{int(panels)} แผง` *(แผงละ 550W รวมได้ขนาดติดตั้งจริง = {actual_kw:,.2f} kW)*
                    3. **พลังงานที่ผลิตได้ต่อเดือน (ก่อนหักผลกระทบ):** `{produced_before:,.2f} kWh` *(คิดจาก 120 หน่วย/kW)*
                    4. **พลังงานที่ผลิตได้ (หลังหักฝุ่นและสภาพอากาศ):** `{solar_produced:,.2f} kWh`
                    5. **สูญเสียพลังงานจากฝุ่นและเมฆ:** `{lost_kwh:,.2f} kWh`
                    6. **ประหยัดค่าไฟได้:** `{monthly_savings:,.2f} บาท/เดือน`
                    7. **ควรเลือกแพ็กเกจขนาด:** `แพ็กเกจ {pkg_rec}`
                    8. **ระยะเวลาคืนทุน:** `{payback:,.2f} ปี` *(อิงจากยอดเงินลงทุนประมาณ {investment:,.0f} บาท)*
                    9. **เปรียบเทียบก่อนและหลัง:** ค่าไฟเดิม `฿ {cust_avg_amt:,.2f}` ➔ ประหยัดได้ `฿ {monthly_savings:,.2f}` ➔ จ่ายจริง `฿ {max(0, amt_after):,.2f}`
                    """)

                # วาดกราฟแสดงค่าไฟและหน่วยการใช้ไฟของลูกค้าแต่ละเดือน
                plot_cust_data = cust_df.rename(columns={'amt_invoice': 'ค่าไฟ (บาท)', 'kwh_total': 'การใช้ไฟ (kWh)'})
                fig_cust = px.bar(
                    plot_cust_data, 
                    x='period_label', 
                    y=['ค่าไฟ (บาท)', 'การใช้ไฟ (kWh)'],
                    barmode='group',
                    text_auto='.2s',
                    title=f"ประวัติการใช้ไฟฟ้าของหมายเลข: {selected_customer}",
                    labels={'period_label': 'เดือน-ปี', 'value': 'จำนวน', 'variable': 'รายการ'}
                )
                st.plotly_chart(fig_cust, use_container_width=True)
                
                # --- เพิ่มกราฟจุดคุ้มทุน (Breakeven) ---
                if monthly_savings > 0 and payback < 99:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("##### กราฟวิเคราะห์จุดคุ้มทุน (Breakeven Analysis)")
                    
                    # คำนวณคาดการณ์ไปข้างหน้า (Project ไปจนถึง ปีที่คุ้มทุน + 5 ปี หรืออย่างน้อย 10 ปี)
                    proj_years = max(10, int(payback) + 5)
                    months_arr = np.arange(0, (proj_years * 12) + 1)
                    years_arr = months_arr / 12.0
                    
                    # สะสมค่าไฟเดิม (ไม่ติดโซล่าร์)
                    cost_cumulative_before = cust_avg_amt * months_arr
                    # สะสมต้นทุนใหม่ (ค่าติดตั้ง + ค่าไฟที่เหลือหลังติด)
                    cost_cumulative_after = investment + (max(0, amt_after) * months_arr)
                    
                    fig_breakeven = go.Figure()
                    
                    # เส้นค่าไฟก่อนติด
                    fig_breakeven.add_trace(go.Scatter(
                        x=years_arr, y=cost_cumulative_before,
                        mode='lines', name='จ่ายค่าไฟปกติ (ไม่ติดโซล่าร์)',
                        line=dict(color='#ef4444', width=3)
                    ))
                    
                    # เส้นต้นทุนหลังติด
                    fig_breakeven.add_trace(go.Scatter(
                        x=years_arr, y=cost_cumulative_after,
                        mode='lines', name='ต้นทุนสะสม (ลงทุนโซล่าร์ + ค่าไฟที่เหลือ)',
                        line=dict(color='#22c55e', width=3)
                    ))
                    
                    # จุดตัด (จุดคุ้มทุน)
                    intersect_y = cust_avg_amt * (payback * 12)
                    
                    # เส้นประชี้พิกัดจุดตัดจากแกน X และ Y
                    fig_breakeven.add_trace(go.Scatter(
                        x=[0, payback, payback], 
                        y=[intersect_y, intersect_y, 0],
                        mode='lines', 
                        line=dict(color='#9ca3af', width=1.5, dash='dash'),
                        showlegend=False, hoverinfo='skip'
                    ))
                    
                    fig_breakeven.add_trace(go.Scatter(
                        x=[payback], y=[intersect_y],
                        mode='markers+text', name='จุดคุ้มทุน',
                        marker=dict(color='#f59e0b', size=14, symbol='star', line=dict(width=2, color='white')),
                        text=[f'<b>จุดคุ้มทุน: {payback:.1f} ปี</b><br>ที่ยอด ฿ {intersect_y:,.0f}'],
                        textposition='top left', textfont=dict(color='#b45309')
                    ))
                    
                    fig_breakeven.update_layout(
                        title='เปรียบเทียบต้นทุนสะสม: ก่อนติด vs หลังติดโซล่าร์เซลล์',
                        xaxis_title='ระยะเวลา (ปี)', yaxis_title='ต้นทุนสะสม (บาท)',
                        hovermode='x unified', template='plotly_white',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_breakeven, use_container_width=True)
    else:
        st.warning("ไม่สามารถค้นหารายบุคคลได้ เนื่องจากไม่พบคอลัมน์หมายเลขผู้ใช้ไฟ (เช่น ca, pea_no) ในไฟล์ข้อมูล")

    st.divider()

    # --- ตารางวิเคราะห์ความคุ้มค่าการติดโซล่าร์เซลล์รายบุคคล ---
    st.subheader("วิเคราะห์ความคุ้มค่าการติดโซล่าร์เซลล์รายบ้าน (Real-Time API)")
    st.markdown("*(คำนวณความคุ้มค่าจากค่าไฟจริง พร้อมดึงข้อมูลความเข้มแสงและค่าฝุ่น PM2.5 แบบเรียลไทม์จากพิกัดของแต่ละบ้าน)*")

    if customer_col:
        # 1. จัดเตรียม Aggregation คอลัมน์
        agg_dict = {
            'total_kwh': ('kwh_total', 'sum'),
            'total_amt': ('amt_invoice', 'sum'),
            'bill_count': ('kwh_total', 'count'),
            'user_type_name': ('user_type_name', 'first')
        }
        
        x_col = 'x_coord' if 'x_coord' in filtered_df.columns else (filtered_df.columns[6] if len(filtered_df.columns) >= 8 else None)
        y_col = 'y_coord' if 'y_coord' in filtered_df.columns else (filtered_df.columns[7] if len(filtered_df.columns) >= 8 else None)
        
        if x_col and y_col:
            agg_dict['x_val'] = (x_col, 'first')
            agg_dict['y_val'] = (y_col, 'first')

        # สร้างตารางข้อมูลรายลูกค้า
        cust_summary = filtered_df.groupby(customer_col).agg(**agg_dict).reset_index()

        # 2. จัดการข้อมูลพิกัดเพื่อนำไปใช้ดึง API
        if 'x_val' in cust_summary.columns and 'y_val' in cust_summary.columns:
            cust_summary['x_val'] = pd.to_numeric(cust_summary['x_val'].astype(str).str.replace(',', '').str.strip(), errors='coerce')
            cust_summary['y_val'] = pd.to_numeric(cust_summary['y_val'].astype(str).str.replace(',', '').str.strip(), errors='coerce')
            
            # ตรวจสอบและแปลง UTM หรือสลับ Lat/Lon
            if (cust_summary['x_val'].abs() > 200).any():
                try:
                    from pyproj import Transformer
                    transformer = Transformer.from_crs("epsg:32647", "epsg:4326", always_xy=True)
                    cust_summary['longitude'], cust_summary['latitude'] = transformer.transform(
                        cust_summary['x_val'].values,
                        cust_summary['y_val'].values
                    )
                except:
                    cust_summary['longitude'], cust_summary['latitude'] = cust_summary['x_val'], cust_summary['y_val']
            else:
                cust_summary['latitude'] = np.where(cust_summary['x_val'] < cust_summary['y_val'], cust_summary['x_val'], cust_summary['y_val'])
                cust_summary['longitude'] = np.where(cust_summary['x_val'] < cust_summary['y_val'], cust_summary['y_val'], cust_summary['x_val'])
            
            # ลดความละเอียดพิกัด (ทศนิยม 1 ตำแหน่ง = รัศมี ~11 กิโลเมตร) เพื่อลดจำนวนการดึง API ซ้ำซ้อนและป้องกันโดนบล็อก
            cust_summary['lat_r'] = cust_summary['latitude'].round(1)
            cust_summary['lon_r'] = cust_summary['longitude'].round(1)
        else:
            cust_summary['lat_r'] = np.nan
            cust_summary['lon_r'] = np.nan

        # 3. ฟังก์ชันดึงข้อมูลจาก Open-Meteo API (ใช้ Cache ลดการดึงซ้ำ)
        @st.cache_data(ttl=1800) # อัปเดตทุกครึ่งชั่วโมง
        def fetch_realtime_env(coords):
            import time
            results = {}
            
            # OpenWeatherMap Free Tier จำกัดที่ 60 requests/minute (1 req/sec)
            # จำกัดจุดที่ไม่ซ้ำกันให้ไม่เกิน 25 จุด เพื่อไม่ให้รอนานและไม่โดนบล็อก
            if len(coords) > 25:
                coords = coords[:25]
                
            # เปลี่ยนมาใช้การวนลูปปกติแทน Parallel เพื่อควบคุม Rate Limit อย่างเคร่งครัด
            for lat, lon in coords:
                try:
                    time.sleep(1.1) # หน่วงเวลา 1.1 วินาที เพื่อไม่ให้เกิน 60 ครั้ง/นาที
                    owm_api_key = "0f5d49af1e876c2b86df0df789f5f02b"
                    aqi_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={owm_api_key}"
                    w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={owm_api_key}"
                    
                    req_aqi = requests.get(aqi_url, timeout=5)
                    req_w = requests.get(w_url, timeout=5)
                    
                    pm25 = 20.0
                    if req_aqi.status_code == 200:
                        data_aqi = req_aqi.json()
                        if 'list' in data_aqi and len(data_aqi['list']) > 0:
                            pm25 = float(data_aqi['list'][0].get('components', {}).get('pm2_5', 20.0))
                            
                    cloud = 20.0
                    if req_w.status_code == 200:
                        cloud = float(req_w.json().get('clouds', {}).get('all', 20.0))
                    
                    results[(lat, lon)] = {'pm25': pm25, 'cloud': cloud}
                except:
                    results[(lat, lon)] = {'pm25': 20.0, 'cloud': 20.0} # ค่าเริ่มต้นกรณี API Error
                    
            return results

        valid_coords = cust_summary.dropna(subset=['lat_r', 'lon_r'])[['lat_r', 'lon_r']].drop_duplicates()
        coord_list = list(zip(valid_coords['lat_r'], valid_coords['lon_r']))
        
        env_data = {}
        if coord_list:
            with st.spinner("กำลังเชื่อมต่อดาวเทียม... ดึงข้อมูลความเข้มแสงและ PM2.5 แบบ Real-Time ให้แต่ละพิกัด..."):
                env_data = fetch_realtime_env(coord_list)

        # 4. ฟังก์ชันคำนวณผลกระทบต่อแผงโซล่าร์เซลล์
        def apply_env_impact(row):
            lat, lon = row.get('lat_r'), row.get('lon_r')
            if pd.isna(lat) or pd.isna(lon): return pd.Series([20.0, 20.0, 1.3, 3.0])
            data = env_data.get((lat, lon), {'pm25': 20.0, 'cloud': 20.0})
            pm = float(data['pm25']) if data['pm25'] is not None else 20.0
            cl = float(data['cloud']) if data['cloud'] is not None else 20.0
            # อิงความสมจริง: ฝุ่น 150 AQI ลดทอนแสงประมาณ 8%, เมฆบัง 100% กระทบค่าเฉลี่ยรายเดือนสูงสุด 15%
            d_imp = min(pm / 15.0, 8.0) 
            l_imp = cl * 0.15  
            return pd.Series([pm, cl, d_imp, l_imp])

        # ผสานข้อมูลสิ่งแวดล้อมเข้าตาราง
        cust_summary[['pm25_real', 'cloud_real', 'dust_impact', 'light_impact']] = cust_summary.apply(apply_env_impact, axis=1)
        cust_summary['light_intensity'] = 100 - cust_summary['cloud_real']

        # หารด้วยจำนวนบิลเพื่อหาค่าเฉลี่ยต่อเดือนของแต่ละบ้าน
        cust_summary['avg_kwh_per_month'] = cust_summary['total_kwh'] / cust_summary['bill_count']
        cust_summary['avg_amt_per_month'] = cust_summary['total_amt'] / cust_summary['bill_count']

        def get_day_ratio(user_type):
            user_type_str = str(user_type) # แปลงเป็น string ก่อนเพื่อป้องกัน Error จากค่าว่าง
            if "บ้าน" in user_type_str:
                return 0.5
            elif "กิจการ" in user_type_str:
                return 0.7
            else:
                return 0.85
                
        cust_summary['day_ratio'] = cust_summary['user_type_name'].apply(get_day_ratio)

        def recommend_package(kw):
            if kw <= 3:
                return "3 kW"
            elif kw <= 5:
                return "5 kW"
            elif kw <= 10:
                return "10 kW"
            elif kw <= 15:
                return "15 kW"
            else:
                return ">15 kW"

        # คำนวณแบบสมจริง: ฐาน 135 kWh/kW หัก System Loss 15% และหักปัจจัยสิ่งแวดล้อม
        cust_summary['efficiency_factor'] = (1 - 0.15) * (1 - (cust_summary['dust_impact'] / 100)) * (1 - (cust_summary['light_impact'] / 100))
        cust_summary['kwh_per_kw_month_adjusted'] = 135.0 * cust_summary['efficiency_factor']

        # จำกัดเป้าหมายการติดไว้แค่ปริมาณที่ใช้ตอนกลางวัน (On-Grid)
        cust_summary['target_kwh'] = cust_summary['avg_kwh_per_month'] * cust_summary['day_ratio']
        # ใช้ 105 เป็นค่าตั้งต้นในการหาขนาด kW ที่เหมาะสม (เพื่อไม่ให้ติดตั้ง Over size)
        cust_summary['recommended_kw'] = cust_summary['target_kwh'] / 105.0

        # คำนวณจำนวนแผงและปัดขึ้นเป็นจำนวนเต็ม
        cust_summary['panels_needed'] = np.ceil(cust_summary['recommended_kw'] / 0.55)
        # ปรับขนาด kW ให้ตรงกับจำนวนแผงที่ต้องติดจริง
        cust_summary['actual_kw'] = cust_summary['panels_needed'] * 0.55
        
        cust_summary['recommended_package'] = cust_summary['actual_kw'].apply(recommend_package)
        
        # หาอัตราค่าไฟเฉลี่ยของบ้านแต่ละหลัง (บาท/หน่วย) ตามข้อมูลจริง
        cust_summary['avg_rate'] = np.where(cust_summary['avg_kwh_per_month'] > 0, 
                                            cust_summary['avg_amt_per_month'] / cust_summary['avg_kwh_per_month'], 
                                            4.5)
        
        # คำนวณหน่วยไฟที่ผลิตได้จริงและประหยัดได้ (ประหยัดได้จริงไม่เกินค่าไฟช่วงกลางวัน)
        cust_summary['solar_kwh_produced'] = cust_summary['actual_kw'] * cust_summary['kwh_per_kw_month_adjusted']
        cust_summary['kwh_saved'] = np.minimum(cust_summary['solar_kwh_produced'], cust_summary['target_kwh'])
        
        # คำนวณส่วนที่ประหยัดได้ (ผลิตได้ตามประสิทธิภาพที่ปรับแล้ว * อัตราค่าไฟ) และไม่ให้เกินค่าไฟเดิม
        cust_summary['monthly_savings'] = cust_summary['solar_kwh_produced'] * cust_summary['avg_rate']
        cust_summary['monthly_savings'] = np.minimum(cust_summary['monthly_savings'], cust_summary['avg_amt_per_month'])
        
        cust_summary['cost_after_solar'] = cust_summary['avg_amt_per_month'] - cust_summary['monthly_savings']
        
        # ราคาขายแพ็กเกจที่คิดกับลูกค้า (Investment)
        pkg_conds = [cust_summary['actual_kw'] <= 3, cust_summary['actual_kw'] <= 5, cust_summary['actual_kw'] <= 10, cust_summary['actual_kw'] <= 15]
        pkg_vals = [145000, 200000, 329000, 454900]
        cust_summary['investment'] = np.select(pkg_conds, pkg_vals, default=np.maximum(550000, cust_summary['actual_kw'] * 27500))
        
        # คำนวณต้นทุนบริษัทและกำไร (ปรับให้สมจริงตาม Economy of Scale)
        cost_vals = [cust_summary['actual_kw'] * 35000, cust_summary['actual_kw'] * 28000, cust_summary['actual_kw'] * 24000, cust_summary['actual_kw'] * 22000]
        cust_summary['company_cost'] = np.select(pkg_conds, cost_vals, default=cust_summary['actual_kw'] * 20000)
        cust_summary['company_profit'] = cust_summary['investment'] - cust_summary['company_cost']
        
        cust_summary['payback_years'] = np.where(cust_summary['monthly_savings'] > 0,
                                                 cust_summary['investment'] / (cust_summary['monthly_savings'] * 12),
                                                 99)
        
        # เงื่อนไขควรติด: ค่าไฟเฉลี่ย >= 3000 และคืนทุน <= 7 ปี (และต้องไม่ใช่ไฟฟ้าชั่วคราว)
        def eval_table_status(row):
            if row['payback_years'] > 7: return "ยังไม่คุ้ม"
            
            avg_bill = row['avg_amt_per_month']
            u_type = str(row.get('user_type_name', ''))
            actual_kw = row['actual_kw']
            payback = row['payback_years']
            
            if "ชั่วคราว" in u_type: return "ยังไม่คุ้ม"
            
            # --- 1. แยกลูกค้าที่คำนวณกำลังผลิตได้เยอะเกินพิกัดของแต่ละกลุ่ม เป็น "ลูกค้ากลุ่มพิเศษ" ---
            is_special = False
            if "บ้านอยู่อาศัย" in u_type:
                if actual_kw > 15: is_special = True
            elif "กิจการขนาดใหญ่" in u_type:
                if actual_kw > 5000: is_special = True
            else:
                # สำหรับ กิจการขนาดเล็ก/กลาง, ส่วนราชการ, อาคารพาณิชย์ ฯลฯ
                if actual_kw > 150: is_special = True
                
            if is_special:
                # ใช้อีกเกณฑ์นึงสำหรับกลุ่มพิเศษ: เช่น คืนทุนต้องไม่เกิน 6 ปี และค่าไฟต้องสูงกว่า 20,000 บาท
                if payback <= 6 and avg_bill >= 20000:
                    return "ควรติด (ลูกค้ากลุ่มพิเศษ)"
                else:
                    return "ยังไม่คุ้ม (ลูกค้ากลุ่มพิเศษ)"
            
            # --- 2. เกณฑ์ปกติสำหรับลูกค้าทั่วไป ---
            if payback > 7: return "ยังไม่คุ้ม"
            
            if "กิจการขนาดใหญ่" in u_type:
                if avg_bill >= 30000: return "ควรติด"
            elif "กิจการขนาดกลาง" in u_type:
                if avg_bill >= 15000: return "ควรติด"
            else:
                if avg_bill >= 3000: return "ควรติด"
            return "ยังไม่คุ้ม"
            
        cust_summary['should_install'] = cust_summary.apply(eval_table_status, axis=1)
        
        # จัดคอลัมน์และเปลี่ยนชื่อเพื่อแสดงผล
        display_df = cust_summary[[
            customer_col, 'user_type_name', 'should_install', 'pm25_real', 'light_intensity', 'avg_kwh_per_month', 'kwh_saved', 'avg_amt_per_month', 'monthly_savings', 'cost_after_solar',
            'actual_kw', 'recommended_package', 'panels_needed', 'investment', 'company_profit', 'payback_years'
        ]].copy()
        
        display_df = display_df.rename(columns={
            customer_col: 'หมายเลขผู้ใช้ไฟ',
            'user_type_name': 'ประเภทผู้ใช้ไฟ',
            'should_install': 'คำแนะนำ',
            'pm25_real': 'ฝุ่น PM2.5 (μg/m³)',
            'light_intensity': 'ความเข้มแสง (%)',
            'avg_kwh_per_month': 'ใช้ไฟเดิม (kWh/เดือน)',
            'kwh_saved': 'ประหยัดไฟ (kWh/เดือน)',
            'avg_amt_per_month': 'ค่าไฟเดิม (บาท/เดือน)',
            'monthly_savings': 'ประหยัดเงิน (บาท/เดือน)',
            'cost_after_solar': 'ค่าไฟสุทธิ (บาท/เดือน)',
            'actual_kw': 'ขนาดติดตั้ง (kW)',
            'recommended_package': 'แพ็กเกจที่แนะนำ',
            'panels_needed': 'จำนวนแผง (แผงละ 550W)',
            'investment': 'ราคาขายแพ็กเกจ (บาท)',
            'company_profit': 'กำไรบริษัท (บาท)',
            'payback_years': 'คืนทุน (ปี)'
        })
        
        display_df['จำนวนแผง (แผงละ 550W)'] = display_df['จำนวนแผง (แผงละ 550W)'].astype(int)
        
        # เรียงตามลำดับค่าไฟจากมากไปน้อย (รายใหญ่ขึ้นก่อน)
        display_df = display_df.sort_values(by='ค่าไฟเดิม (บาท/เดือน)', ascending=False).reset_index(drop=True)
        
        # --- สรุปภาพรวมลูกค้าที่ควรติดโซล่าร์เซลล์ ---
        total_cust = len(display_df)
        recommended_cust = len(display_df[display_df['คำแนะนำ'] == 'ควรติด'])
        # นับรวมทั้ง "ควรติด" และ "ควรติด (ลูกค้ากลุ่มพิเศษ)"
        recommended_cust = len(display_df[display_df['คำแนะนำ'].str.startswith('ควรติด')])
        pct_recommended = (recommended_cust / total_cust * 100) if total_cust > 0 else 0
        
        st.markdown("##### สรุปสัดส่วนกลุ่มเป้าหมาย (ก่อนใช้ตัวกรอง)")
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            with st.container(border=True):
                st.metric("ลูกค้าที่ประเมินทั้งหมด", f"{total_cust:,} ราย")
        with mcol2:
            with st.container(border=True):
                st.metric("ลูกค้าที่ควรติดตั้ง", f"{recommended_cust:,} ราย")
        with mcol3:
            with st.container(border=True):
                st.metric("คิดเป็นสัดส่วนเป้าหมาย", f"{pct_recommended:,.1f}%")

        with st.expander("อ่านคำอธิบาย: เกณฑ์ลูกค้าเป้าหมาย"):
            st.markdown("""
            **เกณฑ์เป้าหมายทั่วไป (ควรติดโซล่าร์เซลล์):**
            - ค่าไฟเฉลี่ยรายเดือน **>= 3,000 บาท**
            - ระยะเวลาคืนทุนประเมิน **<= 7 ปี**
            - ไม่เป็นผู้ใช้ไฟฟ้าแบบชั่วคราว
            """)

        # --- ตัวกรองข้อมูลสำหรับตาราง ---
        st.markdown("**ตัวกรองข้อมูลตาราง:**")
        
        if not display_df.empty:
            fcol1, fcol2 = st.columns(2)
            
            with fcol1:
                filter_status = st.radio(
                    "สถานะคำแนะนำ:",
                    options=["แสดงทั้งหมด", "ควรติด (รวมกลุ่มพิเศษ)", "เฉพาะลูกค้ากลุ่มพิเศษ", "ยังไม่คุ้ม"],
                    horizontal=True,
                    index=1 # ตั้งค่าเริ่มต้นให้เลือกโชว์เฉพาะ 'ควรติด' 
                )

            with fcol2:
                unique_types = display_df['ประเภทผู้ใช้ไฟ'].unique().tolist()
                filter_user_types = st.multiselect(
                    "ประเภทผู้ใช้ไฟ:",
                    options=unique_types,
                    default=unique_types
                )
            # นำตัวกรองทั้งหมดมาตัดข้อมูลในตาราง
            if filter_status == "ควรติด (รวมกลุ่มพิเศษ)":
                display_df = display_df[display_df['คำแนะนำ'].str.startswith('ควรติด')]
            elif filter_status == "เฉพาะลูกค้ากลุ่มพิเศษ":
                display_df = display_df[display_df['คำแนะนำ'].str.contains('ลูกค้ากลุ่มพิเศษ')]
            elif filter_status == "ยังไม่คุ้ม":
                display_df = display_df[display_df['คำแนะนำ'].str.startswith('ยังไม่คุ้ม')]
                
            if filter_user_types:
                display_df = display_df[display_df['ประเภทผู้ใช้ไฟ'].isin(filter_user_types)]
            
            display_df = display_df.reset_index(drop=True)

        # กรองข้อมูลเอาเฉพาะกลุ่มที่ "ควรติด" (รวมกลุ่มพิเศษ) และ "บริษัทได้กำไร"
        profitable_df = display_df[(display_df['คำแนะนำ'].str.startswith('ควรติด')) & (display_df['กำไรบริษัท (บาท)'] > 0)].copy()

        # --- เพิ่มระบบวิเคราะห์ "โอกาสปิดการขาย" (Lead Scoring) ---
        def evaluate_lead(row):
            score = 0
            # 1. คืนทุนไว ตัดสินใจง่าย (สูงสุด 3 คะแนน)
            if row['คืนทุน (ปี)'] <= 4.5: score += 3
            elif row['คืนทุน (ปี)'] <= 5.5: score += 2
            elif row['คืนทุน (ปี)'] <= 6.5: score += 1
            
            # 2. ยอดประหยัดต่อเดือนเห็นผลชัดเจน คุ้มค่า (สูงสุด 3 คะแนน)
            if row['ประหยัดเงิน (บาท/เดือน)'] >= 5000: score += 3
            elif row['ประหยัดเงิน (บาท/เดือน)'] >= 3000: score += 2
            elif row['ประหยัดเงิน (บาท/เดือน)'] >= 1500: score += 1
            
            if score >= 5: return "โอกาสสูงมาก (Hot Lead)"
            elif score >= 3: return "โอกาสปานกลาง (Warm Lead)"
            else: return "โอกาสทั่วไป (Cold Lead)"

        if not profitable_df.empty:
            profitable_df['โอกาสปิดการขาย'] = profitable_df.apply(evaluate_lead, axis=1)
            
            # จัดเรียงคอลัมน์ให้ 'โอกาสปิดการขาย' มาอยู่ถัดจาก 'คำแนะนำ'
            cols = list(profitable_df.columns)
            cols.insert(3, cols.pop(cols.index('โอกาสปิดการขาย')))
            profitable_df = profitable_df[cols]
            
            # เรียงลำดับให้ Hot Lead ขึ้นก่อน และตามด้วยกำไรบริษัทสูงสุด
            profitable_df['score_order'] = profitable_df['โอกาสปิดการขาย'].map({
                "โอกาสสูงมาก (Hot Lead)": 1, 
                "โอกาสปานกลาง (Warm Lead)": 2, 
                "โอกาสทั่วไป (Cold Lead)": 3
            })
            profitable_df = profitable_df.sort_values(by=['score_order', 'กำไรบริษัท (บาท)'], ascending=[True, False]).drop(columns=['score_order'])

        hot_leads_df = profitable_df[profitable_df['โอกาสปิดการขาย'] == "โอกาสสูงมาก (Hot Lead)"] if not profitable_df.empty else pd.DataFrame()

        st.success(f"**จำนวนบ้านที่ควรติดโซล่าร์เซลล์ทั้งหมด:** {len(display_df):,} ราย (**เป็น Hot Lead ปิดการขายได้ง่าย {len(hot_leads_df):,} ราย**)")

        # แปลงคอลัมน์ประหยัดเงินให้แสดงเป็นช่วงราคา (Range +/- 10%) พร้อมปัดเป็นเลขกลมๆ (หลักร้อย)
        def format_savings_range(val):
            if pd.isna(val) or val <= 0:
                return "฿ 0"
            min_val = round(val * 0.9, -2)
            max_val = round(val * 1.1, -2)
            return f"฿ {min_val:,.0f} - {max_val:,.0f}"

        display_df['ประหยัดเงิน (บาท/เดือน)'] = display_df['ประหยัดเงิน (บาท/เดือน)'].apply(format_savings_range)
        if not profitable_df.empty:
            profitable_df['ประหยัดเงิน (บาท/เดือน)'] = profitable_df['ประหยัดเงิน (บาท/เดือน)'].apply(format_savings_range)
        if not hot_leads_df.empty:
            hot_leads_df['ประหยัดเงิน (บาท/เดือน)'] = hot_leads_df['ประหยัดเงิน (บาท/เดือน)'].apply(format_savings_range)

        # ใช้ st.column_config เพื่อปรับแต่งตารางให้สวยงามและดูเป็นมืออาชีพมากขึ้น
        table_config = {
            "หมายเลขผู้ใช้ไฟ": st.column_config.TextColumn("หมายเลขผู้ใช้ไฟ"),
            "ประเภทผู้ใช้ไฟ": st.column_config.TextColumn("ประเภทผู้ใช้ไฟ"),
            "คำแนะนำ": st.column_config.TextColumn("คำแนะนำ"),
            "โอกาสปิดการขาย": st.column_config.TextColumn("โอกาสปิดการขาย"),
            "ฝุ่น PM2.5 (μg/m³)": st.column_config.Column("ฝุ่น PM2.5"),
            "ความเข้มแสง (%)": st.column_config.ProgressColumn("ความเข้มแสง (%)", format="%f%%", min_value=0, max_value=100),
            "ใช้ไฟเดิม (kWh/เดือน)": st.column_config.Column("ใช้ไฟเดิม (kWh/เดือน)"),
            "ประหยัดไฟ (kWh/เดือน)": st.column_config.Column("ประหยัดไฟ (kWh/เดือน)"),
            "ค่าไฟเดิม (บาท/เดือน)": st.column_config.Column("ค่าไฟเดิม"),
            "ประหยัดเงิน (บาท/เดือน)": st.column_config.TextColumn("ประหยัดเงิน (ประมาณ)"),
            "ค่าไฟสุทธิ (บาท/เดือน)": st.column_config.Column("ค่าไฟสุทธิ"),
            "ขนาดติดตั้ง (kW)": st.column_config.Column("ขนาด (kW)"),
            "แพ็กเกจที่แนะนำ": st.column_config.TextColumn("แพ็กเกจ"),
            "จำนวนแผง (แผงละ 550W)": st.column_config.Column("แผง"),
            "ราคาขายแพ็กเกจ (บาท)": st.column_config.Column("ราคาขายแพ็กเกจ"),
            "กำไรบริษัท (บาท)": st.column_config.Column("กำไรบริษัท"),
            "คืนทุน (ปี)": st.column_config.ProgressColumn("คืนทุน (ปี)", format="%.1f", min_value=0, max_value=10),
        }
        
        style_format = {
            "ฝุ่น PM2.5 (μg/m³)": "{:,.1f}",
            "ใช้ไฟเดิม (kWh/เดือน)": "{:,.0f}",
            "ประหยัดไฟ (kWh/เดือน)": "{:,.0f}",
            "ค่าไฟเดิม (บาท/เดือน)": "฿ {:,.0f}",
            "ค่าไฟสุทธิ (บาท/เดือน)": "฿ {:,.0f}",
            "ขนาดติดตั้ง (kW)": "{:,.2f}",
            "จำนวนแผง (แผงละ 550W)": "{:,.0f}",
            "ราคาขายแพ็กเกจ (บาท)": "฿ {:,.0f}",
            "กำไรบริษัท (บาท)": "฿ {:,.0f}"
        }
        
        # แยกข้อมูลลูกค้ากลุ่มพิเศษออกมา
        special_leads_df = display_df[display_df['คำแนะนำ'].str.contains('ลูกค้ากลุ่มพิเศษ', na=False)].copy()

        # สร้าง Tabs เพื่อแยกตารางการแสดงผล
        tab_all, tab_hot, tab_special, tab_sim = st.tabs([
            f"บ้านที่ควรติดทั้งหมด ({len(display_df)} ราย)", 
            f"โอกาสปิดการขายสูง ({len(hot_leads_df)} ราย)",
            f"ลูกค้ากลุ่มพิเศษ ({len(special_leads_df)} ราย)",
            f"จำลองโปรเจกต์รายใหญ่ ({len(special_leads_df)} ราย)"
        ])
        
        with tab_all:
            st.dataframe(display_df.style.format(style_format), column_config=table_config, hide_index=True, use_container_width=True)
            # --- ส่วนปุ่ม Export ไฟล์ Excel (ทั้งหมด) ---
            st.markdown("<br>", unsafe_allow_html=True)
            if not display_df.empty:
                buffer_all = io.BytesIO()
                try:
                    with pd.ExcelWriter(buffer_all, engine='xlsxwriter') as writer:
                        display_df.to_excel(writer, index=False, sheet_name='Recommended_Targets')
                    
                    st.download_button(
                        label="ดาวน์โหลดรายชื่อบ้านที่ควรติดตั้งทั้งหมด (Excel)",
                        data=buffer_all.getvalue(),
                        file_name="Recommended_Target_Customers.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="btn_dl_all_excel"
                    )
                except ImportError:
                    csv_data_all = display_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="ดาวน์โหลดรายชื่อบ้านที่ควรติดตั้งทั้งหมด (CSV)",
                        data=csv_data_all,
                        file_name="Recommended_Target_Customers.csv",
                        mime="text/csv",
                        key="btn_dl_all_csv"
                    )
                
        with tab_hot:
            st.markdown("#### กลุ่มลูกค้าที่ 'ซื้อง่าย คืนทุนไว กำไรดี'")
            st.markdown("ลูกค้ากลุ่มนี้คือ **'กลุ่มเป้าหมายหลัก' (Hot Leads)** มีโอกาสที่เซลล์จะปิดการขายได้ง่ายที่สุด เพราะประเมินแล้วว่าลูกค้ามีระยะเวลาคืนทุนสั้นมาก (< 5 ปี) และมียอดประหยัดเงินต่อเดือนสูง ทำให้ลูกค้ารู้สึกถึงความคุ้มค่าและตัดสินใจได้ง่ายขึ้น")
            
            st.dataframe(hot_leads_df.style.format(style_format), column_config=table_config, hide_index=True, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if not hot_leads_df.empty:
                buffer_hot = io.BytesIO()
                try:
                    with pd.ExcelWriter(buffer_hot, engine='xlsxwriter') as writer:
                        hot_leads_df.to_excel(writer, index=False, sheet_name='Hot_Leads')
                    
                    st.download_button(
                        label="ดาวน์โหลดรายชื่อ Hot Leads (Excel)",
                        data=buffer_hot.getvalue(),
                        file_name="Hot_Leads_Target_Customers.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        key="btn_dl_hot_excel"
                    )
                except ImportError:
                    csv_data_hot = hot_leads_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="ดาวน์โหลดรายชื่อ Hot Leads (CSV)",
                        data=csv_data_hot,
                        file_name="Hot_Leads_Target_Customers.csv",
                        mime="text/csv",
                        type="primary",
                        key="btn_dl_hot_csv"
                    )
            else:
                st.info("ไม่มีข้อมูลลูกค้ากลุ่ม Hot Leads ในขณะนี้")
                
        with tab_special:
            st.markdown("#### กลุ่มลูกค้ารายใหญ่ (ลูกค้ากลุ่มพิเศษ)")
            st.markdown("ลูกค้ากลุ่มนี้คือลูกค้าที่คำนวณแล้วต้องใช้แผงโซล่าร์เซลล์จำนวนมากเกินกว่าพิกัดทั่วไป ซึ่งถือเป็นโปรเจกต์ขนาดใหญ่ที่น่าสนใจสำหรับการเข้าไปนำเสนอขาย")
            
            st.dataframe(special_leads_df.style.format(style_format), column_config=table_config, hide_index=True, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if not special_leads_df.empty:
                buffer_special = io.BytesIO()
                try:
                    with pd.ExcelWriter(buffer_special, engine='xlsxwriter') as writer:
                        special_leads_df.to_excel(writer, index=False, sheet_name='Special_Customers')
                    
                    st.download_button(
                        label="ดาวน์โหลดรายชื่อลูกค้ากลุ่มพิเศษ (Excel)",
                        data=buffer_special.getvalue(),
                        file_name="Special_Target_Customers.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        key="btn_dl_special_excel"
                    )
                except ImportError:
                    csv_data_special = special_leads_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="ดาวน์โหลดรายชื่อลูกค้ากลุ่มพิเศษ (CSV)",
                        data=csv_data_special,
                        file_name="Special_Target_Customers.csv",
                        mime="text/csv",
                        type="primary",
                        key="btn_dl_special_csv"
                    )
            else:
                st.info("ไม่มีข้อมูลลูกค้ากลุ่มพิเศษในขณะนี้")
                
        with tab_sim:
            st.markdown("#### 🏢 ตารางจำลองขนาดโครงการ (ข้อจำกัดพื้นที่/หม้อแปลง)")
            st.markdown("""
            เพื่อป้องกันไม่ให้ระบบประเมินขนาดแผงออกมา **โอเวอร์จนเกินไป (Over-sized)** ตารางนี้จึงนำลูกค้ารายใหญ่มาจำลองด้วย **ขนาดที่เหมาะสมกับความเป็นจริง** มากที่สุด:
            1. **บ้านพักอาศัย:** จำกัดสูงสุดไม่เกิน 15 kW (~30 แผง) ตามขนาดหลังคาทั่วไปและข้อจำกัด กฟภ. (3 เฟส)
            2. **อาคารพาณิชย์ / SME / โรงเรียน:** จำกัดสูงสุดไม่เกิน 150 kW (~300 แผง)
            3. **โรงงานอุตสาหกรรมขนาดใหญ่:** จำกัดสูงสุดไม่เกิน 5,000 kW หรือ 5 MW (~9,000 แผง)
            """)
            
            if not special_leads_df.empty:
                # ดึงข้อมูลตั้งต้น (cust_summary) มาเพื่อคำนวณใหม่
                sim_raw_df = cust_summary[cust_summary[customer_col].isin(special_leads_df['หมายเลขผู้ใช้ไฟ'])].copy()
                
                # 1. ฟังก์ชันจำกัดเพดานขนาดติดตั้ง (Capping)
                def apply_realistic_cap(row):
                    u_type = str(row['user_type_name'])
                    calc_kw = row['actual_kw']
                    
                    if "บ้าน" in u_type:
                        max_kw = 15.0
                    elif "กิจการขนาดใหญ่" in u_type:
                        max_kw = 5000.0
                    else:
                        max_kw = 150.0
                        
                    capped_kw = min(calc_kw, max_kw)
                    panels = np.ceil(capped_kw / 0.55)
                    return panels * 0.55, panels

                sim_raw_df[['capped_kw', 'capped_panels']] = sim_raw_df.apply(
                    lambda row: apply_realistic_cap(row), axis=1, result_type='expand'
                )
                
                # 2. คำนวณไฟที่ผลิตได้และส่วนประหยัดใหม่
                sim_raw_df['solar_kwh_produced'] = sim_raw_df['capped_kw'] * sim_raw_df['kwh_per_kw_month_adjusted']
                sim_raw_df['kwh_saved'] = np.minimum(sim_raw_df['solar_kwh_produced'], sim_raw_df['avg_kwh_per_month'])
                
                sim_raw_df['monthly_savings'] = sim_raw_df['solar_kwh_produced'] * sim_raw_df['avg_rate']
                sim_raw_df['monthly_savings'] = np.minimum(sim_raw_df['monthly_savings'], sim_raw_df['avg_amt_per_month'])
                
                sim_raw_df['cost_after_solar'] = sim_raw_df['avg_amt_per_month'] - sim_raw_df['monthly_savings']
                
                # 3. คำนวณราคาโปรเจกต์ EPC Rate 
                def get_project_investment(kw):
                    if kw <= 3: return 145000
                    elif kw <= 5: return 200000
                    elif kw <= 10: return 329000
                    elif kw <= 15: return 454900
                    elif kw <= 150: return kw * 26000
                    else: return kw * 24000
                    
                def get_project_cost(kw):
                    if kw <= 15: return kw * 22000
                    elif kw <= 150: return kw * 19000
                    else: return kw * 17000
                
                sim_raw_df['investment'] = sim_raw_df['capped_kw'].apply(get_project_investment)
                sim_raw_df['company_cost'] = sim_raw_df['capped_kw'].apply(get_project_cost)
                sim_raw_df['company_profit'] = sim_raw_df['investment'] - sim_raw_df['company_cost']
                
                sim_raw_df['payback_years'] = np.where(sim_raw_df['monthly_savings'] > 0,
                                                       sim_raw_df['investment'] / (sim_raw_df['monthly_savings'] * 12),
                                                       99)
                
                def recommend_package_sim(kw):
                    if kw <= 15: return f"{kw:.0f} kW"
                    elif kw <= 150: return "EPC <150kW"
                    else: return "EPC Mega Project"
                sim_raw_df['recommended_package'] = sim_raw_df['capped_kw'].apply(recommend_package_sim)
                
                sim_raw_df['should_install'] = "✅ ควรติด (สมจริง)"

                sim_display_df = sim_raw_df[[
                    customer_col, 'user_type_name', 'should_install', 'pm25_real', 'light_intensity', 
                    'avg_kwh_per_month', 'kwh_saved', 'avg_amt_per_month', 'monthly_savings', 'cost_after_solar',
                    'capped_kw', 'recommended_package', 'capped_panels', 'investment', 'company_profit', 'payback_years'
                ]].copy()

                sim_display_df = sim_display_df.rename(columns={
                    customer_col: 'หมายเลขผู้ใช้ไฟ',
                    'user_type_name': 'ประเภทผู้ใช้ไฟ',
                    'should_install': 'คำแนะนำ',
                    'pm25_real': 'ฝุ่น PM2.5 (μg/m³)',
                    'light_intensity': 'ความเข้มแสง (%)',
                    'avg_kwh_per_month': 'ใช้ไฟเดิม (kWh/เดือน)',
                    'kwh_saved': 'ประหยัดไฟ (kWh/เดือน)',
                    'avg_amt_per_month': 'ค่าไฟเดิม (บาท/เดือน)',
                    'monthly_savings': 'ประหยัดเงิน (บาท/เดือน)',
                    'cost_after_solar': 'ค่าไฟสุทธิ (บาท/เดือน)',
                    'capped_kw': 'ขนาดติดตั้ง (kW)',
                    'recommended_package': 'แพ็กเกจที่แนะนำ',
                    'capped_panels': 'จำนวนแผง (แผงละ 550W)',
                    'investment': 'ราคาขายแพ็กเกจ (บาท)',
                    'company_profit': 'กำไรบริษัท (บาท)',
                    'payback_years': 'คืนทุน (ปี)'
                })
                
                sim_display_df['จำนวนแผง (แผงละ 550W)'] = sim_display_df['จำนวนแผง (แผงละ 550W)'].astype(int)
                sim_display_df['ประหยัดเงิน (บาท/เดือน)'] = sim_display_df['ประหยัดเงิน (บาท/เดือน)'].apply(format_savings_range)
                sim_display_df = sim_display_df.sort_values(by='กำไรบริษัท (บาท)', ascending=False).reset_index(drop=True)
                
                st.dataframe(sim_display_df.style.format(style_format), column_config=table_config, hide_index=True, use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                buffer_sim = io.BytesIO()
                try:
                    with pd.ExcelWriter(buffer_sim, engine='xlsxwriter') as writer:
                        sim_display_df.to_excel(writer, index=False, sheet_name='Simulated_Projects')
                    
                    st.download_button(
                        label="ดาวน์โหลดตารางจำลองโปรเจกต์ (Excel)",
                        data=buffer_sim.getvalue(),
                        file_name="Simulated_Projects.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        key="btn_dl_sim_excel"
                    )
                except ImportError:
                    csv_data_sim = sim_display_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="ดาวน์โหลดตารางจำลองโปรเจกต์ (CSV)",
                        data=csv_data_sim,
                        file_name="Simulated_Projects.csv",
                        mime="text/csv",
                        type="primary",
                        key="btn_dl_sim_csv"
                    )
            else:
                st.info("ไม่มีข้อมูลลูกค้ากลุ่มพิเศษที่เข้าเกณฑ์ในขณะนี้")
        
        st.caption("""
        **สมมติฐานการคำนวณแบบอิงค่าความเป็นจริง (Realistic Simulation):**
            - ประเมินให้ระบบโซลาร์เซลล์ขนาดเหมาะสม **ครอบคลุมเฉพาะการใช้ไฟช่วงกลางวัน** ป้องกันไฟเหลือทิ้งแบบ On-Grid (บ้านอยู่อาศัย 50%, กิจการ 70%, อื่นๆ 85%)
            - ใช้แผงโซลาร์เซลล์ขนาด 550W (0.55 kW)
            - 1 kW ผลิตไฟฟ้าอุดมคติได้ **135 หน่วย/เดือน** (อิงแดดเฉลี่ยไทย 4.5 ชม./วัน) 
            - หักค่า **System Loss ถาวร 15%** (การสูญเสียในสายไฟ/อินเวอร์เตอร์)
            - หักผลกระทบจากฝุ่นและเมฆแบบ Real-Time (ดึงค่าเฉลี่ยฝุ่นและเมฆมาประเมินการบดบังแสงให้สมจริงยิ่งขึ้น) ทำให้ค่าผลิตจริงจะเฉลี่ยอยู่ที่ราวๆ 100-110 หน่วย/เดือน
        - **ราคาติดตั้งอ้างอิงจาก PEA Solar (Standard Package):**
            - ขนาดไม่เกิน 3 kW: ~48,333 บาท/kW (แพ็กเกจ 145,000 บาท)
            - ขนาด 3 - 5 kW: 40,000 บาท/kW (แพ็กเกจ 200,000 บาท)
            - ขนาด 5 - 10 kW: 32,900 บาท/kW (แพ็กเกจ 329,000 บาท)
          - ขนาด 10 - 15 kW: ~30,326 บาท/kW (แพ็กเกจ 454,900 บาท)
          - ขนาด 15 kW ขึ้นไป: 27,500 บาท/kW (แพ็กเกจ 550,000 บาท)
        - **เกณฑ์แนะนำให้ติด (ต้องคืนทุนไม่เกิน 7 ปี):** 
          - บ้านอยู่อาศัย / กิจการขนาดเล็ก / กิจการเฉพาะอย่าง: ค่าไฟเฉลี่ย >= 3,000 บาท/เดือน
          - กิจการขนาดกลาง (SME): ค่าไฟเฉลี่ย >= 15,000 บาท/เดือน
          - กิจการขนาดใหญ่: ค่าไฟเฉลี่ย >= 30,000 บาท/เดือน
        """)
    else:
        st.warning("ไม่สามารถประเมินได้เนื่องจากไม่พบคอลัมน์หมายเลขผู้ใช้ไฟในไฟล์ข้อมูล")


else:
    import os
    st.warning(f"ไม่พบข้อมูล กรุณาตรวจสอบว่ามีไฟล์ CSV หรือ ZIP ในโฟลเดอร์เดียวกับสคริปต์หรือไม่\n\n(กำลังค้นหาที่โฟลเดอร์: `{os.path.abspath('.')}`)")  