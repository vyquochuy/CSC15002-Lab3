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

def open_students(manv, malop, manv_lop):
    stu = tk.Tk()
    stu.title(f"Danh sách sinh viên lớp {malop}")
    center_window(stu, 800, 600)
    stu.lift()
    stu.attributes('-topmost', True)
    stu.after(100, lambda: stu.attributes('-topmost', False))

    tk.Label(stu, text=f"Lớp: {malop} (Quản lý bởi {manv_lop})", font=("Arial", 18)).pack(pady=20)

    students = db.get_students(malop)

    listbox = tk.Listbox(stu, width=100)
    listbox.pack(pady=20)

    for sv in students:
        listbox.insert(tk.END, f"{sv.MASV} - {sv.HOTEN}")

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

    def open_view_info_screen():
        masv = get_selected_masv()
        if masv:
            info_window = tk.Toplevel(stu)
            info_window.title("Thông tin chi tiết sinh viên")
            info_window.lift()
            info_window.attributes('-topmost', True)
            info_window.after(100, lambda: info_window.attributes('-topmost', False))

            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT HOTEN, NGAYSINH, DIACHI, MALOP, TENDN FROM SINHVIEN WHERE MASV = ?", (masv,))
            sv = cursor.fetchone()
            conn.close()

            labels = ["Họ tên", "Ngày sinh", "Địa chỉ", "Mã lớp", "Tên đăng nhập"]
            values = [
                sv.HOTEN,
                str(sv.NGAYSINH).split(' ')[0],
                sv.DIACHI,
                sv.MALOP,
                sv.TENDN
            ]

            for label_text, value in zip(labels, values):
                tk.Label(info_window, text=f"{label_text}: {value}", anchor="w", justify="left", padx=10).pack(fill="x", pady=5)

            # Chỉ gọi 1 lần sau khi tạo widget
            info_window.update_idletasks()
            center_window(info_window, 400, 350)

    def open_insert_score_screen():
        masv = get_selected_masv()
        if masv:
            score_window = tk.Toplevel(stu)
            score_window.title("Nhập điểm")
            score_window.lift()
            score_window.attributes('-topmost', True)
            score_window.after(100, lambda: score_window.attributes('-topmost', False))

            tk.Label(score_window, text="Mã học phần:").pack(pady=10)
            entry_mahp = tk.Entry(score_window)
            entry_mahp.pack(pady=5)

            tk.Label(score_window, text="Điểm thi:").pack(pady=10)
            entry_diem = tk.Entry(score_window)
            entry_diem.pack(pady=5)

            btn_xn = tk.Button(score_window, text="Xác nhận")
            btn_xn.pack(pady=20)

            def submit_score(event=None):
                mahp = entry_mahp.get().strip().upper()
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
                    if "PRIMARY KEY" in str(e):
                        messagebox.showerror("Lỗi", "Sinh viên này đã có điểm học phần này rồi!")
                    else:
                        messagebox.showerror("Lỗi", f"Lỗi khác: {e}")
                score_window.destroy()

            entry_mahp.focus_set()
            entry_mahp.bind('<Tab>', lambda e: entry_diem.focus_set())
            entry_diem.bind('<Tab>', lambda e: btn_xn.focus_set())
            btn_xn.bind('<Return>', submit_score)
            btn_xn.config(command=submit_score)

            score_window.update_idletasks()
            center_window(score_window, 400, 350)

    def open_edit_info_screen():
        masv = get_selected_masv()
        if masv:
            edit_window = tk.Toplevel(stu)
            edit_window.title("Thay đổi thông tin sinh viên")
            edit_window.lift()
            edit_window.attributes('-topmost', True)
            edit_window.after(100, lambda: edit_window.attributes('-topmost', False))

            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT HOTEN, NGAYSINH, DIACHI, MALOP, TENDN, MATKHAU FROM SINHVIEN WHERE MASV = ?", (masv,))
            sv = cursor.fetchone()
            conn.close()

            labels = ["Họ tên", "Ngày sinh (YYYY-MM-DD)", "Địa chỉ", "Mã lớp", "Tên đăng nhập"]
            values = [
                sv.HOTEN,
                str(sv.NGAYSINH).split(' ')[0],
                sv.DIACHI,
                sv.MALOP,
                sv.TENDN
            ]

            entries = []
            for label_text, value in zip(labels, values):
                tk.Label(edit_window, text=label_text + ":").pack(pady=5)
                entry = tk.Entry(edit_window, width=80)
                entry.pack(pady=5)
                entry.insert(0, value)
                entries.append(entry)

            btn_save = tk.Button(edit_window, text="Lưu thay đổi")
            btn_save.pack(pady=20)

            def submit_edit(event=None):
                values = [entry.get().strip() for entry in entries[:5]]
                if any(v == "" for v in values):
                    messagebox.showwarning("Cảnh báo", "Điền đầy đủ thông tin trước khi lưu!")
                    return
                hoten, ngaysinh, diachi, malop, tendn = values
                db.update_student(masv, hoten, ngaysinh, diachi, malop, tendn)
                messagebox.showinfo("Thông báo", "Cập nhật sinh viên thành công!")
                edit_window.destroy()
                stu.destroy()
                dashboard_screen.open_dashboard(manv)

            entries[0].focus_set()
            for i in range(len(entries)-1):
                entries[i].bind('<Tab>', lambda e, idx=i: entries[idx+1].focus_set())
            entries[-1].bind('<Tab>', lambda e: btn_save.focus_set())
            btn_save.bind('<Return>', submit_edit)
            btn_save.config(command=submit_edit)

            # Chỉ gọi 1 lần sau khi tạo widget, tăng kích thước cho đủ
            edit_window.update_idletasks()
            center_window(edit_window, 600, 400)

    def open_score_view():
        masv = get_selected_masv()
        if masv:
            pw_window = tk.Toplevel(stu)
            pw_window.title("Nhập mật khẩu để xem điểm")
            pw_window.lift()
            pw_window.attributes('-topmost', True)
            pw_window.after(100, lambda: pw_window.attributes('-topmost', False))

            tk.Label(pw_window, text="Mật khẩu:").pack(pady=10)
            entry_pw = tk.Entry(pw_window, show="*")
            entry_pw.pack(pady=5)
            btn_xn = tk.Button(pw_window, text="Xác nhận")
            btn_xn.pack(pady=20)

            def submit_pw(event=None):
                matkhau = entry_pw.get()
                try:
                    scores = db.get_scores(masv, manv, matkhau)
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Lỗi giải mã hoặc mật khẩu không đúng.\nChi tiết: {e}")
                    pw_window.destroy()
                    return
                pw_window.destroy()
                score_window = tk.Toplevel(stu)
                score_window.title("Bảng điểm")
                score_window.lift()
                score_window.attributes('-topmost', True)
                score_window.after(100, lambda: score_window.attributes('-topmost', False))
                for row in scores:
                    line = f"Môn: {row[1]} ({row[0]}) - Điểm: {row[2]}"
                    tk.Label(score_window, text=line, anchor="w", padx=10).pack(fill="x", pady=5)
                # Chỉ gọi 1 lần sau khi tạo widget, tăng kích thước cho đủ
                score_window.update_idletasks()
                center_window(score_window, 500, 350)

            entry_pw.focus_set()
            entry_pw.bind('<Tab>', lambda e: btn_xn.focus_set())
            btn_xn.bind('<Return>', submit_pw)
            btn_xn.config(command=submit_pw)

            # Chỉ gọi 1 lần sau khi tạo widget
            pw_window.update_idletasks()
            center_window(pw_window, 350, 200)

    btn_view = tk.Button(stu, text="Xem thông tin chi tiết", width=40, command=open_view_info_screen)
    btn_edit = tk.Button(stu, text="Thay đổi thông tin sinh viên", width=40, command=open_edit_info_screen)
    btn_score = tk.Button(stu, text="Nhập điểm cho sinh viên", width=40, command=open_insert_score_screen)
    btn_view_score = tk.Button(stu, text="Xem điểm sinh viên", width=40, command=open_score_view)
    btn_back = tk.Button(stu, text="Quay lại Dashboard", width=40, command=lambda: (stu.destroy(), dashboard_screen.open_dashboard(manv)))

    btn_view.pack(pady=10)
    btn_edit.pack(pady=10)
    btn_score.pack(pady=10)
    btn_view_score.pack(pady=10)
    btn_back.pack(pady=10)

    # Đảm bảo căn giữa sau khi tạo widget
    stu.update_idletasks()
    center_window(stu, 800, 600)

    stu.mainloop()
