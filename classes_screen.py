import tkinter as tk
from tkinter import messagebox
import db

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def open_classes(manv):
    class_window = tk.Tk()
    class_window.title("Quản lý lớp học")
    center_window(class_window, 500, 500)

    # Hiển thị danh sách lớp học
    classes = db.get_all_classes()  # Tạo hàm này trong db.py để lấy danh sách lớp học

    listbox = tk.Listbox(class_window, width=70)
    listbox.pack(pady=10)

    for cls in classes:
        listbox.insert(tk.END, f"{cls.MALOP} - {cls.TENLOP} (Quản lý: {cls.MANV})")

    # Thêm nút để thêm lớp học mới
    def add_class():
        def submit_class():
            malop = entry_malop.get().strip()
            tenlop = entry_tenlop.get().strip()

            if not malop or not tenlop:
                messagebox.showwarning("Cảnh báo", "Mã lớp và tên lớp không được để trống!")
                return

            try:
                db.insert_class(malop, tenlop, manv)  # Gọi hàm insert_class đã tạo trong db.py
                messagebox.showinfo("Thông báo", "Thêm lớp học thành công!")
                class_window.destroy()
                open_classes(manv)  # Cập nhật lại danh sách lớp học
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm lớp học: {e}")

        add_window = tk.Toplevel(class_window)
        add_window.title("Thêm lớp học")
        center_window(add_window, 300, 200)

        tk.Label(add_window, text="Mã lớp:").pack(pady=5)
        entry_malop = tk.Entry(add_window)
        entry_malop.pack()

        tk.Label(add_window, text="Tên lớp:").pack(pady=5)
        entry_tenlop = tk.Entry(add_window)
        entry_tenlop.pack()

        tk.Button(add_window, text="Thêm", command=submit_class).pack(pady=10)

    tk.Button(class_window, text="Thêm lớp học", command=add_class).pack(pady=5)
    class_window.mainloop()
