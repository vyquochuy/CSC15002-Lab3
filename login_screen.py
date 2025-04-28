import tkinter as tk
from tkinter import messagebox
import db
import dashboard_screen

def open_login():
    login_window = tk.Tk()
    login_window.title("Đăng nhập")
    login_window.geometry("300x200")

    tk.Label(login_window, text="MANV:").pack(pady=5)
    manv_entry = tk.Entry(login_window)
    manv_entry.pack()

    tk.Label(login_window, text="Mật khẩu:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    def handle_login():
        manv = manv_entry.get().upper()
        matkhau = password_entry.get()
        if db.login(manv, matkhau):
            messagebox.showinfo("Thông báo", "Đăng nhập thành công!")
            login_window.destroy()
            dashboard_screen.open_dashboard(manv)
        else:
            messagebox.showerror("Thông báo", "Đăng nhập thất bại!")

    tk.Button(login_window, text="Đăng nhập", command=handle_login).pack(pady=10)

    login_window.mainloop()

if __name__ == "__main__":
    open_login()
