import pandas as pd
from pathlib import Path
import zipfile

def read_all_csv_in_directory(directory_path: str = ".", combine: bool = False):
    """
    ค้นหาและอ่านไฟล์ .csv ทั้งหมดในโฟลเดอร์ที่กำหนด
    
    :param directory_path: พาธของโฟลเดอร์ที่ต้องการค้นหาไฟล์ (ค่าเริ่มต้นคือโฟลเดอร์ปัจจุบัน ".")
    :param combine: หากตั้งเป็น True จะนำข้อมูลทุกไฟล์มารวมเป็น DataFrame เดียว
    :return: Dictionary ของ DataFrame หรือ DataFrame รวม
    """
    folder = Path(directory_path)
    csv_files = list(folder.glob("*.csv")) + list(folder.glob("*.zip"))
    
    if not csv_files:
        print(f"ไม่พบไฟล์ .csv หรือ .zip ในโฟลเดอร์: {directory_path}")
        return None
        
    print(f"พบไฟล์ข้อมูลทั้งหมด {len(csv_files)} ไฟล์ กำลังเริ่มอ่านข้อมูล...\n")
    
    dataframes = {}
    for file in csv_files:
        if file.suffix.lower() == '.zip':
            # กรณีเป็นไฟล์ .zip ให้เปิดค้นหาไฟล์ .csv ข้างใน
            try:
                with zipfile.ZipFile(file, 'r') as z:
                    # ค้นหาเฉพาะไฟล์ .csv และมองข้ามโฟลเดอร์ซ่อนตัวของระบบ (เช่น __MACOSX)
                    csv_names = [f for f in z.namelist() if f.lower().endswith('.csv') and '__MACOSX' not in f]
                    
                    if not csv_names:
                        print(f"⚠️ ไม่พบไฟล์ .csv ภายใน: {file.name}")
                        
                    for csv_name in csv_names:
                        try:
                            try:
                                # ลองอ่านแบบปกติก่อน (รองรับภาษาไทยมาตรฐานใหม่)
                                with z.open(csv_name) as f:
                                    df = pd.read_csv(f, encoding='utf-8-sig')
                            except UnicodeDecodeError:
                                # ถ้าอ่านไม่ได้ ให้ลองใช้ภาษาไทยแบบ Windows (TIS-620/CP874)
                                with z.open(csv_name) as f:
                                    df = pd.read_csv(f, encoding='cp874')
                                    
                            if len(df.columns) >= 8:
                                df = df.rename(columns={df.columns[6]: 'x_coord', df.columns[7]: 'y_coord'})
                            
                            # ใช้ชื่อไฟล์ CSV ข้างใน ZIP เพื่อให้แยกเดือน-ปีได้ถูกต้อง
                            df['source_file'] = Path(csv_name).name 
                            dataframes[f"{file.name}_{csv_name}"] = df
                            print(f"✅ อ่านไฟล์สำเร็จ: {csv_name} (จาก {file.name}) (จำนวน {len(df)} แถว)")
                        except Exception as e:
                            print(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์ {csv_name} ใน {file.name}: {e}")
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการเปิดไฟล์ ZIP {file.name}: {e}")
        else:
            # กรณีเป็นไฟล์ .csv ปกติ
            try:
                try:
                    df = pd.read_csv(file, encoding='utf-8-sig')
                except UnicodeDecodeError:
                    df = pd.read_csv(file, encoding='cp874')
                    
                if len(df.columns) >= 8:
                    df = df.rename(columns={
                        df.columns[6]: 'x_coord',
                        df.columns[7]: 'y_coord'
                    })
                        
                df['source_file'] = file.name
                dataframes[file.name] = df
                print(f"✅ อ่านไฟล์สำเร็จ: {file.name} (จำนวน {len(df)} แถว, {len(df.columns)} คอลัมน์)")
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์ {file.name}: {e}")
            
    if combine:
        if dataframes:
            print("\nกำลังรวมข้อมูล (Concatenating) ทั้งหมดเข้าด้วยกัน...")
            combined_df = pd.concat(dataframes.values(), ignore_index=True)
            print(f"รวมข้อมูลเสร็จสิ้น! ข้อมูลรวมมีทั้งหมด {len(combined_df)} แถว")
            return combined_df
        return None
        
    return dataframes

# ฟังก์ชันสำหรับ Mapping ประเภทผู้ใช้งาน PEA ตามหมวดหมู่หลัก
def get_pea_user_type(ratecat_code):
    # แปลงข้อมูลเป็นข้อความ ตัดช่องว่าง และเช็คค่าว่าง (NaN)
    val = str(ratecat_code).strip()
    if val.lower() == 'nan' or val == '':
        return 'ไม่สามารถระบุได้'
        
    # ดึงอักขระตัวแรกสุดมาเช็ค
    main_category = val[0]
    
    mapping = {
        '1': 'บ้านอยู่อาศัย',
        '2': 'กิจการขนาดเล็ก',
        '3': 'กิจการขนาดกลาง',
        '4': 'กิจการขนาดใหญ่',
        '5': 'กิจการเฉพาะอย่าง',
        '6': 'ส่วนราชการ/องค์กรที่ไม่แสวงหากำไร',
        '7': 'สูบน้ำเพื่อการเกษตร',
        '8': 'ไฟฟ้าชั่วคราว'
    }
    return mapping.get(main_category, 'ไม่สามารถระบุได้')

def process_pea_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    ฟังก์ชันสำหรับทำความสะอาดและเตรียมข้อมูล PEA จากไฟล์ที่รวมกันแล้ว
    """
    print("\nกำลังเตรียมข้อมูล (Data Preprocessing)...")
    # 1. แปลง ratecat เป็นชื่อประเภท
    # ถ้าไม่พบคอลัมน์ชื่อ ratecat ให้ดึงจากคอลัมน์ B (Index 1)
    if 'ratecat' not in df.columns and len(df.columns) >= 2:
        df = df.rename(columns={df.columns[1]: 'ratecat'})

    if 'ratecat' in df.columns:
        df['user_type_name'] = df['ratecat'].apply(get_pea_user_type)
        
        # ตรวจสอบและแสดงค่าแปลกปลอมที่ถูกจัดเป็น "ไม่สามารถระบุได้"
        unknowns = df[df['user_type_name'] == 'ไม่สามารถระบุได้']['ratecat'].unique()
        if len(unknowns) > 0:
            print(f"⚠️ พบข้อมูลประเภทผู้ใช้ไฟที่ไม่ได้ขึ้นต้นด้วย 1-8 ได้แก่: {unknowns[:10]}")
        
    # 2. จัดการแยกปี-เดือน จาก "ชื่อไฟล์" (เช่น 012025.csv -> เดือน 01, ปี 2025)
    if 'source_file' in df.columns:
        # ดึงตัวเลข 2 ตัว (เดือน) และ 4 ตัว (ปี) ที่อยู่ก่อน .csv หรือ .zip
        extracted = df['source_file'].astype(str).str.extract(r'(\d{2})(\d{4})\.(?:csv|CSV|zip|ZIP)')
        df['month'] = extracted[0].fillna('01')
        df['year'] = extracted[1].fillna('2024')
    else:
        df['year'] = '2024' # ค่าเริ่มต้นหากไม่มีคอลัมน์นี้
        df['month'] = '01'
        
    # 3. จัดการคอลัมน์ kwh_total (หน่วยไฟ)
    # ถ้าไม่พบคอลัมน์ชื่อ kwh_total ให้ดึงจากคอลัมน์ E (Index 4)
    if 'kwh_total' not in df.columns and len(df.columns) >= 5:
        df = df.rename(columns={df.columns[4]: 'kwh_total'})

    if 'kwh_total' in df.columns:
        if df['kwh_total'].dtype == 'object':
            df['kwh_total'] = df['kwh_total'].astype(str).str.replace(',', '').str.strip()
        df['kwh_total'] = pd.to_numeric(df['kwh_total'], errors='coerce').fillna(0)
        
    # 4. จัดการคอลัมน์ amt_invoice (ค่าไฟที่ต้องจ่าย)
    # ถ้าไม่พบคอลัมน์ชื่อ amt_invoice ให้ดึงจากคอลัมน์ F (Index 5) แทน
    if 'amt_invoice' not in df.columns and len(df.columns) >= 6:
        df = df.rename(columns={df.columns[5]: 'amt_invoice'})

    if 'amt_invoice' in df.columns:
        # กรณีที่มีเครื่องหมายคอมมา (,) ในตัวเลข ให้ลบออกก่อนแปลงค่า
        if df['amt_invoice'].dtype == 'object':
            df['amt_invoice'] = df['amt_invoice'].astype(str).str.replace(',', '').str.strip()
        df['amt_invoice'] = pd.to_numeric(df['amt_invoice'], errors='coerce').fillna(0)
        
    print("เตรียมข้อมูลเสร็จสิ้น!")
    return df

def separate_and_save_data(df: pd.DataFrame, category_column: str, output_folder: str = "separated_data"):
    """
    แยกข้อมูลตามประเภทในคอลัมน์ที่กำหนดและบันทึกเป็นไฟล์ .csv ใหม่แต่ละประเภท
    """
    if category_column not in df.columns:
        print(f"❌ เกิดข้อผิดพลาด: ไม่พบคอลัมน์ '{category_column}' ในข้อมูล")
        print(f"คอลัมน์ที่มีทั้งหมด: {list(df.columns)}")
        return
        
    # สร้างโฟลเดอร์สำหรับเก็บไฟล์ผลลัพธ์
    out_path = Path(output_folder)
    out_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\nกำลังแยกข้อมูลตามคอลัมน์: '{category_column}'...")
    
    # ใช้ groupby ของ pandas ในการจัดกลุ่มข้อมูล
    grouped = df.groupby(category_column)
    
    for category_name, group_df in grouped:
        # จัดการชื่อไฟล์ไม่ให้มีอักขระพิเศษ
        safe_filename = "".join([c for c in str(category_name) if c.isalpha() or c.isdigit() or c in ' -_']).strip()
        if not safe_filename:
            safe_filename = "unknown"
            
        file_path = out_path / f"category_{safe_filename}.csv"
        
        # บันทึกไฟล์ CSV รองรับภาษาไทยด้วย utf-8-sig
        group_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"💾 บันทึกหมวดหมู่ '{category_name}' ลงไฟล์ -> {file_path.name} ({len(group_df)} แถว)")

# ---------------------------------------------------------
# วิธีการเรียกใช้งาน
# ---------------------------------------------------------
if __name__ == "__main__":
    # 1. อ่านทุกไฟล์ CSV (แต่ละไฟล์คือแต่ละเดือน) ในโฟลเดอร์ปัจจุบัน มารวมเป็น DataFrame เดียว
    all_data_combined = read_all_csv_in_directory(".", combine=True)
    
    if all_data_combined is not None:
        # 2. ทำความสะอาดและสร้างคอลัมน์ใหม่ (user_type_name, year, month)
        processed_df = process_pea_data(all_data_combined)
        
        # 3. สรุปยอดรวมการใช้ไฟฟ้า (kwh_total) และค่าไฟ (amt_invoice) รายเดือน จากข้อมูลทุกไฟล์รวมกัน
        summary_cols = [col for col in ['kwh_total', 'amt_invoice'] if col in processed_df.columns]
        
        if 'year' in processed_df.columns and 'month' in processed_df.columns and summary_cols:
            monthly_summary = processed_df.groupby(['year', 'month'])[summary_cols].sum().reset_index()
            
            # จัดเรียงตามปีและเดือนเพื่อให้ดูง่ายขึ้น
            monthly_summary = monthly_summary.sort_values(by=['year', 'month'])
            
            print("\n--- สรุปยอดรวมรายเดือน (รวมจากทุกไฟล์) ---")
            print(monthly_summary.to_string(index=False))
            
        # 4. หากต้องการเซฟแยกเป็นโฟลเดอร์ย่อยตามประเภทผู้ใช้ (ratecat) ให้เอาคอมเมนต์บรรทัดล่างออก
        # print("\n--- แยกไฟล์ตามประเภทผู้ใช้งาน (user_type_name) ---")
        # separate_and_save_data(processed_df, category_column='user_type_name', output_folder='separated_by_usertype')