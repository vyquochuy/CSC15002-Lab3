import tkinter as tk
from tkinter import messagebox
import db
import dashboard_screen

def open_students(manv, malop):
    stu = tk.Tk()
    stu.title(f"Danh sách sinh viên lớp {malop}")
    stu.geometry("500x500")

    tk.Label(stu, text=f"Lớp: {malop}", font=("Arial", 14)).pack(pady=10)

    students = db.get_students(malop)

    listbox = tk.Listbox(stu, width=60)
    listbox.pack(pady=10)

    for sv in students:
        listbox.insert(tk.END, f"{sv.MASV} - {sv.HOTEN}")

    def insert_score():
        selected = listbox.curselection()
        if selected:
            masv = listbox.get(selected[0]).split(' - ')[0]
            mahp = entry_mahp.get().strip()
            diemthi_str = entry_diem.get().strip()

            if not mahp or not diemthi_str:
                messagebox.showwarning("Cảnh báo", "Mã học phần và điểm thi không được để trống!")
                return
            
            try:
                diemthi = float(diemthi_str)
            except ValueError:
                messagebox.showerror("Lỗi", "Điểm thi phải là số!")
                return

            try:
                db.insert_score(masv, mahp, diemthi, manv)
                messagebox.showinfo("Thông báo", "Nhập điểm thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khác: {e}")
        else:
            messagebox.showwarning("Cảnh báo", "Chọn sinh viên trước!")



    tk.Label(stu, text="Mã học phần:").pack()
    entry_mahp = tk.Entry(stu)
    entry_mahp.pack()

    tk.Label(stu, text="Điểm thi:").pack()
    entry_diem = tk.Entry(stu)
    entry_diem.pack()

    tk.Button(stu, text="Nhập điểm", command=insert_score).pack(pady=10)
    tk.Button(stu, text="Quay lại Dashboard", command=lambda: (stu.destroy(), dashboard_screen.open_dashboard(manv))).pack(pady=5)

    stu.mainloop()
