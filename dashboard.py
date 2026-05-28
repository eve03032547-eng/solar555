import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import sys
import subprocess
import os

# ตรวจสอบว่ารันผ่าน Streamlit หรือไม่ ถ้าไม่ใช่ (เช่น กดปุ่ม Run ปกติ) ให้รัน streamlit อัตโนมัติ
if not st.runtime.exists():
    print("🚀 กำลังเปิดหน้าเว็บ Streamlit อัตโนมัติ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", sys.argv[0]])
    sys.exit(0)

from read_all_csv import read_all_csv_in_directory, process_pea_data

# ตั้งค่าหน้าจอ Dashboard
st.set_page_config(page_title="Solar Cell Sales Platform", page_icon="☀️", layout="wide")

# --- เมนูนำทาง (Sidebar Navigation) ---
st.sidebar.title("🧭 เมนูนำทาง")
page = st.sidebar.radio(
    "เลือกหน้าต่างการใช้งาน:", 
    ["🏠 หน้าแรก (ข้อมูลบริการและแพ็กเกจ)", "📊 แดชบอร์ดวิเคราะห์", "🎯 ค้นหาลูกค้าเป้าหมาย", "🧮 คำนวณโซล่าร์เซลล์ (ด้วยตัวเอง)", "🏦 บริการด้านสินเชื่อ"]
)
st.sidebar.divider()

# ฟังก์ชันสำหรับค้นหาไฟล์รูปภาพ ทั้งหน้าแรกและโฟลเดอร์ย่อย (รองรับทั้งตอนรันในเครื่องและบน Cloud)
def get_image_path(file_name, default_folder=""):
    if os.path.exists(file_name):
        return file_name
    elif os.path.exists(os.path.join(default_folder, file_name)):
        return os.path.join(default_folder, file_name)
    return file_name

# ฟังก์ชันแปลงรูปภาพในเครื่องเป็น Base64 เพื่อให้แทรกลง HTML ได้
import base64
def get_base64_image(file_name, folder_name="Logo"):
    image_path = get_image_path(file_name, folder_name)
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()
            ext = image_path.split('.')[-1].lower()
            mime = 'jpeg' if ext == 'jpg' else ext
            return f"data:image/{mime};base64,{b64}"
    return ""

