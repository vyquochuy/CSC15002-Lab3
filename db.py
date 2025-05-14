import pyodbc

def get_connection():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=QLSVNhom;Trusted_Connection=yes;'
    )
    return conn

def login(manv, matkhau):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM NHANVIEN WHERE MANV = ? AND MATKHAU = HASHBYTES('SHA1', ?)", (manv, matkhau))
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

def insert_score(masv, mahp, diemthi, pubkey):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_INSERT_BANGDIEM ?, ?, ?, ?", (masv, mahp, diemthi, pubkey))
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

def get_scores(masv, manv, matkhau):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC SP_GET_BANGDIEM ?, ?, ?", (masv, manv, matkhau))
    rows = cursor.fetchall()
    conn.close()
    return rows
