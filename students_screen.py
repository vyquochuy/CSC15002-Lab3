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
            info_window.geometry("400x300")

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
                tk.Label(info_window, text=f"{label_text}: {value}", anchor="w", justify="left", padx=10).pack(fill="x", pady=2)

    
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
                    

            tk.Button(score_window, text="Xác nhận", command=submit_score).pack(pady=10)

    def open_edit_info_screen():
        masv = get_selected_masv()
        if masv:
            
            edit_window = tk.Toplevel(stu)
            edit_window.title("Thay đổi thông tin sinh viên")
            edit_window.geometry("400x300")

            conn = db.get_connection()
            cursor = conn.cursor()
            # Sau khi fetch xong sinh viên
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

            entries = []  # List để lưu các Entry nếu cần dùng sau

            for label_text, value in zip(labels, values):
                tk.Label(edit_window, text=label_text + ":").pack()
                entry = tk.Entry(edit_window, width=50)
                entry.pack()
                entry.insert(0, value)
                entries.append(entry)  # Lưu entry vào list để dùng sau


            def submit_edit():
                field_names = ["hoten", "ngaysinh", "diachi", "malop", "tendn"]
                values = [entry.get().strip() for entry in entries[:5]]  
                if any(v == "" for v in values):
                    messagebox.showwarning("Cảnh báo", "Điền đầy đủ thông tin trước khi lưu!")
                    return

                # Unpack theo thứ tự
                hoten, ngaysinh, diachi, malop, tendn = values

                db.update_student(masv, hoten, ngaysinh, diachi, malop, tendn)
                messagebox.showinfo("Thông báo", "Cập nhật sinh viên thành công!")
                edit_window.destroy()
                stu.destroy()
                dashboard_screen.open_dashboard(manv)

            tk.Button(edit_window, text="Lưu thay đổi", command=submit_edit).pack(pady=10)
    
    def open_score_view():
        masv = get_selected_masv()
        if masv:
            pw_window = tk.Toplevel(stu)
            pw_window.title("Nhập mật khẩu để xem điểm")
            pw_window.geometry("300x150")

            tk.Label(pw_window, text="Mật khẩu:").pack()
            entry_pw = tk.Entry(pw_window, show="*")
            entry_pw.pack()
            
            def submit_pw():
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
                score_window.geometry("400x300")

                for row in scores:
                    line = f"Môn: {row.TENHP} ({row.MAHP}) - Điểm: {row.DIEM}"
                    tk.Label(score_window, text=line, anchor="w", padx=10).pack(fill="x", pady=2)

            tk.Button(pw_window, text="Xác nhận", command=submit_pw).pack(pady=10)

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
                    db.insert_score(masv, mahp, diemthi, manv)  # Gọi hàm insert_score đã tạo trong db.py
                    messagebox.showinfo("Thông báo", "Nhập điểm thành công!")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Lỗi khác: {e}")
                    
                score_window.destroy()



    tk.Button(stu, text="Xem thông tin chi tiết",width=30, command=open_view_info_screen).pack(pady=5)
    tk.Button(stu, text="Thay đổi thông tin sinh viên",width=30, command=open_edit_info_screen).pack(pady=5)
    tk.Button(stu, text="Nhập điểm cho sinh viên",width=30, command=open_insert_score_screen).pack(pady=5)
    tk.Button(stu, text="Xem điểm sinh viên", width=30, command=open_score_view).pack(pady=5)


    tk.Button(stu, text="Quay lại Dashboard",width=30, command=lambda: (stu.destroy(), dashboard_screen.open_dashboard(manv))).pack(pady=5)

    stu.mainloop()