# ==========================================
# ส่วนที่ 5: หน้าบริการด้านสินเชื่อ
# ==========================================
if page == "🏦 บริการด้านสินเชื่อ":
    st.title("🏦 บริการด้านสินเชื่อสำหรับติดตั้งโซล่าร์เซลล์")
    st.markdown("*(ข้อมูลผลิตภัณฑ์สินเชื่อโครงการ PEA SOLAR จากสถาบันการเงินพันธมิตร เพื่อสนับสนุนการเข้าถึงพลังงานสะอาด)*")
    
    st.image("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=1200&auto=format&fit=crop", use_container_width=True)
    
    st.markdown("""
    การไฟฟ้าส่วนภูมิภาค (PEA) ได้ร่วมมือกับ **6 สถาบันการเงินชั้นนำของประเทศ** เพื่อให้บริการด้านสินเชื่อสำหรับการติดตั้งระบบผลิตไฟฟ้าจากพลังงานแสงอาทิตย์บนหลังคา (Solar Rooftop) 
    ช่วยลดภาระการลงทุนก้อนแรก ทำให้คุณเป็นเจ้าของระบบโซล่าร์เซลล์ได้ง่ายขึ้น ด้วยอัตราดอกเบี้ยพิเศษและระยะเวลาผ่อนชำระที่ยาวนาน คุ้มค่ากับเงินที่ประหยัดได้จากค่าไฟในแต่ละเดือน
    """)
    st.divider()

    # ฟังก์ชันสำหรับค้นหาไฟล์รูปภาพ ทั้งหน้าแรกและโฟลเดอร์ย่อย (รองรับทั้งตอนรันในเครื่องและบน Cloud)
    def get_image_path(file_name, default_folder=""):
        if os.path.exists(file_name):
            return file_name
        elif os.path.exists(os.path.join(default_folder, file_name)):
            return os.path.join(default_folder, file_name)
        return file_name

    # ฟังก์ชันแปลงรูปภาพในเครื่องเป็น Base64 เพื่อให้แทรกลง HTML ได้
    import base64
    def get_base64_image(file_name, folder_name="Logo"):
        image_path = get_image_path(file_name, folder_name)
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                b64 = base64.b64encode(img_file.read()).decode()
                ext = image_path.split('.')[-1].lower()
                mime = 'jpeg' if ext == 'jpg' else ext
                return f"data:image/{mime};base64,{b64}"
        return ""

    # แบ่งเป็น 2 แท็บ: สำหรับบ้านพักอาศัย และ สำหรับภาคธุรกิจ
    tab1, tab2 = st.tabs(["🏠 สินเชื่อสำหรับบ้านพักอาศัย", "🏢 สินเชื่อสำหรับภาคธุรกิจ (SME & Corporate)"])
    
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
                st.link_button("🌐 ดูรายละเอียดบนเว็บไซต์", "https://www.kasikornbank.com/th/personal/loan/home-loan/pages/solar-rooftop.aspx", use_container_width=True)
        with c2:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #0284c7; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('กรุงเทพ.jpg')}' height='30'> ธนาคารกรุงเทพ</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อบัวหลวงพูนผลกรีน**")
                st.markdown("- **วงเงินกู้สูงสุด:** 10 ล้านบาท")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 30 ปี")
                st.markdown("- **จุดเด่น:** อัตราดอกเบี้ยพิเศษตลอดอายุสัญญา (ประมาณ 5.78% - 6.13% ต่อปี) เพื่อปรับปรุงบ้านและประหยัดพลังงาน")
                st.link_button("🌐 ดูรายละเอียดบนเว็บไซต์", "https://www.bangkokbank.com/th-TH/Personal/My-Home/Bualuang-Poonpol-Green-Loan", use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #0f172a; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('uob.png')}' height='25'> ธนาคารยูโอบี</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อบ้านรักษ์โลก U-Green**")
                st.markdown("- **วงเงินกู้สูงสุด:** 50 ล้านบาท")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 30 ปี")
                st.markdown("- **จุดเด่น:** สินเชื่อบ้านแลกเงิน (Green Cash to Home) หรือรีไฟแนนซ์ (Green Top Up) ดอกเบี้ยเฉลี่ย 3 ปีแรกเริ่มต้น 3.49%")
                st.link_button("🌐 ดูรายละเอียดบนเว็บไซต์", "https://www.uob.co.th/personal/loans/home-loan/u-green.page", use_container_width=True)
        with c4:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #db2777; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('ออมสิน.jpg')}' height='30'> ธนาคารออมสิน</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อ GSB Green Home Loan**")
                st.markdown("- **วงเงินกู้สูงสุด:** 110% (รวมซื้อบ้าน/ตกแต่ง)")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 40 ปี")
                st.markdown("- **จุดเด่น:** สนับสนุนสินเชื่อดอกเบี้ยต่ำเพื่อที่อยู่อาศัยประหยัดพลังงาน เป็นมิตรกับสิ่งแวดล้อม")
                st.link_button("🌐 ดูรายละเอียดบนเว็บไซต์", "https://www.gsb.or.th/promotions/gsb-green-home-loan/", use_container_width=True)

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
                st.link_button("🌐 ดูรายละเอียดบนเว็บไซต์", "https://www.kasikornbank.com/th/business/sme/loan/solar-rooftop/pages/index.aspx", use_container_width=True)
        with b2:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #ea580c; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('ttb.png')}' height='25'> ทีเอ็มบีธนชาต (ttb)</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อธุรกิจเพื่อสิ่งแวดล้อม**")
                st.markdown("- **วงเงินกู้สูงสุด:** 100% ของมูลค่าการติดตั้ง")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 8 ปี")
                st.markdown("- **จุดเด่น:** สนับสนุนผู้ประกอบการมุ่งสู่เศรษฐกิจคาร์บอนต่ำ ช่วยประหยัดต้นทุนค่าไฟอย่างยั่งยืน")
                st.link_button("🌐 ดูรายละเอียดบนเว็บไซต์", "https://www.ttbbank.com/th/sme/sme-loan/business-loan/sme-green-loan", use_container_width=True)

        b3, b4 = st.columns(2)
        with b3:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #ca8a04; display: flex; align-items: center; gap: 8px;'><img src='{get_base64_image('sme.png')}' height='30'> SME D Bank</h3>", unsafe_allow_html=True)
                st.markdown("**สินเชื่อ SME Green Productivity**")
                st.markdown("- **วงเงินกู้สูงสุด:** 10 ล้านบาท")
                st.markdown("- **ระยะเวลาผ่อน:** นานสูงสุด 10 ปี")
                st.markdown("- **จุดเด่น:** อัตราดอกเบี้ยต่ำเพียง 3% ต่อปี คงที่ 3 ปีแรก เพื่อยกระดับและเพิ่มผลิตภาพธุรกิจสีเขียว")
                st.link_button("🌐 ดูรายละเอียดบนเว็บไซต์", "https://www.smebank.co.th/products/sme-green-productivity/", use_container_width=True)
        with b4:
             with st.container(border=True):
                st.markdown("### 💡 สนใจขอรับบริการสินเชื่อ")
                st.markdown("ลูกค้าที่สนใจสามารถแจ้งความประสงค์ผ่านสำนักงานการไฟฟ้าส่วนภูมิภาค (PEA) ที่ดูแลโครงการ หรือติดต่อสาขาของธนาคารพันธมิตรทั่วประเทศ")
                st.info("เงื่อนไขการอนุมัติสินเชื่อ วงเงิน และอัตราดอกเบี้ย เป็นไปตามที่แต่ละธนาคารกำหนด")
                st.link_button("🌐 ดูข้อมูลโครงการ PEA SOLAR หน้าหลัก", "https://peasolar.pea.co.th/", use_container_width=True)

    st.divider()
    
    # เพิ่มเครื่องคำนวณยอดผ่อนชำระเบื้องต้น
    st.subheader("🧮 เครื่องคำนวณยอดผ่อนชำระสินเชื่อเบื้องต้น")
    st.markdown("*(ประเมินค่างวดรายเดือนแบบลดต้นลดดอก (Effective Rate) เพื่อเปรียบเทียบกับค่าไฟที่ประหยัดได้)*")
    
    calc_col1, calc_col2 = st.columns([1, 1])
    with calc_col1:
        with st.container(border=True):
            loan_amount = st.number_input("💵 วงเงินที่ต้องการกู้ (ราคาแพ็กเกจ)", min_value=10000, max_value=5000000, value=200000, step=10000)
            interest_rate = st.number_input("📈 อัตราดอกเบี้ยเฉลี่ย (% ต่อปี)", min_value=0.0, max_value=20.0, value=5.5, step=0.1)
            loan_years = st.number_input("🗓️ ระยะเวลาผ่อนชำระ (ปี)", min_value=1, max_value=40, value=7, step=1)
            
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
            st.markdown(f"- 🏦 ยอดเงินต้น: **฿ {loan_amount:,.0f}**")
            st.markdown(f"- 💸 ดอกเบี้ยรวมตลอดสัญญา: **฿ {total_interest:,.0f}**")
            st.markdown(f"- 📋 ยอดชำระรวมทั้งหมด: **฿ {total_payment:,.0f}**")
            
            st.info("💡 **ทริค:** นำ 'ยอดผ่อนชำระนี้' ไปเทียบกับ 'ค่าไฟที่ประหยัดได้' หากยอดผ่อนน้อยกว่าค่าไฟที่ลดได้ แสดงว่าคุณได้กำไรตั้งแต่เดือนแรกที่ติดตั้ง!")
    
    st.stop() # 🛑 บล็อกโค้ดตรงนี้เด็ดขาด ไม่ให้โค้ดส่วนค้นหาเป้าหมายหรือแผนที่ข้างล่างทำงานได้
# ==========================================
# ส่วนที่ 4: หน้าคำนวณโซล่าร์เซลล์จากเครื่องใช้ไฟฟ้า (แยกออกมาให้ทำงานอิสระได้)
# ==========================================
if page == "🧮 คำนวณโซล่าร์เซลล์ (ด้วยตัวเอง)":
    st.title("🧮 คำนวณขนาดโซล่าร์เซลล์ที่เหมาะสมจากเครื่องใช้ไฟฟ้า")
    st.markdown("*(คำนวณขนาดแผงโซล่าร์เซลล์ On-Grid จากจำนวนและชั่วโมงการเปิดใช้งานเครื่องใช้ไฟฟ้าในช่วงเวลากลางวัน)*")
    
    st.info("💡 **คำแนะนำ:** ให้กรอกเฉพาะชั่วโมงการใช้งานในช่วงที่ **มีแสงแดด (ประมาณ 08:00 - 17:00 น.)** เท่านั้น เนื่องจากระบบไม่มีแบตเตอรี่สำรองไฟ")
    
    appliances = [
        {"name": "❄️ แอร์ 9,000 BTU", "watts": 800, "qty": 0, "hrs": 0.0},
        {"name": "❄️ แอร์ 12,000 BTU", "watts": 1000, "qty": 0, "hrs": 0.0},
        {"name": "❄️ แอร์ 18,000 BTU", "watts": 1500, "qty": 0, "hrs": 0.0},
        {"name": "🧊 ตู้เย็น (ทำงานตลอดวัน)", "watts": 150, "qty": 1, "hrs": 8.0},
        {"name": "📺 ทีวี", "watts": 100, "qty": 0, "hrs": 0.0},
        {"name": "💻 คอมพิวเตอร์ / โน้ตบุ๊ก", "watts": 200, "qty": 0, "hrs": 0.0},
        {"name": "💡 หลอดไฟ", "watts": 15, "qty": 0, "hrs": 0.0},
        {"name": "🌀 พัดลม", "watts": 50, "qty": 0, "hrs": 0.0},
        {"name": "👕 เครื่องซักผ้า", "watts": 400, "qty": 0, "hrs": 0.0},
        {"name": "💧 ปั๊มน้ำ", "watts": 300, "qty": 0, "hrs": 0.0},
        {"name": "🔌 อื่นๆ (ระบุกำลังไฟรวม)", "watts": 100, "qty": 0, "hrs": 0.0},
    ]
    
    total_daily_wh = 0
    
    # หัวตาราง
    cols = st.columns([3, 2, 2, 2])
    cols[0].write("**เครื่องใช้ไฟฟ้า**")
    cols[1].write("**กำลังไฟ (วัตต์)**")
    cols[2].write("**จำนวน (เครื่อง)**")
    cols[3].write("**ใช้งานกลางวัน (ชม.)**")
    st.markdown("<hr style='margin-top: 0; margin-bottom: 10px;'>", unsafe_allow_html=True)
    
    # แถวรับข้อมูล
    for i, app in enumerate(appliances):
        row = st.columns([3, 2, 2, 2])
        row[0].markdown(f"<div style='padding-top: 10px;'>{app['name']}</div>", unsafe_allow_html=True)
        # รับค่า input หากเป็น "อื่นๆ" ให้แก้ค่า W ได้
        if "อื่นๆ" in app['name']:
            custom_w = row[1].number_input(f"w_{i}", min_value=0, max_value=10000, value=app['watts'], step=100, label_visibility="collapsed")
            app['watts'] = custom_w
        else:
            row[1].markdown(f"<div style='padding-top: 10px; color: #6b7280;'>~ {app['watts']} W</div>", unsafe_allow_html=True)
            
        qty = row[2].number_input(f"qty_{i}", min_value=0, max_value=100, value=app['qty'], label_visibility="collapsed")
        hrs = row[3].number_input(f"hrs_{i}", min_value=0.0, max_value=12.0, value=app['hrs'], step=0.5, label_visibility="collapsed")
        
        total_daily_wh += (app['watts'] * qty * hrs)
        
    total_daily_kwh = total_daily_wh / 1000
    
    st.divider()
    st.subheader("📊 ผลการประเมินและขนาดที่แนะนำ")
    
    # 1 kW แผงโซล่าร์เซลล์ ผลิตไฟได้ประมาณ 4 หน่วย (kWh) ต่อวัน
    recommended_kw = total_daily_kwh / 4.0
    
    if recommended_kw > 0:
        def rec_pkg(kw):
            if kw <= 3: return "3 kW", 145000
            elif kw <= 5: return "5 kW", 200000
            elif kw <= 10: return "10 kW", 329000
            elif kw <= 15: return "15 kW", 454900
            else: return ">15 kW", 550000
        
        pkg_name, pkg_price = rec_pkg(recommended_kw)
        
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            with st.container(border=True):
                st.metric("⚡ การใช้ไฟกลางวันรวม", f"{total_daily_kwh:,.1f} หน่วย/วัน")
        with rc2:
            with st.container(border=True):
                st.metric("🎯 ขนาดติดตั้งขั้นต่ำที่ต้องการ", f"{recommended_kw:,.2f} kW")
        with rc3:
            with st.container(border=True):
                st.metric("📦 แพ็กเกจที่ครอบคลุม", f"{pkg_name}")
        
        st.success(f"✅ จากพฤติกรรมการใช้งานของคุณ ขอแนะนำให้พิจารณา **แพ็กเกจ {pkg_name}** (ราคาประเมิน ฿ {pkg_price:,.0f})")
        
        st.info('''
        **💡 หลักการคำนวณเบื้องต้น:**
        - **สูตรคำนวณ:** `หน่วยไฟรวม (kWh) ÷ 4 ชั่วโมง (แสงแดดเฉลี่ย/วัน)`
        - ในประเทศไทย แผงโซล่าร์เซลล์ขนาด 1 kW สามารถผลิตกระแสไฟฟ้าได้เฉลี่ยวันละ 4 หน่วย (ครอบคลุม Loss แล้ว)
        - ตัวเลขนี้เป็นเพียงการประเมินเบื้องต้นสำหรับการติดระบบ On-Grid เพื่อลดค่าไฟกลางวันเท่านั้น
        ''')
    else:
        st.warning("⚠️ กรุณาระบุจำนวนเครื่องใช้ไฟฟ้าและชั่วโมงการเปิดใช้งาน เพื่อเริ่มต้นการคำนวณ")
        
    st.stop() # 🛑 บล็อกโค้ดตรงนี้เด็ดขาด ไม่ให้โค้ดส่วนค้นหาเป้าหมายหรือแผนที่ข้างล่างทำงานได้

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
    if page == "🏠 หน้าแรก (ข้อมูลบริการและแพ็กเกจ)":
        st.title("☀️ บริการติดตั้งระบบโซล่าร์เซลล์ครบวงจร (Solar Cell)")
        # รูปภาพหน้าปก (Banner) แผงโซล่าร์เซลล์จาก Unsplash
        st.image("https://images.unsplash.com/photo-1509391366360-1e9e0344d21e?q=80&w=1200&auto=format&fit=crop", use_container_width=True)
        st.markdown("---")
        st.subheader("💡 ลงทุนวันนี้ เพื่อลดต้นทุนค่าไฟในระยะยาว")
        st.markdown("""
        **ทำไมถึงควรติดตั้งโซล่าร์เซลล์?**
        - 💸 **ลดค่าไฟทันที:** ประหยัดค่าไฟฟ้าในเวลากลางวันได้สูงสุดถึง 60%
        - ♻️ **พลังงานสะอาด:** ช่วยลดปริมาณคาร์บอนและส่งเสริมภาพลักษณ์ที่ดี (ESG) ให้กับธุรกิจของคุณ
        - 📈 **คุ้มทุนไว:** ระยะเวลาคืนทุนเฉลี่ยเพียง 3-6 ปี (ขึ้นอยู่กับปริมาณการใช้ไฟฟ้า)
        - 🛡️ **รับประกันยาวนาน:** แผงโซล่าร์เซลล์คุณภาพสูง รับประกันประสิทธิภาพนานถึง 25 ปี
        """)
        st.divider()
        
        st.subheader("📦 แพ็กเกจการติดตั้งมาตรฐาน (ราคาโดยประมาณ)")
        
        # ใส่ CSS เพื่อตกแต่ง st.container ให้เป็นรูปแบบการ์ด (Card) ที่มีเอฟเฟกต์ตอนเอาเมาส์ชี้แบบ 3 มิติ
        st.markdown("""
        <style>
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px;
            background-color: #ffffff;
            /* เพิ่มเงาหลายชั้น ทั้งด้านนอกและด้านในเพื่อสร้างความลึก 3 มิติ */
            box-shadow: 
                0 8px 15px rgba(0,0,0,0.08), 
                0 3px 6px rgba(0,0,0,0.04), 
                inset 0 2px 4px rgba(255,255,255,0.8), 
                inset 0 -3px 5px rgba(0,0,0,0.04);
            border: 1px solid #f0f0f0;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* เอฟเฟกต์เด้งแบบสปริงนิดๆ */
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            /* ขยับการ์ดให้ลอยขึ้นและขยายขนาดเล็กน้อย */
            transform: translateY(-8px) scale(1.02);
            box-shadow: 
                0 15px 25px rgba(0,0,0,0.15), 
                0 10px 10px rgba(0,0,0,0.05), 
                inset 0 2px 4px rgba(255,255,255,0.9), 
                inset 0 -3px 5px rgba(0,0,0,0.04);
            border-color: #e2e8f0;
        }
        /* รองรับ Dark Mode ให้การ์ดกลมกลืน */
        @media (prefers-color-scheme: dark) {
            [data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #1e1e1e;
                border-color: #333333;
                box-shadow: 
                    0 8px 15px rgba(0,0,0,0.3), 
                    inset 0 1px 2px rgba(255,255,255,0.1), 
                    inset 0 -3px 5px rgba(0,0,0,0.3);
            }
            [data-testid="stVerticalBlockBorderWrapper"]:hover {
                box-shadow: 
                    0 15px 25px rgba(0,0,0,0.5), 
                    inset 0 1px 2px rgba(255,255,255,0.15), 
                    inset 0 -3px 5px rgba(0,0,0,0.3);
                border-color: #444444;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # ฟังก์ชันสำหรับเปิดหน้าต่าง Modal/Dialog แสดงรายละเอียดแพ็กเกจแบบกว้าง
        @st.dialog("📋 รายละเอียดแพ็กเกจการติดตั้ง", width="large")
        def show_details(pkg_name, size, price, details, models=None, panel_models=None):
            st.markdown(f"## {pkg_name} ({size})")
            st.subheader(f"💵 ราคาเริ่มต้นประมาณ: {price}")
            st.divider()
            st.markdown("### 🔧 อุปกรณ์และบริการที่รวมในแพ็กเกจ:")
            st.markdown(details)
            
            # --- ส่วนแสดงรูปภาพแผงโซล่าร์เซลล์ ---
            if panel_models:
                st.divider()
                st.markdown("### ☀️ เลือกรุ่นแผงโซล่าร์เซลล์ Tier 1 (รวมในแพ็กเกจ):")
                p_cols = st.columns(len(panel_models))
                for i, p_model in enumerate(panel_models):
                    with p_cols[i]:
                        with st.container(border=True):
                            if 'image' in p_model:
                                if os.path.exists(p_model['image']):
                                    st.image(p_model['image'], use_container_width=True)
                                else:
                                    st.warning(f"⚠️ ไม่พบรูปภาพ: {p_model['image']}")
                            st.markdown(f"""
                            <div style="background-color: #F3F4F6; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; border: 2px dashed #D8B4FE;">
                                <div style="font-size: 40px; margin-bottom: 5px;">🔆</div>
                                <div style="font-size: 16px; font-weight: bold; color: #4C1D95;">{p_model['name']}</div>
                                <div style="color: #6B7280; font-size: 12px; margin-top: 5px;">แผงคุณภาพสูง (Tier 1)</div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"เลือกแผง {p_model['name']}", key=f"select_panel_{pkg_name}_{i}", use_container_width=True):
                                st.success(f"✅ สนใจแผงโซล่าร์เซลล์รุ่น {p_model['name']}")

            # --- ส่วนแสดงรูปภาพอินเวอร์เตอร์ / มิตเตอร์แต่ละรุ่น ---
            if models:
                st.divider()
                st.markdown("### 🔌 เลือกรุ่นอินเวอร์เตอร์ / สมาร์ทมิเตอร์ (ราคาตามแพ็กเกจ):")
                cols = st.columns(len(models))
                for i, model in enumerate(models):
                    with cols[i]:
                        with st.container(border=True):
                            if 'image' in model:
                                if os.path.exists(model['image']):
                                    st.image(model['image'], use_container_width=True)
                                else:
                                    st.warning(f"⚠️ ไม่พบรูปภาพ: {model['image']}")
                            st.markdown(f"""
                            <div style="background-color: #F8FAFC; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; border: 2px dashed #93C5FD;">
                                <div style="font-size: 40px; margin-bottom: 5px;">⚡</div>
                                <div style="font-size: 16px; font-weight: bold; color: #0369A1;">{model['name']}</div>
                                <div style="font-size: 14px; color: #0284C7; font-weight: bold; margin-top: 10px; padding: 5px; background-color: #E0F2FE; border-radius: 8px;">🏷️ {model['price']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"เลือก {model['name']}", key=f"select_{pkg_name}_{i}", use_container_width=True):
                                st.success(f"✅ คุณเลือกสนใจ {model['name']} ราคา {model['price']}")

            st.divider()
            st.info("💡 หมายเหตุ: ราคาอาจมีการเปลี่ยนแปลงขึ้นอยู่กับการประเมินหน้างาน โครงสร้างหลังคา และรุ่นอุปกรณ์ที่เลือก")

        # รายชื่อแผงโซล่าร์เซลล์มาตรฐาน (Tier 1) ที่ใช้กับทุกแพ็กเกจ
        panel_models_std = [ 
            {"name": "Jinko Tiger Pro 550W", "image": get_image_path("Jiinko_550w.jpg", "package3kW")},
            {"name": "LONGI Hi-MO 5 550W", "image": get_image_path("Longi550w.png", "package3kW")}
        ]

        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #FFD6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">🥉 แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">3 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("🏠 เหมาะสำหรับ: บ้านพักอาศัยขนาดเล็ก\n\n💵 ราคา: **145,000 บาท**\n\n*(เฉลี่ย ~48,333 ฿/kW)*")
                if st.button("🔍 ดูรายละเอียด", key="btn_s", use_container_width=True):
                    models_s = [
                        {"name": "Huawei SUN2000-3KTL-L1", "price": "145,000 บาท", "image": get_image_path("SUN2000-3KTL-L1..webp", "package3kW")},
                        {"name": "Growatt MIN 3000TL-X", "price": "135,000 บาท", "image": get_image_path("Growatt-MIN-3000-TL-X.webp", "package3kW")}
                    ]
                    show_details("แพ็กเกจ", "3 kW", "135,000 - 145,000 บาท", "- แผงโซล่าร์เซลล์ (550W) จำนวน 5-6 แผง\n- อินเวอร์เตอร์ 1 เฟส จำนวน 1 ตัว พร้อมสมาร์ทมิเตอร์\n- ฟรี! ค่าดำเนินการขออนุญาตขนานไฟกับการไฟฟ้า\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี\n- รับประกันงานติดตั้ง 1 ปี", models=models_s, panel_models=panel_models_std)
        with col2:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #E7C6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">🥈 แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">5 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("🏡 เหมาะสำหรับ: บ้านพักอาศัยขนาดกลาง-ใหญ่\n\n💵 ราคา: **200,000 บาท**\n\n*(เฉลี่ย ~40,000 ฿/kW)*")
                if st.button("🔍 ดูรายละเอียด", key="btn_m", use_container_width=True):
                    models_m = [
                        {"name": "Huawei SUN2000-5KTL-L1", "price": "200,000 บาท", "image": get_image_path("SUN2000-5KTL-L1-01.webp", "package3kW")},
                        {"name": "Growatt MIN 5000TL-X", "price": "189,000 บาท", "image": get_image_path("growatt-min-5000tl-x.jpg", "package3kW")}
                    ]
                    show_details("แพ็กเกจ", "5 kW", "189,000 - 200,000 บาท", "- แผงโซล่าร์เซลล์ (550W) จำนวน 8-10 แผง\n- อินเวอร์เตอร์ 1 เฟส จำนวน 1 ตัว พร้อมสมาร์ทมิเตอร์\n- ฟรี! ค่าดำเนินการขออนุญาตขนานไฟกับการไฟฟ้า\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี\n- รับประกันงานติดตั้ง 1 ปี", models=models_m, panel_models=panel_models_std)
        with col3:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #C8B6FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">🥇 แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">10 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("🏢 เหมาะสำหรับ: โฮมออฟฟิศ, กิจการขนาดเล็ก\n\n💵 ราคา: **329,000 บาท**\n\n*(เฉลี่ย ~32,900 ฿/kW)*")
                if st.button("🔍 ดูรายละเอียด", key="btn_l", use_container_width=True):
                    models_l = [
                        {"name": "Huawei SUN2000-10KTL-M1", "price": "329,000 บาท", "image": get_image_path("SUN2000-10KTL-M1-01.webp", "package3kW")},
                        {"name": "Growatt MOD 10KTL3-X", "price": "315,000 บาท", "image": get_image_path("growatt-mod-10ktl3-x.jpg", "package3kW")}
                    ]
                    show_details("แพ็กเกจ", "10 kW", "315,000 - 329,000 บาท", "- แผงโซล่าร์เซลล์ (550W) จำนวน 14-18 แผง\n- อินเวอร์เตอร์ 3 เฟส จำนวน 1 ตัว พร้อมสมาร์ทมิเตอร์\n- ฟรี! ค่าดำเนินการขออนุญาตขนานไฟกับการไฟฟ้า\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี\n- รับประกันงานติดตั้ง 2 ปี", models=models_l, panel_models=panel_models_std)
            
        # แถวที่ 2 แบ่ง 3 คอลัมน์เหมือนเดิมแต่ปล่อยคอลัมน์สุดท้ายว่างไว้เพื่อให้การ์ดขนาดเท่ากัน
        col4, col5, col6 = st.columns(3)
        with col4:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #B8C0FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">💎 แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">15 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("🏭 เหมาะสำหรับ: โรงงาน, กิจการขนาดกลาง\n\n💵 ราคา: **454,900 บาท**\n\n*(เฉลี่ย ~30,326 ฿/kW)*")
                if st.button("🔍 ดูรายละเอียด", key="btn_xl", use_container_width=True):
                    models_xl = [
                        {"name": "Huawei SUN2000-15KTL-M2", "price": "454,900 บาท", "image": get_image_path("Huawei-SUN2000-15KTL-M2.jpg", "package3kW")},
                        {"name": "Growatt MID 15KTL3-X", "price": "439,000 บาท", "image": get_image_path("Growatt MID 15KTL3-X.webp", "package3kW")}
                    ]
                    show_details("แพ็กเกจ", "15 kW", "439,000 - 454,900 บาท", "- แผงโซล่าร์เซลล์ (550W) จำนวน 20-28 แผง\n- อินเวอร์เตอร์ 3 เฟส พร้อมสมาร์ทมิเตอร์\n- บริการสำรวจและประเมินโครงสร้างหลังคาฟรี\n- ฟรี! ค่าดำเนินการขออนุญาตขนานไฟกับการไฟฟ้า\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี", models=models_xl, panel_models=panel_models_std)
        with col5:
            with st.container(border=True):
                st.image(get_image_path("Jiinko_550w.jpg", "package3kW"), use_container_width=True)
                st.markdown("""
                <div style="background-color: #BBD0FF; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #3B0764;">👑 แพ็กเกจ</h3>
                    <span style="color: #2E1065; font-weight: bold; font-size: 1.1em;">>15 kW</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("🏭 เหมาะสำหรับ: โรงงานใหญ่, อุตสาหกรรม\n\n💵 ราคา: **550,000 บาทขึ้นไป**\n\n*(เฉลี่ย ~27,500 ฿/kW)*")
                if st.button("🔍 ดูรายละเอียด", key="btn_xxl", use_container_width=True):
                    models_xxl = [
                        {"name": "Huawei SUN2000-30KTL-M3", "price": "550,000 บาท", "image": get_image_path("SUN2000-30KTL-M3.2.webp", "package3kW")},
                        {"name": "Growatt MID 30KTL3-X", "price": "520,000 บาท", "image": get_image_path("Growatt MID 30KTL3-X.webp", "package3kW")},
                        {"name": "Solis 30K-5G", "price": "500,000 บาท", "image": get_image_path("Solis 30K-5G.jpg", "package3kW")}
                    ]
                    show_details("แพ็กเกจ", ">15 kW", "500,000 - 550,000 บาทขึ้นไป", "- แผงโซล่าร์เซลล์ (550W) จำนวน 30 แผงขึ้นไป\n- อินเวอร์เตอร์ 3 เฟส พร้อมสมาร์ทมิเตอร์\n- ออกแบบระบบและประเมินโหลดตามการใช้งานจริง\n- บริการสำรวจและประเมินโครงสร้างหลังคาฟรี\n- รับประกันแผงโซล่าร์เซลล์ 25 ปี", models=models_xxl, panel_models=panel_models_std)
            
        st.divider()
        st.markdown("👈 **กรุณาเลือกเมนูที่แถบด้านซ้ายมือ** เพื่อวิเคราะห์ข้อมูลพฤติกรรมการใช้ไฟฟ้า และค้นหาลูกค้าเป้าหมายสำหรับเสนอโครงการ")
        
        st.stop() # หยุดการทำงานสคริปต์ตรงนี้ เพื่อไม่ให้แสดงผลหน้าอื่นซ้อนกัน

    # --- Sidebar สำหรับฟิลเตอร์ (ตัวกรอง) ---
    st.sidebar.header("🔍 ตัวกรองข้อมูล")
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
    if page == "📊 แดชบอร์ดวิเคราะห์":
        st.title("☀️ แดชบอร์ดวิเคราะห์พฤติกรรมการใช้ไฟฟ้า")
        st.markdown("*(สำหรับวิเคราะห์ภาพรวมการใช้ไฟฟ้า แนวโน้ม และพฤติกรรมของแต่ละกลุ่มลูกค้า)*")
        
        # --- KPI Section ---
        st.subheader("📊 สรุปภาพรวม (KPIs) ของกลุ่มที่เลือก")
        col1, col2, col3 = st.columns(3)
        
        total_kwh = filtered_df['kwh_total'].sum()
        total_amt = filtered_df['amt_invoice'].sum()
        avg_rate = total_amt / total_kwh if total_kwh > 0 else 0
        
        col1.metric("⚡ ปริมาณการใช้ไฟรวม (kWh)", f"{total_kwh:,.2f} หน่วย")
        col2.metric("💰 ค่าไฟฟ้ารวม (บาท)", f"฿ {total_amt:,.2f}")
        col3.metric("📈 ค่าไฟเฉลี่ยต่อหน่วย", f"฿ {avg_rate:,.2f} / kWh")
        
        st.divider()
        
        # --- ข้อมูลพื้นฐานสำหรับวิเคราะห์กลุ่มลูกค้า ---
        st.subheader("👥 ข้อมูลพื้นฐานสำหรับวิเคราะห์กลุ่มลูกค้า")
        st.markdown("*(ใช้ดูพฤติกรรมรายบุคคล/รายบิล เพื่อประเมินว่าแต่ละรายใช้ไฟเยอะพอที่จะคุ้มทุนในการเสนอโปรเจกต์หรือไม่)*")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        if customer_col:
            unique_customers = filtered_df[customer_col].nunique()
            info_col1.metric("🏠 จำนวนครัวเรือนรวม (ครัวเรือน)", f"{unique_customers:,}")
            
            avg_kwh_per_customer = total_kwh / unique_customers if unique_customers > 0 else 0
            info_col2.metric("⚡ การใช้ไฟเฉลี่ยต่อครัวเรือน", f"{avg_kwh_per_customer:,.2f} kWh")
            
            avg_amt_per_customer = total_amt / unique_customers if unique_customers > 0 else 0
            info_col3.metric("💸 ค่าไฟเฉลี่ยต่อครัวเรือน", f"฿ {avg_amt_per_customer:,.2f}")
            
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
            info_col1.metric("📄 จำนวนบิล/รายการรวม", f"{total_bills:,}")
            
            avg_kwh_per_bill = total_kwh / total_bills if total_bills > 0 else 0
            info_col2.metric("⚡ การใช้ไฟเฉลี่ยต่อบิล", f"{avg_kwh_per_bill:,.2f} kWh")
            
            avg_amt_per_bill = total_amt / total_bills if total_bills > 0 else 0
            info_col3.metric("💸 ค่าไฟเฉลี่ยต่อบิล", f"฿ {avg_amt_per_bill:,.2f}")
            
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

        st.subheader("📅 เปรียบเทียบหน่วยการใช้ไฟฟ้า ปี 2025 - 2026 (ม.ค. - มี.ค.)")
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
            st.subheader("📈 ตารางวิเคราะห์การเติบโต (Year-over-Year)")
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
            else:
                st.info("ℹ️ ข้อมูลไม่เพียงพอสำหรับการเปรียบเทียบการเติบโตระหว่างปี 2025 และ 2026 (อาจมีข้อมูลเพียงปีเดียว)")
        else:
            st.info("ℹ️ ยังไม่มีข้อมูลการใช้ไฟของเดือน มกราคม-มีนาคม ในปี 2025 และ 2026 ในระบบ")

        # --- สร้างกราฟแท่งความเคลื่อนไหวรายเดือน (New vs Lost) ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(" วิเคราะห์การเพิ่มขึ้นและลดลงของผู้ใช้ไฟ (New vs Lost Users)")
        
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
                st.write("**📊 วิเคราะห์การเพิ่มขึ้นและลดลงของผู้ใช้ไฟ (Interactive)**")
                
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
                )
                )
                
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

                st.info("💡 **ผู้ใช้ใหม่** คือคนที่ไม่เคยเห็นรหัสนี้มาก่อนในข้อมูลเดือนก่อนหน้า | **ผู้ใช้ที่หายไป** คือคนที่มีชื่อเดือนที่แล้วแต่ไม่มีในเดือนนี้")
            else:
                st.info("ℹ️ ข้อมูลไม่เพียงพอสำหรับสร้างกราฟความเคลื่อนไหวรายเดือน")
        else:
            st.warning("ไม่สามารถสร้างกราฟความเคลื่อนไหวได้ เนื่องจากไม่พบคอลัมน์หมายเลขผู้ใช้ไฟ")

        st.divider()

        col_pie1, col_pie2 = st.columns(2)
        
        with col_pie1:
            st.subheader("⚡ สัดส่วนการใช้ไฟ (kWh)")
            st.markdown("*(ใช้ดูว่ากลุ่มลูกค้าไหนมีการใช้พลังงานไฟฟ้าเยอะที่สุด)*")
            type_summary_kwh = filtered_df.groupby('user_type_name')['kwh_total'].sum().reset_index()
            fig_pie_kwh = px.pie(type_summary_kwh, values='kwh_total', names='user_type_name', 
                                 title="สัดส่วนปริมาณการใช้ไฟ (kWh) ตามกลุ่มลูกค้า", hole=0.4)
            st.plotly_chart(fig_pie_kwh, use_container_width=True)
            
        with col_pie2:
            st.subheader("🏢 สัดส่วนค่าไฟ (บาท)")
            st.markdown("*(ใช้หา Target Group ว่ากลุ่มไหนคือลูกค้ารายใหญ่ที่สุดที่ควรเข้าไปคุยเสนอโปรเจกต์)*")
            type_summary_amt = filtered_df.groupby('user_type_name')['amt_invoice'].sum().reset_index()
            fig_pie_amt = px.pie(type_summary_amt, values='amt_invoice', names='user_type_name', 
                                 title="สัดส่วนเม็ดเงินค่าไฟ (บาท) ตามกลุ่มลูกค้า", hole=0.4)
            st.plotly_chart(fig_pie_amt, use_container_width=True)

            st.divider()
            st.stop() # จบหน้าแดชบอร์ดตรงนี้

    # ==========================================
    # ส่วนที่ 3: หน้าค้นหาและวิเคราะห์ลูกค้าเป้าหมาย
    # ==========================================
    if page == "🎯 ค้นหาลูกค้าเป้าหมาย":
        st.title("🎯 ค้นหาและวิเคราะห์กลุ่มลูกค้าเป้าหมาย")
        st.markdown("*(เจาะลึกพฤติกรรมรายบุคคล ดูตำแหน่งแผนที่ และตารางประเมินความคุ้มค่าแบบ Real-Time)*")
        
        # --- แผนที่ตำแหน่งลูกค้า ---
        st.subheader("🗺️ แผนที่แสดงเป้าหมายลูกค้าที่ควรติดโซล่าร์เซลล์")
        st.markdown("*(แสดงจุดพิกัดของลูกค้าเพื่อประเมินศักยภาพในการเสนอโปรเจกต์)*")

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
                
                actual_kw = np.ceil((avg_kwh * 0.5 / 120) / 0.55) * 0.55
                avg_rate = np.where(avg_kwh > 0, map_summary['ค่าไฟเฉลี่ย/เดือน'] / avg_kwh, 4.5)
                solar_produced = actual_kw * (120 * 0.92) # หักประสิทธิภาพฝุ่นเมฆ 8% คร่าวๆ
                kwh_saved = np.minimum(solar_produced, avg_kwh)
                monthly_savings = np.minimum(kwh_saved * avg_rate, map_summary['ค่าไฟเฉลี่ย/เดือน'])
                
                # อิงราคาเงินลงทุนตามขนาดแพ็กเกจจริง
                inv_conds = [actual_kw <= 3, actual_kw <= 5, actual_kw <= 10, actual_kw <= 15]
                inv_vals = [145000, 200000, 329000, 454900]
                investment_map = np.select(inv_conds, inv_vals, default=actual_kw * 27500)
                
                payback_years = np.where(monthly_savings > 0, investment_map / (monthly_savings * 12), 99)
                
                map_summary['payback_years'] = payback_years
                
                def eval_map_status(row):
                    if row['payback_years'] > 7:
                        return "❌ ยังไม่คุ้มทุน"
                    
                    avg_bill = row['ค่าไฟเฉลี่ย/เดือน']
                    u_type = str(row.get('user_type', ''))
                    
                    if "กิจการขนาดใหญ่" in u_type:
                        if avg_bill >= 30000: return "🔵 ควรติด (กิจการขนาดใหญ่)"
                    elif "กิจการขนาดกลาง" in u_type:
                        if avg_bill >= 15000: return "🟣 ควรติด (กิจการขนาดกลาง)"
                    else:
                        # บ้านอยู่อาศัย, กิจการขนาดเล็ก, กิจการเฉพาะอย่าง หรืออื่นๆ
                        if avg_bill >= 3000: return "🟢 ควรติด (บ้าน/ขนาดเล็ก)"
                        
                    return "❌ ยังไม่คุ้มทุน"
                    
                map_summary['สถานะ'] = map_summary.apply(eval_map_status, axis=1)
                
                # เตรียมข้อมูลเพิ่มเติมสำหรับแสดงตอนชี้เมาส์ (Hover)
                map_summary['ประเภทผู้ใช้ไฟ'] = map_summary.get('user_type', 'ไม่ระบุ')
                map_summary['ค่าไฟก่อนติด (บาท/เดือน)'] = map_summary['ค่าไฟเฉลี่ย/เดือน']
                map_summary['ค่าไฟหลังติด (บาท/เดือน)'] = (map_summary['ค่าไฟเฉลี่ย/เดือน'] - monthly_savings).round(2)
                map_summary['คืนทุน (ปี)'] = np.round(payback_years, 1)

                # กรองให้เหลือเฉพาะเป้าหมายที่ควรเสนอโครงการ (ควรติดโซล่าร์เซลล์)
                map_summary = map_summary[map_summary['สถานะ'] != "❌ ยังไม่คุ้มทุน"]

                map_df = map_summary
                color_col = 'สถานะ'
                color_map = {
                    "🟢 ควรติด (บ้าน/ขนาดเล็ก)": "#00E676", # สีเขียว
                    "🟣 ควรติด (กิจการขนาดกลาง)": "#D500F9", # สีม่วง
                    "🔵 ควรติด (กิจการขนาดใหญ่)": "#2979FF"  # สีน้ำเงิน
                }
                hover_data = ["ประเภทผู้ใช้ไฟ", "ค่าไฟก่อนติด (บาท/เดือน)", "ค่าไฟหลังติด (บาท/เดือน)", "คืนทุน (ปี)"]

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
                    st.success("🔄 ระบบตรวจพบพิกัด UTM และได้แปลงเป็นพิกัดบนแผนที่สากล (Lat/Lon) อัตโนมัติ")
                except ImportError:
                    st.error("🛠️ พบพิกัดรูปแบบ UTM แต่ไม่สามารถแสดงแผนที่ได้เนื่องจากขาดเครื่องมือแปลงพิกัด (`pyproj`)")
                    st.info("💡 **วิธีแก้ไข:** ให้เปิด Terminal แล้วพิมพ์คำสั่ง `python -m pip install pyproj` จากนั้นกด Refresh หน้าเว็บ")
            
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
                fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True})
                
                if len(valid_map) < len(map_df):
                    st.warning(f"⚠️ ซ่อนจุดพิกัด {len(map_df) - len(valid_map):,} จุด เนื่องจากอยู่นอกเขตประเทศไทย หรือพิกัดผิดพลาด")
            else:
                st.info("ℹ️ ไม่มีจุดพิกัดบนแผนที่ (ไม่มีลูกค้าเข้าเกณฑ์ 'ควรติดโซล่าร์เซลล์' หรือข้อมูลพิกัดผิดพลาด)")
        else:
            st.warning(f"⚠️ พบคอลัมน์เป้าหมาย ({x_col}, {y_col}) แต่ไม่สามารถแปลงให้เป็นตัวเลขพิกัดได้เลย")
            st.write("ตัวอย่างข้อมูลดิบ (Raw Data):", filtered_df[[x_col, y_col]].head())
    else:
        st.info("ไม่พบคอลัมน์พิกัด X (คอลัมน์ G) และ Y (คอลัมน์ H) ในชุดข้อมูล")

    st.divider()

    # --- ค้นหารายบุคคล ---
    st.subheader("🔍 ค้นหาพฤติกรรมการใช้ไฟฟ้ารายบุคคล")
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
            if pd.isna(avg_kwh) or avg_kwh <= 0 or pd.isna(avg_amt) or avg_amt < 2000: 
                return False
            
            u_type = str(row['user_type'])
            day_r = 0.5 if "บ้าน" in u_type else (0.7 if "กิจการ" in u_type else 0.85)
            
            target_kw = (avg_kwh * day_r) / 120
            panels = np.ceil(target_kw / 0.55) if target_kw > 0 else 0
            actual_kw = panels * 0.55
            avg_rate = avg_amt / avg_kwh if avg_kwh > 0 else 4.5
            
            solar_produced = actual_kw * 120
            kwh_saved = min(solar_produced, avg_kwh)
            monthly_savings = min(kwh_saved * avg_rate, avg_amt)
            investment = actual_kw * 35000
            payback = investment / (monthly_savings * 12) if monthly_savings > 0 else 99
            
            return payback <= 7

        quick_summary['should_install'] = quick_summary.apply(eval_quick_status, axis=1)
        recommended_customers = set(quick_summary[quick_summary['should_install']][customer_col].astype(str))
        not_recommended_customers = set(quick_summary[~quick_summary['should_install']][customer_col].astype(str))
        
        if len(customer_list) > 0:
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
                options=["-- โปรดเลือกหมายเลขผู้ใช้ไฟ --"] + customer_list,
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
                scol1.metric("💰 ค่าไฟฟ้ารวมตลอดช่วง", f"฿ {cust_total_amt:,.2f}")
                scol2.metric("📊 ค่าไฟฟ้าเฉลี่ยต่อเดือน", f"฿ {cust_avg_amt:,.2f}")
                scol3.metric("📈 ค่าไฟสูงสุดที่เคยจ่าย", f"฿ {cust_max_amt:,.2f}")
                
                # --- เพิ่มข้อมูลและรายละเอียดเชิงลึกของลูกค้ารายบุคคล ---
                st.markdown("#### ⚙️ รายละเอียดและคำแนะนำการติดตั้งโซล่าร์เซลล์ (เฉพาะราย)")
                
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
                        aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5"
                        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=cloud_cover"
                        pm25 = float(requests.get(aqi_url, timeout=2).json().get('current', {}).get('pm2_5', 20.0))
                        cloud = float(requests.get(w_url, timeout=2).json().get('current', {}).get('cloud_cover', 20.0))
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
                investment = actual_kw * 35000
                payback = investment / (monthly_savings * 12) if monthly_savings > 0 else 99
                
                if cust_avg_amt >= 2000 and payback <= 7:
                    status_text = "✅ ควรติดโซล่าร์เซลล์ (คุ้มทุนเหมาะสม)"
                    status_color = "#dcfce7"
                    status_font = "#166534"
                else:
                    status_text = "❌ ยังไม่แนะนำ (ใช้ไฟน้อยไปหรือคืนทุนช้า)"
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
                        st.markdown(f"<div style='text-align:center'><b>ระยะเวลาคืนทุน</b><br><span style='font-size: 1.2em; color: #b45309;'>{payback:,.1f} ปี</span><br>(ลงทุน ฿ {investment:,.0f})</div>", unsafe_allow_html=True)
                with dcol4:
                    with st.container(border=True):
                        st.markdown(f"<div style='text-align:center'><b>สภาพแวดล้อม (Real-Time)</b><br><span style='font-size: 0.75em; color: #6b7280;'>📍 พิกัด: {lat:.4f}, {lon:.4f}</span><br><span style='font-size: 0.9em; color: #6b7280;'>ฝุ่น PM2.5: {pm25:.1f} μg/m³<br>ความเข้มแสง: {100 - cloud:.0f}%</span></div>", unsafe_allow_html=True)

                st.markdown(f'''
                <div style="background-color: {status_color}; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                    <strong style="color: {status_font}; font-size: 16px;">สถานะการประเมิน: {status_text}</strong>
                </div>
                ''', unsafe_allow_html=True)
                
                # --- ส่วนแสดงเปรียบเทียบ ก่อน-หลัง (Before & After) ---
                kwh_after = cust_avg_kwh - kwh_saved
                amt_after = cust_avg_amt - monthly_savings
                
                st.markdown("##### ⚖️ เปรียบเทียบก่อนและหลังติดตั้ง (หักลบผลกระทบฝุ่นและเมฆแล้ว)")
                c1, c2, c3 = st.columns(3)
                with c1:
                    with st.container(border=True):
                        st.info(f"**💡 ก่อนติดตั้ง (เฉลี่ยเดิม)**\n\n⚡ ใช้ไฟ: **{cust_avg_kwh:,.2f}** หน่วย/เดือน\n\n💸 ค่าไฟ: **฿ {cust_avg_amt:,.2f}** /เดือน")
                with c2:
                    with st.container(border=True):
                        st.success(f"**☀️ โซล่าร์เซลล์ช่วยลดได้**\n\n📉 ลดการใช้ไฟ: **{kwh_saved:,.2f}** หน่วย/เดือน\n\n💰 ประหยัดเงิน: **฿ {monthly_savings:,.2f}** /เดือน")
                with c3:
                    with st.container(border=True):
                        st.warning(f"**⚡ หลังติดตั้ง (ต้องจ่ายการไฟฟ้า)**\n\n🔋 เหลือการใช้ไฟ: **{max(0, kwh_after):,.2f}** หน่วย/เดือน\n\n🧾 จ่ายค่าไฟ: **฿ {max(0, amt_after):,.2f}** /เดือน")
                        
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📝 ดูรายการคำนวณทีละขั้นตอน 9 ข้อ (อิงจากหน่วยไฟและค่าไฟจริงของลูกค้ารายนี้)"):
                    pkg_rec = "3 kW" if actual_kw <= 3 else "5 kW" if actual_kw <= 5 else "10 kW" if actual_kw <= 10 else "15 kW" if actual_kw <= 15 else ">15 kW"
                    produced_before = actual_kw * 120
                    lost_kwh = produced_before - solar_produced
                    
                    st.markdown(f"""
                    **📊 ข้อมูลตั้งต้นของลูกค้ารายนี้:**
                    - การใช้ไฟเฉลี่ย (`kwh_total`): **{cust_avg_kwh:,.2f} หน่วย/เดือน**
                    - ค่าไฟเฉลี่ย (`amt_invoice`): **{cust_avg_amt:,.2f} บาท/เดือน**
                    - อัตราค่าไฟเฉลี่ย: **{avg_rate:,.2f} บาท/หน่วย**
                    - สภาพแวดล้อม ณ พิกัดบ้าน ({lat:.4f}, {lon:.4f}): ฝุ่น PM2.5 = {pm25:.1f} (ลดทอน {d_imp:.1f}%), ความเข้มแสง = {100 - cloud:.0f}% (เมฆลดทอน {l_imp:.1f}%)

                    **🧮 ผลการคำนวณ 9 ขั้นตอน:**
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
                    st.markdown("##### 📈 กราฟวิเคราะห์จุดคุ้มทุน (Breakeven Analysis)")
                    
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
    st.subheader("☀️ วิเคราะห์ความคุ้มค่าการติดโซล่าร์เซลล์รายบ้าน (Real-Time API)")
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
            
            # ลดความละเอียดพิกัด (ทศนิยม 3 ตำแหน่ง = รัศมี ~100 เมตร) เพื่อให้ข้อมูลแม่นยำระดับหมู่บ้าน/ถนนจริงๆ
            cust_summary['lat_r'] = cust_summary['latitude'].round(3)
            cust_summary['lon_r'] = cust_summary['longitude'].round(3)
        else:
            cust_summary['lat_r'] = np.nan
            cust_summary['lon_r'] = np.nan

        # 3. ฟังก์ชันดึงข้อมูลจาก Open-Meteo API (ใช้ Cache ลดการดึงซ้ำ)
        @st.cache_data(ttl=1800) # อัปเดตทุกครึ่งชั่วโมง
        def fetch_realtime_env(coords):
            import concurrent.futures
            results = {}
            
            # จำกัดพิกัดที่ไม่ซ้ำกันสูงสุด 100 จุด เพื่อป้องกัน API โดนบล็อก
            if len(coords) > 100:
                coords = coords[:100]
                
            def fetch_single(lat, lon):
                try:
                    aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5"
                    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=cloud_cover"
                    pm25 = requests.get(aqi_url, timeout=2).json().get('current', {}).get('pm2_5', 20.0)
                    cloud = requests.get(w_url, timeout=2).json().get('current', {}).get('cloud_cover', 20.0)
                    return (lat, lon, pm25, cloud)
                except:
                    return (lat, lon, 20.0, 20.0) # ค่าเริ่มต้นกรณี API Error หรือ Timeout

            # ดึงข้อมูลพร้อมกัน (Parallel Threading) เพื่อให้เสร็จไวขึ้น 5 เท่า
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(fetch_single, lat, lon) for lat, lon in coords]
                for future in concurrent.futures.as_completed(futures):
                    lat, lon, pm25, cloud = future.result()
                    results[(lat, lon)] = {'pm25': pm25, 'cloud': cloud}
                    
            return results

        valid_coords = cust_summary.dropna(subset=['lat_r', 'lon_r'])[['lat_r', 'lon_r']].drop_duplicates()
        coord_list = list(zip(valid_coords['lat_r'], valid_coords['lon_r']))
        
        env_data = {}
        if coord_list:
            with st.spinner("🌍 กำลังเชื่อมต่อดาวเทียม... ดึงข้อมูลความเข้มแสงและ PM2.5 แบบ Real-Time ให้แต่ละพิกัด..."):
                env_data = fetch_realtime_env(coord_list)

        # 4. ฟังก์ชันคำนวณผลกระทบต่อแผงโซล่าร์เซลล์
        def apply_env_impact(row):
            lat, lon = row.get('lat_r'), row.get('lon_r')
            if pd.isna(lat) or pd.isna(lon): return pd.Series([20.0, 20.0, 2.0, 5.0])
            data = env_data.get((lat, lon), {'pm25': 20.0, 'cloud': 20.0})
            pm = float(data['pm25']) if data['pm25'] is not None else 20.0
            cl = float(data['cloud']) if data['cloud'] is not None else 20.0
            d_imp = min(pm / 10, 15.0) # ยิ่งฝุ่นเยอะ ประสิทธิภาพลด
            l_imp = min(cl / 4, 25.0)  # ยิ่งเมฆเยอะ ความเข้มแสงยิ่งน้อย
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

        def recommend_package(avg_bill):
            if avg_bill < 3000:
                return "3 kW"
            elif avg_bill < 7000:
                return "5 kW"
            elif avg_bill < 15000:
                return "10 kW"
            else:
                return "20+ kW"
                
        cust_summary['recommended_package'] = cust_summary['avg_amt_per_month'].apply(recommend_package)

        # สมมติฐาน: ใช้ไฟกลางวันตามสัดส่วน (บ้าน 50%, กิจการ 70%, อื่นๆ 85%), 1kW ผลิตไฟ 120 หน่วย/เดือน, แผงละ 550W (0.55kW)
        cust_summary['target_kwh'] = cust_summary['avg_kwh_per_month'] * cust_summary['day_ratio']
        cust_summary['recommended_kw'] = cust_summary['target_kwh'] / 120
        
        # ปรับลดประสิทธิภาพการผลิตจากปัจจัยสิ่งแวดล้อม (ดึง API มาแล้ว)
        cust_summary['efficiency_factor'] = (1 - (cust_summary['dust_impact'] / 100)) * (1 - (cust_summary['light_impact'] / 100))
        cust_summary['kwh_per_kw_month_adjusted'] = 120 * cust_summary['efficiency_factor']

        # คำนวณจำนวนแผงและปัดขึ้นเป็นจำนวนเต็ม
        cust_summary['panels_needed'] = np.ceil(cust_summary['recommended_kw'] / 0.55)
        # ปรับขนาด kW ให้ตรงกับจำนวนแผงที่ต้องติดจริง
        cust_summary['actual_kw'] = cust_summary['panels_needed'] * 0.55
        
        # หาอัตราค่าไฟเฉลี่ยของบ้านแต่ละหลัง (บาท/หน่วย) ตามข้อมูลจริง
        cust_summary['avg_rate'] = np.where(cust_summary['avg_kwh_per_month'] > 0, 
                                            cust_summary['avg_amt_per_month'] / cust_summary['avg_kwh_per_month'], 
                                            4.5)
        
        # คำนวณหน่วยไฟที่ผลิตได้จริงและประหยัดได้
        cust_summary['solar_kwh_produced'] = cust_summary['actual_kw'] * cust_summary['kwh_per_kw_month_adjusted']
        cust_summary['kwh_saved'] = np.minimum(cust_summary['solar_kwh_produced'], cust_summary['avg_kwh_per_month'])
        
        # คำนวณส่วนที่ประหยัดได้ (ผลิตได้ตามประสิทธิภาพที่ปรับแล้ว * อัตราค่าไฟ) และไม่ให้เกินค่าไฟเดิม
        cust_summary['monthly_savings'] = cust_summary['solar_kwh_produced'] * cust_summary['avg_rate']
        cust_summary['monthly_savings'] = np.minimum(cust_summary['monthly_savings'], cust_summary['avg_amt_per_month'])
        
        cust_summary['cost_after_solar'] = cust_summary['avg_amt_per_month'] - cust_summary['monthly_savings']
        cust_summary['investment'] = cust_summary['actual_kw'] * 35000
        
        cust_summary['payback_years'] = np.where(cust_summary['monthly_savings'] > 0,
                                                 cust_summary['investment'] / (cust_summary['monthly_savings'] * 12),
                                                 99)
        
        # เงื่อนไขควรติด: ค่าไฟเฉลี่ย >= 2000 และคืนทุน <= 7 ปี
        cust_summary['should_install'] = np.where(
            (cust_summary['avg_amt_per_month'] >= 2000) & (cust_summary['payback_years'] <= 7),
            "✅ ควรติด",
            "❌ ยังไม่คุ้ม"
        )
        
        # จัดคอลัมน์และเปลี่ยนชื่อเพื่อแสดงผล
        display_df = cust_summary[[
            customer_col, 'user_type_name', 'should_install', 'pm25_real', 'light_intensity', 'avg_kwh_per_month', 'kwh_saved', 'avg_amt_per_month', 'monthly_savings', 'cost_after_solar',
            'actual_kw', 'recommended_package', 'panels_needed', 'investment', 'payback_years'
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
            'investment': 'เงินลงทุนโดยประมาณ (บาท)',
            'payback_years': 'คืนทุน (ปี)'
        })
        
        display_df['จำนวนแผง (แผงละ 550W)'] = display_df['จำนวนแผง (แผงละ 550W)'].astype(int)
        
        # เรียงตามลำดับค่าไฟจากมากไปน้อย (รายใหญ่ขึ้นก่อน)
        display_df = display_df.sort_values(by='ค่าไฟเดิม (บาท/เดือน)', ascending=False).reset_index(drop=True)
        
        # --- ตัวกรองข้อมูลสำหรับตาราง ---
        st.markdown("**🔎 ตัวกรองข้อมูลตาราง:**")
        
        if not display_df.empty:
            fcol1, fcol2 = st.columns(2)
            
            with fcol1:
                filter_status = st.radio(
                    "สถานะคำแนะนำ:",
                    options=["แสดงทั้งหมด", "✅ ควรติด", "❌ ยังไม่คุ้ม"],
                    horizontal=True,
                    index=1 # ตั้งค่าเริ่มต้นให้เลือกโชว์เฉพาะ 'ควรติด' 
                )
                
                min_bill = float(display_df['ค่าไฟเดิม (บาท/เดือน)'].min())
                max_bill = float(display_df['ค่าไฟเดิม (บาท/เดือน)'].max())
                if min_bill < max_bill:
                    filter_bill = st.slider("ช่วงค่าไฟเดิม (บาท/เดือน):", min_value=min_bill, max_value=max_bill, value=(min_bill, max_bill), step=100.0)
                else:
                    filter_bill = (min_bill, max_bill)

            with fcol2:
                unique_types = display_df['ประเภทผู้ใช้ไฟ'].unique().tolist()
                filter_user_types = st.multiselect(
                    "ประเภทผู้ใช้ไฟ:",
                    options=unique_types,
                    default=unique_types
                )
                
                min_pb = float(display_df['คืนทุน (ปี)'].min())
                max_pb = float(display_df['คืนทุน (ปี)'].max())
                if min_pb < max_pb:
                    filter_payback = st.slider("ระยะเวลาคืนทุน (ปี):", min_value=min_pb, max_value=max_pb, value=(min_pb, max_pb), step=0.5)
                else:
                    filter_payback = (min_pb, max_pb)
                    
            # นำตัวกรองทั้งหมดมาตัดข้อมูลในตาราง
            if filter_status != "แสดงทั้งหมด":
                display_df = display_df[display_df['คำแนะนำ'] == filter_status]
                
            if filter_user_types:
                display_df = display_df[display_df['ประเภทผู้ใช้ไฟ'].isin(filter_user_types)]
                
            display_df = display_df[
                (display_df['ค่าไฟเดิม (บาท/เดือน)'] >= filter_bill[0]) & 
                (display_df['ค่าไฟเดิม (บาท/เดือน)'] <= filter_bill[1])
            ]
            
            display_df = display_df[
                (display_df['คืนทุน (ปี)'] >= filter_payback[0]) & 
                (display_df['คืนทุน (ปี)'] <= filter_payback[1])
            ]
            
            display_df = display_df.reset_index(drop=True)

        st.success(f"🎯 **จำนวนลูกค้าเป้าหมายที่ตรงตามเงื่อนไข:** {len(display_df):,} ราย")

        # กำหนดรูปแบบให้มีลูกน้ำและจุดทศนิยมสำหรับตาราง (เพื่อให้ยังคลิกเรียงลำดับในหน้าเว็บได้ปกติ)
        format_dict_solar = {
            'ฝุ่น PM2.5 (μg/m³)': '{:,.1f}',
            'ความเข้มแสง (%)': '{:,.0f}%',
            'ใช้ไฟเดิม (kWh/เดือน)': '{:,.2f}',
            'ประหยัดไฟ (kWh/เดือน)': '{:,.2f}',
            'ค่าไฟเดิม (บาท/เดือน)': '{:,.2f}',
            'ประหยัดเงิน (บาท/เดือน)': '{:,.2f}',
            'ค่าไฟสุทธิ (บาท/เดือน)': '{:,.2f}',
            'ขนาดติดตั้ง (kW)': '{:,.2f}',
            'เงินลงทุนโดยประมาณ (บาท)': '{:,.2f}',
            'คืนทุน (ปี)': '{:,.1f}'
        }
        
        # ปรับขยายขีดจำกัดการ Render ของ Pandas Styler ให้รองรับข้อมูลตารางขนาดใหญ่
        pd.set_option("styler.render.max_elements", max(display_df.size, 262144))
        
        st.dataframe(display_df.style.format(format_dict_solar), use_container_width=True)
        
        st.caption("""
        **💡 สมมติฐานการคำนวณจากข้อมูลการใช้ไฟจริง (อ้างอิงตามมาตรฐานไทย):**
            - ประเมินให้ระบบโซล่าร์เซลล์ครอบคลุมการใช้ไฟช่วงกลางวันตามพฤติกรรม (บ้านอยู่อาศัย 50%, กิจการ 70%, อื่นๆ 85%)
            - ใช้แผงโซล่าร์เซลล์ขนาด 550W (0.55 kW)
            - 1 kW ผลิตไฟฟ้าได้เฉลี่ย 120 หน่วย/เดือน **(ก่อนหักผลกระทบจากฝุ่นและความเข้มแสง)**
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