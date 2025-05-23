import tkinter as tk
from tkinter import messagebox
import db
import dashboard_screen

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def open_employees(manv):
    emp_window = tk.Tk()
    emp_window.title("Quản lý nhân viên")
    center_window(emp_window, 500, 500)

    # Hiển thị danh sách nhân viên
    employees = db.get_all_employees()  # Tạo hàm này trong db.py để lấy danh sách nhân viên

    listbox = tk.Listbox(emp_window, width=70)
    listbox.pack(pady=10)

    for emp in employees:
        listbox.insert(tk.END, f"{emp.MANV} - {emp.HOTEN}")

    def get_selected_manv():
        selected = listbox.curselection()
        if selected:
            manv_selected = listbox.get(selected[0]).split(' - ')[0]
            return manv_selected
        else:
            messagebox.showwarning("Cảnh báo", "Chọn một nhân viên trước!")
            return None

    def view_employee_info():
        manv_selected = get_selected_manv()
        if manv_selected:
            def submit_pw(event=None):
                mk = entry_pw.get()
                try:
                    # Gọi stored procedure để lấy thông tin nhân viên với lương chưa giải mã
                    rows = db.select_nhanvien(manv_selected, mk)
                    if not rows:
                        pw_window.destroy()
                        messagebox.showerror("Lỗi", "Không tìm thấy hoặc mật khẩu sai.")
                        return
                    emp = rows[0]
                    info_window = tk.Toplevel(emp_window)
                    info_window.title("Thông tin nhân viên")
                    info_window.lift()
                    info_window.attributes('-topmost', True)
                    center_window(info_window, 400, 250)
                    labels = ["Mã NV", "Họ tên", "Email", "Lương (mã hóa)"]
                    # LUONG là giá trị chưa giải mã (dạng bytes)
                    values = [emp.MANV, emp.HOTEN, emp.EMAIL, str(emp.LUONG) if hasattr(emp, "LUONG") else "N/A"]
                    for label, value in zip(labels, values):
                        tk.Label(info_window, text=f"{label}: {value}", anchor="w", padx=10).pack(fill="x", pady=2)
                    pw_window.destroy()
                except Exception as e:
                    pw_window.destroy()
                    messagebox.showerror("Lỗi", f"Lỗi truy vấn: {e}")

            pw_window = tk.Toplevel(emp_window)
            pw_window.title("Nhập mật khẩu để xem thông tin")
            pw_window.lift()
            pw_window.attributes('-topmost', True)
            center_window(pw_window, 300, 120)
            tk.Label(pw_window, text="Mật khẩu:").pack(pady=5)
            entry_pw = tk.Entry(pw_window, show="*")
            entry_pw.pack()
            btn_xacnhan = tk.Button(pw_window, text="Xác nhận", command=submit_pw)
            btn_xacnhan.pack(pady=10)
            pw_window.bind('<Return>', submit_pw)
            entry_pw.focus_set()

    # Thêm nút để thêm nhân viên mới
    def add_employee():
        def submit_employee(event=None):
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
        center_window(add_window, 400, 350)  # Tăng kích thước cửa sổ

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

        btn_them = tk.Button(add_window, text="Thêm", command=submit_employee)
        btn_them.pack(pady=10)
        add_window.bind('<Return>', submit_employee)
        entry_manv.focus_set()

    btn_them_nv = tk.Button(emp_window, text="Thêm nhân viên", command=add_employee, width=20)
    btn_xem_nv = tk.Button(emp_window, text="Xem thông tin nhân viên", command=view_employee_info, width=20)
    btn_quay_lai = tk.Button(emp_window, text="Quay lại Dashboard", command=lambda: (emp_window.destroy(), dashboard_screen.open_dashboard(manv)), width=20)

    btn_them_nv.pack(pady=5)
    btn_xem_nv.pack(pady=5)
    btn_quay_lai.pack(pady=5)

    # Hỗ trợ Enter cho các nút chính
    emp_window.bind('<Return>', lambda event: btn_them_nv.invoke() if btn_them_nv == emp_window.focus_get() else
                                            btn_xem_nv.invoke() if btn_xem_nv == emp_window.focus_get() else
                                            btn_quay_lai.invoke() if btn_quay_lai == emp_window.focus_get() else None)

    emp_window.mainloop()
