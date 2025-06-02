import tkinter as tk
from tkinter import messagebox
import db
import login_screen
import students_screen
import employees_screen

# Danh sách các MANV có quyền quản lý nhân viên (bạn có thể cập nhật hoặc lấy từ DB khi cần)
ADMIN_MANV_LIST = ['NV01', 'NV02']  # Ví dụ các MANV được phép quản lý nhân viên

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def open_dashboard(manv):
    dash = tk.Tk()
    dash.title("Dashboard - Danh sách lớp")
    center_window(dash, 500, 500)

    tk.Label(dash, text=f"Xin chào {manv}", font=("Arial", 14)).pack(pady=10)

    classes = db.get_all_classes()

    listbox = tk.Listbox(dash, width=70)
    listbox.pack(pady=10)

    for lop in classes:
        listbox.insert(tk.END, f"{lop.MALOP} - {lop.TENLOP} (Quản lý: {lop.MANV})")

    def open_students():
        selected = listbox.curselection()
        
        if selected:
            line = listbox.get(selected[0])
            parts = line.split(' - ')
            malop = parts[0].strip()
            manv_lop = parts[1].split('(Quản lý:')[1].replace(')', '').strip()

            if manv != manv_lop:
                messagebox.showerror("Cấm truy cập", "Bạn không có quyền xem danh sách sinh viên của lớp này!")
                return
            
            dash.destroy()
            students_screen.open_students(manv, malop, manv_lop)
        else:
            messagebox.showwarning("Cảnh báo", "Chọn một lớp trước!")

    def open_employees():
        dash.destroy()
        employees_screen.open_employees(manv)

    tk.Button(dash, text="Xem sinh viên", command=open_students, width=20).pack(pady=5)
    tk.Button(dash, text="Quản lý nhân viên", command=open_employees, width=20).pack(pady=5)
    tk.Button(dash, text="Đăng xuất", command=lambda: (dash.destroy(), login_screen.open_login()), width=20).pack(pady=5)
    
    dash.mainloop()