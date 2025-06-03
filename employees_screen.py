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
    center_window(emp_window, 700, 500)
    emp_window.lift()
    emp_window.attributes('-topmost', True)
    emp_window.after(100, lambda: emp_window.attributes('-topmost', False))

    listbox = tk.Listbox(emp_window, width=100)
    listbox.pack(pady=20)

    employee_tendn_map = {}

    def refresh_employee_list():
        listbox.delete(0, tk.END)
        employee_tendn_map.clear()
        employees = db.get_all_employees()
        for idx, emp in enumerate(employees):
            manv_val = emp.MANV if hasattr(emp, "MANV") else emp["MANV"]
            hoten_val = emp.HOTEN if hasattr(emp, "HOTEN") else emp["HOTEN"]
            tendn_val = emp.TENDN if hasattr(emp, "TENDN") else emp["TENDN"]
            listbox.insert(tk.END, f"{manv_val} - {hoten_val}")
            employee_tendn_map[idx] = tendn_val

    refresh_employee_list()

    def get_selected_tendn():
        selected = listbox.curselection()
        if selected:
            idx = selected[0]
            return employee_tendn_map.get(idx)
        else:
            messagebox.showwarning("Cảnh báo", "Chọn một nhân viên trước!")
            return None

    def view_employee_info():
        tendn_selected = get_selected_tendn()
        if tendn_selected:
            pw_window = tk.Toplevel(emp_window)
            pw_window.title("Nhập mật khẩu để xem thông tin")
            pw_window.lift()
            pw_window.attributes('-topmost', True)
            pw_window.after(100, lambda: pw_window.attributes('-topmost', False))
            pw_window.update_idletasks()
            center_window(pw_window, 350, 200)

            tk.Label(pw_window, text="Mật khẩu:").pack(pady=10)
            entry_pw = tk.Entry(pw_window, show="*")
            entry_pw.pack(pady=5)
            btn_xn = tk.Button(pw_window, text="Xác nhận")
            btn_xn.pack(pady=10)

            def submit_pw(event=None):
                mk = entry_pw.get()
                try:
                    rows = db.select_nhanvien(tendn_selected, mk)
                    if not rows:
                        pw_window.destroy()
                        messagebox.showerror("Lỗi", "Không tìm thấy hoặc mật khẩu sai.")
                        return
                    emp = rows[0]
                    info_window = tk.Toplevel(emp_window)
                    info_window.title("Thông tin nhân viên")
                    info_window.lift()
                    info_window.attributes('-topmost', True)
                    info_window.after(100, lambda: info_window.attributes('-topmost', False))
                    info_window.update_idletasks()
                    center_window(info_window, 500, 350)

                    labels = ["Mã NV", "Họ tên", "Email", "Lương (giải mã)"]
                    values = [emp["MANV"], emp["HOTEN"], emp["EMAIL"], emp["LUONG"]]

                    for label, value in zip(labels, values):
                        tk.Label(info_window, text=f"{label}: {value}", anchor="w", padx=10).pack(fill="x", pady=5)

                    pw_window.destroy()
                except Exception as e:
                    pw_window.destroy()
                    messagebox.showerror("Lỗi", f"Lỗi truy vấn: {e}")

            btn_xn.config(command=submit_pw)
            entry_pw.focus_set()
            entry_pw.bind('<Tab>', lambda e: btn_xn.focus_set())
            btn_xn.bind('<Return>', submit_pw)

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
                luong_int = int(luong)
                db.insert_nhanvien(manv, hoten, email, luong_int, tendn, mk, manv)
                messagebox.showinfo("Thông báo", "Thêm nhân viên thành công!")
                add_window.destroy()
                refresh_employee_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm nhân viên: {e}")

        add_window = tk.Toplevel(emp_window)
        add_window.title("Thêm nhân viên")
        add_window.lift()
        add_window.attributes('-topmost', True)
        add_window.after(100, lambda: add_window.attributes('-topmost', False))
        add_window.update_idletasks()
        center_window(add_window, 600, 500)

        tk.Label(add_window, text="MANV:").pack(pady=10)
        entry_manv = tk.Entry(add_window)
        entry_manv.pack(pady=5)
        tk.Label(add_window, text="Họ tên:").pack(pady=10)
        entry_hoten = tk.Entry(add_window)
        entry_hoten.pack(pady=5)
        tk.Label(add_window, text="Email:").pack(pady=10)
        entry_email = tk.Entry(add_window)
        entry_email.pack(pady=5)
        tk.Label(add_window, text="Lương:").pack(pady=10)
        entry_luong = tk.Entry(add_window)
        entry_luong.pack(pady=5)
        tk.Label(add_window, text="Tên đăng nhập:").pack(pady=10)
        entry_tendn = tk.Entry(add_window)
        entry_tendn.pack(pady=5)
        tk.Label(add_window, text="Mật khẩu:").pack(pady=10)
        entry_mk = tk.Entry(add_window, show="*")
        entry_mk.pack(pady=5)

        btn_them = tk.Button(add_window, text="Thêm")
        btn_them.pack(pady=20)

        def on_add_employee():
            submit_employee()

        btn_them.config(command=submit_employee)
        entry_manv.focus_set()
        entry_manv.bind('<Tab>', lambda e: entry_hoten.focus_set())
        entry_hoten.bind('<Tab>', lambda e: entry_email.focus_set())
        entry_email.bind('<Tab>', lambda e: entry_luong.focus_set())
        entry_luong.bind('<Tab>', lambda e: entry_tendn.focus_set())
        entry_tendn.bind('<Tab>', lambda e: entry_mk.focus_set())
        entry_mk.bind('<Tab>', lambda e: btn_them.focus_set())
        btn_them.bind('<Return>', submit_employee)

    def delete_employee():
        tendn_selected = get_selected_tendn()
        if not tendn_selected:
            return  # Đã có messagebox cảnh báo trong get_selected_tendn

        confirm_window = tk.Toplevel(emp_window)
        confirm_window.title("Xác nhận xóa nhân viên")
        confirm_window.lift()
        confirm_window.attributes('-topmost', True)
        confirm_window.after(100, lambda: confirm_window.attributes('-topmost', False))
        confirm_window.update_idletasks()
        center_window(confirm_window, 350, 150)

        tk.Label(confirm_window, text="Bạn có chắc chắn muốn xóa nhân viên này?", font=("Arial", 12)).pack(pady=20)
        btn_frame = tk.Frame(confirm_window)
        btn_frame.pack(pady=5)

        def do_delete():
            try:
                db.delete_employee(tendn_selected)
                messagebox.showinfo("Thành công", "Đã xóa nhân viên thành công!")
                confirm_window.destroy()
                refresh_employee_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa nhân viên: {e}")
                confirm_window.destroy()

        tk.Button(btn_frame, text="Xác nhận", command=do_delete, width=10).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=confirm_window.destroy, width=10).pack(side="right", padx=10)

    btn_add = tk.Button(emp_window, text="Thêm nhân viên", command=add_employee, width=30)
    btn_view = tk.Button(emp_window, text="Xem thông tin nhân viên", command=view_employee_info, width=30)
    btn_delete = tk.Button(emp_window, text="Xóa nhân viên", command=delete_employee, width=30)
    btn_back = tk.Button(emp_window, text="Quay lại Dashboard", command=lambda: (emp_window.destroy(), dashboard_screen.open_dashboard(manv)), width=30)

    btn_add.pack(pady=10)
    btn_view.pack(pady=10)
    btn_delete.pack(pady=10)
    btn_back.pack(pady=10)
    emp_window.update_idletasks()
    center_window(emp_window, 700, 500)
    emp_window.mainloop()
