import pyodbc
import hashlib
from rsa_utils import load_public_key, load_private_key, encrypt_rsa, decrypt_rsa


def get_connection():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=QLSVNhom;Trusted_Connection=yes;'
    )
    return conn

def login(manv, matkhau):
    # Mã hóa mật khẩu thành UTF-16 little-endian (giống SQL Server)
    matkhau_utf16 = matkhau.encode('utf-16le')
    hashed_pw = hashlib.sha1(matkhau_utf16).digest()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM NHANVIEN WHERE MANV = ? AND MATKHAU = ?", (manv, hashed_pw))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def get_classes(manv):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_GET_LOP_BY_NHANVIEN ?", (manv,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_students(malop):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_GET_SINHVIEN_BY_LOP ?", (malop,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_score(masv, mahp, diemthi, pubkey_name):
    public_key = load_public_key()
    encrypted_diem = encrypt_rsa(str(diemthi), public_key)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_INSERT_BANGDIEM ?, ?, ?, ?", (masv, mahp, encrypted_diem, pubkey_name))
    conn.commit()
    conn.close()


def get_all_classes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MALOP, TENLOP, MANV FROM LOP")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_student(masv, hoten, ngaysinh, diachi, malop, tendn):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE SINHVIEN
        SET HOTEN = ?, NGAYSINH = ?, DIACHI = ?, MALOP = ?, TENDN = ?
        WHERE MASV = ?
    """, (hoten, ngaysinh, diachi,malop, tendn, masv))
    conn.commit()
    conn.close()

def get_scores(masv, manv, mk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_GET_BANGDIEM ?, ?, ?", (masv, manv, mk))
    rows = cursor.fetchall()
    conn.close()

    private_key = load_private_key()
    result = []

    for row in rows:
        mahp, tenhp, diem_enc = row
        try:
            diem = float(decrypt_rsa(diem_enc, private_key))
        except:
            diem = None
        result.append((mahp, tenhp, diem))
    
    return result

def insert_nhanvien(manv, hoten, email, luong, tendn, mk, pub):
    # Hash mật khẩu giống như login (SHA1 trên UTF-16LE)
    hashed_pw = hashlib.sha1(mk.encode('utf-16le')).digest()
    public_key = load_public_key()
    encrypted_luong = encrypt_rsa(str(luong), public_key)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_INS_PUBLIC_ENCRYPT_NHANVIEN ?, ?, ?, ?, ?, ?, ?", 
                   (manv, hoten, email, encrypted_luong, tendn, hashed_pw, pub))
    conn.commit()
    conn.close()

def select_nhanvien(tendn, mk):
    # Hash mật khẩu giống như login (SHA1 trên UTF-16LE)
    hashed_pw = hashlib.sha1(mk.encode('utf-16le')).digest()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_SEL_PUBLIC_ENCRYPT_NHANVIEN ?, ?", (tendn, hashed_pw))
    rows = cursor.fetchall()
    conn.close()

    # Giải mã lương ở đây
    if not rows:
        return []

    private_key = load_private_key()
    decrypted_rows = []
    for row in rows:
        try:
            luong_giai_ma = decrypt_rsa(row.LUONG, private_key)
        except Exception:
            luong_giai_ma = "Không giải mã được"
        decrypted_rows.append({
            "MANV": row.MANV,
            "HOTEN": row.HOTEN,
            "EMAIL": row.EMAIL,
            "LUONG": luong_giai_ma
        })
    
    return decrypted_rows

def get_all_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MANV, HOTEN, TENDN FROM NHANVIEN")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_employee(tendn):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM NHANVIEN WHERE TENDN = ?", (tendn,))
    conn.commit()
    conn.close()