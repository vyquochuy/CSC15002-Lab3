import tkinter as tk
from tkinter import messagebox
import db
import students_screen
import login_screen

def open_dashboard(manv):
    root = tk.Tk()
    root.title("Quản lý lớp học")

    classes = db.get_classes(manv)

    tk.Label(root, text="Các lớp bạn quản lý:").pack(pady=5)

    listbox = tk.Listbox(root, width=50)
    for lop in classes:
        listbox.insert(tk.END, f"{lop.MALOP} - {lop.TENLOP}")
    listbox.pack(pady=5)

    def open_students():
        selected = listbox.curselection()
        if selected:
            value = listbox.get(selected[0])
            malop = value.split(" - ")[0]
            root.destroy()
            students_screen.open_students(manv, malop)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp!")

    tk.Button(root, text="Xem sinh viên", command=open_students).pack(pady=5)
    tk.Button(root, text="Đăng xuất", command=lambda: logout(root)).pack(pady=5)

    root.mainloop()

def logout(current_root):
    current_root.destroy()
    login_screen.open_login()
