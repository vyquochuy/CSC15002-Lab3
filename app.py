import pyodbc

# Kết nối SQL Server
conn = pyodbc.connect(
    'DRIVER={SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=QLSVNhom;Trusted_Connection=yes;'
)

cursor = conn.cursor()

def login(tendn, matkhau):
    cursor.execute("EXEC SP_LOGIN_NHANVIEN ?, ?", (tendn, matkhau))
    result = cursor.fetchone()
    return result.Status == 'LOGIN_SUCCESS'

def get_lop(manv):
    cursor.execute("EXEC SP_GET_LOP_BY_NHANVIEN ?", (manv,))
    return cursor.fetchall()

def get_sinhvien(malop):
    cursor.execute("EXEC SP_GET_SINHVIEN_BY_LOP ?", (malop,))
    return cursor.fetchall()

def insert_bangdiem(masv, mahp, diemthi, pubkey):
    cursor.execute("EXEC SP_INSERT_BANGDIEM ?, ?, ?, ?", (masv, mahp, diemthi, pubkey))
    conn.commit()

# --- Chạy thử ---
print("=== Đăng nhập ===")
manv = input("Mã Nhân ViênViên: ")
matkhau = input("Mật khẩu: ")

if login(manv, matkhau):
    print("Đăng nhập thành công!")

    # Xem lớp quản lý
    print("\n=== Các lớp bạn quản lý ===")
    lops = get_lop(manv)
    for lop in lops:
        print(f"Mã lớp: {lop.MALOP}, Tên lớp: {lop.TENLOP}")

    malop = input("\nNhập mã lớp để xem sinh viên: ")
    svs = get_sinhvien(malop)
    print("\n=== Danh sách sinh viên ===")
    for sv in svs:
        print(f"MASV: {sv.MASV}, Họ tên: {sv.HOTEN}")

    # Nhập điểm cho sinh viên
    masv = input("\nNhập MASV cần nhập điểm: ")
    mahp = input("Nhập MAHP môn học: ")
    diemthi = float(input("Nhập điểm thi: "))
    insert_bangdiem(masv, mahp, diemthi, manv)
    print("Nhập điểm thành công, điểm đã được mã hóa!")
    
else:
    print("Đăng nhập thất bại!")

conn.close()
