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

def open_login():
    login_window = tk.Tk()
    login_window.title("Đăng nhập")
    login_window.lift()
    login_window.attributes('-topmost', True)
    login_window.after(100, lambda: login_window.attributes('-topmost', False))

    tk.Label(login_window, text="MANV:").pack(pady=10)
    manv_entry = tk.Entry(login_window)
    manv_entry.pack(pady=5)
    manv_entry.focus_set()

    tk.Label(login_window, text="Mật khẩu:").pack(pady=10)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    def handle_login(event=None):
        manv = manv_entry.get().upper()
        matkhau = password_entry.get()
        if db.login(manv, matkhau):
            messagebox.showinfo("Thông báo", "Đăng nhập thành công!")
            login_window.destroy()
            dashboard_screen.open_dashboard(manv)
        else:
            messagebox.showerror("Thông báo", "Đăng nhập thất bại!")

    btn = tk.Button(login_window, text="Đăng nhập", command=handle_login)
    btn.pack(pady=20)

    # Tab chuyển trường, Enter để đăng nhập
    manv_entry.bind('<Return>', lambda e: password_entry.focus_set())
    password_entry.bind('<Return>', lambda e: btn.focus_set())
    btn.bind('<Return>', handle_login)

    # Đảm bảo căn giữa sau khi tạo widget
    login_window.update_idletasks()
    center_window(login_window, 400, 250)

    login_window.mainloop()

if __name__ == "__main__":
    open_login()
