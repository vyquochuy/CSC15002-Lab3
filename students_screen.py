import tkinter as tk
from tkinter import messagebox
import db
import dashboard_screen

def open_students(manv, malop, manv_lop):
    stu = tk.Tk()
    stu.title(f"Danh sách sinh viên lớp {malop}")
    stu.geometry("500x500")

    tk.Label(stu, text=f"Lớp: {malop} (Quản lý bởi {manv_lop})", font=("Arial", 14)).pack(pady=10)

    students = db.get_students(malop)

    listbox = tk.Listbox(stu, width=70)
    listbox.pack(pady=10)

    for sv in students:
        listbox.insert(tk.END, f"{sv.MASV} - {sv.HOTEN}")

    is_editable = (manv == manv_lop)

    selected_masv = tk.StringVar()

    def get_selected_masv():
        selected = listbox.curselection()
        if selected:
            masv = listbox.get(selected[0]).split(' - ')[0]
            selected_masv.set(masv)
            return masv
        else:
            messagebox.showwarning("Cảnh báo", "Chọn một sinh viên trước!")
            return None

    def open_insert_score_screen():
        masv = get_selected_masv()
        if masv:
            score_window = tk.Toplevel(stu)
            score_window.title("Nhập điểm")
            score_window.geometry("300x200")

            tk.Label(score_window, text="Mã học phần:").pack()
            entry_mahp = tk.Entry(score_window)
            entry_mahp.pack()

            tk.Label(score_window, text="Điểm thi:").pack()
            entry_diem = tk.Entry(score_window)
            entry_diem.pack()

            def submit_score():
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
                    score_window.destroy()
                except Exception as e:
                    if "PRIMARY KEY" in str(e):
                        messagebox.showerror("Lỗi", "Sinh viên này đã có điểm học phần này rồi!")
                    else:
                        messagebox.showerror("Lỗi", f"Lỗi khác: {e}")

            tk.Button(score_window, text="Xác nhận", command=submit_score).pack(pady=10)

    def open_edit_info_screen():
        masv = get_selected_masv()
        if masv:
            
            edit_window = tk.Toplevel(stu)
            edit_window.title("Thay đổi thông tin sinh viên")
            edit_window.geometry("400x300")

            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT HOTEN, NGAYSINH, DIACHI FROM SINHVIEN WHERE MASV = ?", (masv,))
            sv = cursor.fetchone()
            conn.close()

            tk.Label(edit_window, text="Họ tên:").pack()
            entry_hoten = tk.Entry(edit_window, width=50)
            entry_hoten.pack()
            entry_hoten.insert(0, sv.HOTEN)

            tk.Label(edit_window, text="Ngày sinh (YYYY-MM-DD):").pack()
            entry_ngaysinh = tk.Entry(edit_window, width=50)
            entry_ngaysinh.pack()
            entry_ngaysinh.insert(0, str(sv.NGAYSINH).split(' ')[0])

            tk.Label(edit_window, text="Địa chỉ:").pack()
            entry_diachi = tk.Entry(edit_window, width=50)
            entry_diachi.pack()
            entry_diachi.insert(0, sv.DIACHI)

            def submit_edit():
                hoten = entry_hoten.get().strip()
                ngaysinh = entry_ngaysinh.get().strip()
                diachi = entry_diachi.get().strip()

                if not hoten or not ngaysinh or not diachi:
                    messagebox.showwarning("Cảnh báo", "Điền đầy đủ thông tin trước khi lưu!")
                    return

                db.update_student(masv, hoten, ngaysinh, diachi)
                messagebox.showinfo("Thông báo", "Cập nhật sinh viên thành công!")
                edit_window.destroy()
                stu.destroy()
                dashboard_screen.open_dashboard(manv)

            tk.Button(edit_window, text="Lưu thay đổi", command=submit_edit).pack(pady=10)

    tk.Button(stu, text="Nhập điểm cho sinh viên", command=open_insert_score_screen).pack(pady=5)
    tk.Button(stu, text="Thay đổi thông tin sinh viên", command=open_edit_info_screen).pack(pady=5)
    tk.Button(stu, text="Quay lại Dashboard", command=lambda: (stu.destroy(), dashboard_screen.open_dashboard(manv))).pack(pady=5)

    stu.mainloop()
