import tkinter as tk
from tkinter import messagebox
import db

def open_employees(manv):
    emp_window = tk.Tk()
    emp_window.title("Quản lý nhân viên")
    emp_window.geometry("500x500")

    # Hiển thị danh sách nhân viên
    employees = db.get_all_employees()  # Tạo hàm này trong db.py để lấy danh sách nhân viên

    listbox = tk.Listbox(emp_window, width=70)
    listbox.pack(pady=10)

    for emp in employees:
        listbox.insert(tk.END, f"{emp.MANV} - {emp.HOTEN}")

    # Thêm nút để thêm nhân viên mới
    def add_employee():
        def submit_employee():
            manv = entry_manv.get().strip()
            hoten = entry_hoten.get().strip()
            email = entry_email.get().strip()
            luong = entry_luong.get().strip()
            tendn = entry_tendn.get().strip()
            mk = entry_mk.get().strip()

            if not manv or not hoten or not email or not luong or not tendn or not mk:
                messagebox.showwarning("Cảnh báo", "Tất cả các trường không được để trống!")
                return

            try:
                luong = int(luong)  # Chuyển đổi lương sang số nguyên
                db.insert_nhanvien(manv, hoten, email, luong, tendn, mk, manv)  # Gọi hàm insert_nhanvien đã tạo trong db.py
                messagebox.showinfo("Thông báo", "Thêm nhân viên thành công!")
                emp_window.destroy()
                open_employees(manv)  # Cập nhật lại danh sách nhân viên
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm nhân viên: {e}")

        add_window = tk.Toplevel(emp_window)
        add_window.title("Thêm nhân viên")
        add_window.geometry("300x300")

        tk.Label(add_window, text="MANV:").pack(pady=5)
        entry_manv = tk.Entry(add_window)
        entry_manv.pack()

        tk.Label(add_window, text="Họ tên:").pack(pady=5)
        entry_hoten = tk.Entry(add_window)
        entry_hoten.pack()

        tk.Label(add_window, text="Email:").pack(pady=5)
        entry_email = tk.Entry(add_window)
        entry_email.pack()

        tk.Label(add_window, text="Lương:").pack(pady=5)
        entry_luong = tk.Entry(add_window)
        entry_luong.pack()

        tk.Label(add_window, text="Tên đăng nhập:").pack(pady=5)
        entry_tendn = tk.Entry(add_window)
        entry_tendn.pack()

        tk.Label(add_window, text="Mật khẩu:").pack(pady=5)
        entry_mk = tk.Entry(add_window, show="*")
        entry_mk.pack()

        tk.Button(add_window, text="Thêm", command=submit_employee).pack(pady=10)

    tk.Button(emp_window, text="Thêm nhân viên", command=add_employee).pack(pady=5)
    emp_window.mainloop()
