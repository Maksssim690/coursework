import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sqlite3
from openpyxl import Workbook

current_user_id = 1


themes = {
    "default": {
        "bg": "#f0f0f0",
        "fg": "black",
        "entry_bg": "white",
        "entry_fg": "black",
        "text_bg": "white",
        "text_fg": "black",
        "button_bg": "#e1e1e1",
        "button_fg": "black",
        "tree_bg": "white",
        "tree_fg": "black",
        "tree_heading_bg": "#e1e1e1",
        "tree_heading_fg": "black",
        "tab_bg": "#f0f0f0",
        "tab_fg": "black",
        "notebook_bg": "#f0f0f0",
        "notebook_fg": "black"
    },
    "dark": {
        "bg": "#2d2d2d",
        "fg": "#e0e0e0",
        "entry_bg": "#3d3d3d",
        "entry_fg": "white",
        "text_bg": "#3d3d3d",
        "text_fg": "white",
        "button_bg": "#3d3d3d",
        "button_fg": "white",
        "tree_bg": "#3d3d3d",
        "tree_fg": "white",
        "tree_heading_bg": "#2d2d2d",
        "tree_heading_fg": "white",
        "tab_bg": "#2d2d2d",
        "tab_fg": "white",
        "notebook_bg": "#2d2d2d",
        "notebook_fg": "white"
    },
    "cream": {
        "bg": "#fff5e6",
        "fg": "#5a3e36",
        "entry_bg": "white",
        "entry_fg": "black",
        "text_bg": "white",
        "text_fg": "black",
        "button_bg": "#e6d5c3",
        "button_fg": "#5a3e36",
        "tree_bg": "white",
        "tree_fg": "black",
        "tree_heading_bg": "#e6d5c3",
        "tree_heading_fg": "#5a3e36",
        "tab_bg": "#fff5e6",
        "tab_fg": "#5a3e36",
        "notebook_bg": "#fff5e6",
        "notebook_fg": "#5a3e36"
    },
    "contrast": {
        "bg": "black",
        "fg": "yellow",
        "entry_bg": "white",
        "entry_fg": "black",
        "text_bg": "white",
        "text_fg": "black",
        "button_bg": "yellow",
        "button_fg": "black",
        "tree_bg": "white",
        "tree_fg": "black",
        "tree_heading_bg": "yellow",
        "tree_heading_fg": "black",
        "tab_bg": "black",
        "tab_fg": "yellow",
        "notebook_bg": "black",
        "notebook_fg": "yellow"
    }
}

current_theme = "default"


#Функции для работы с пациентами
def on_add_patient():
    if add_patient(
            patient_name_entry.get(),
            patient_birth_entry.get(),
            patient_diag_entry.get(),
            patient_presc_entry.get(),
            patient_history_text.get("1.0", tk.END),
            doctor_combobox.get()
    ):
        clear_patient_entries()
        refresh_patients_tree()


def on_edit_patient():
    global selected_patient_id
    if selected_patient_id is None:
        messagebox.showwarning("Выбор", "Выберите пациента для редактирования")
        return
    if update_patient(
            selected_patient_id,
            patient_name_entry.get(),
            patient_birth_entry.get(),
            patient_diag_entry.get(),
            patient_presc_entry.get(),
            patient_history_text.get("1.0", tk.END),
            doctor_combobox.get()
    ):
        clear_patient_entries()
        refresh_patients_tree()
        selected_patient_id = None


def on_delete_patient():
    global selected_patient_id
    if selected_patient_id is None:
        messagebox.showwarning("Выбор", "Выберите пациента для удаления")
        return
    delete_patient(selected_patient_id)
    selected_patient_id = None
    clear_patient_entries()
    refresh_patients_tree()


def clear_patient_entries():
    patient_name_entry.delete(0, tk.END)
    patient_birth_entry.delete(0, tk.END)
    patient_diag_entry.delete(0, tk.END)
    patient_presc_entry.delete(0, tk.END)
    patient_history_text.delete("1.0", tk.END)
    doctor_combobox.set("")


def on_patient_select(event):
    global selected_patient_id
    selected = patients_tree.selection()
    if not selected:
        return
    values = patients_tree.item(selected[0])['values']
    selected_patient_id = values[0]

    patient_name_entry.delete(0, tk.END)
    patient_name_entry.insert(0, values[1])
    patient_birth_entry.delete(0, tk.END)
    patient_birth_entry.insert(0, values[2])
    patient_diag_entry.delete(0, tk.END)
    patient_diag_entry.insert(0, values[3])
    patient_presc_entry.delete(0, tk.END)
    patient_presc_entry.insert(0, values[4])
    patient_history_text.delete("1.0", tk.END)

    patient = get_patient_details(selected_patient_id)
    if patient and patient[5]:
        patient_history_text.insert(tk.END, patient[5])
    doctor_combobox.set(values[5] if values[5] else "")


def refresh_patients_tree():
    for row in patients_tree.get_children():
        patients_tree.delete(row)
    for pat in get_patients():
        patients_tree.insert("", "end", values=pat)


def refresh_doctors_combobox():
    doctors = get_doctors()
    doctor_combobox['values'] = [doc[1] for doc in doctors]


def show_patient_details():
    global selected_patient_id
    if selected_patient_id is None:
        messagebox.showwarning("Выбор", "Выберите пациента для просмотра")
        return

    patient = get_patient_details(selected_patient_id)
    if not patient:
        return


    details_window = tk.Toplevel(root)
    details_window.title(f"Карта пациента: {patient[1]}")
    details_window.geometry("700x700")


    theme = themes[current_theme]
    details_window.config(bg=theme["bg"])


    ttk.Label(details_window, text="ФИО пациента:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w",padx=10, pady=5)
    ttk.Label(details_window, text=patient[1]).grid(row=0, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(details_window, text="Дата рождения:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky="w",padx=10, pady=5)
    ttk.Label(details_window, text=patient[2]).grid(row=1, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(details_window, text="Лечащий врач:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky="w",padx=10, pady=5)
    ttk.Label(details_window, text=f"{patient[6]} ({patient[7]})" if patient[6] else "Не назначен").grid(row=2, column=1, sticky="w", padx=10,pady=5)

    ttk.Label(details_window, text="Диагноз:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky="w", padx=10,pady=5)
    ttk.Label(details_window, text=patient[3] if patient[3] else "Не указан").grid(row=3, column=1, sticky="w", padx=10,pady=5)

    ttk.Label(details_window, text="Рецепт:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky="w", padx=10,pady=5)
    ttk.Label(details_window, text=patient[4] if patient[4] else "Не указан").grid(row=4, column=1, sticky="w", padx=10,pady=5)

    ttk.Label(details_window, text="История болезни:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky="nw",padx=10, pady=5)
    history_text = scrolledtext.ScrolledText(details_window, width=60, height=15, wrap=tk.WORD)
    history_text.grid(row=5, column=1, sticky="we", padx=10, pady=5)
    history_text.insert(tk.END, patient[5] if patient[5] else "История болезни не заполнена")
    history_text.config(state=tk.DISABLED)

    ttk.Button(details_window, text="Закрыть", command=details_window.destroy).grid(row=6, column=1, sticky="e",padx=10, pady=10)


#Функции для работы с врачами
def on_add_doctor():
    full_name = doctor_name_entry.get()
    specialty = doctor_spec_entry.get()
    if add_doctor(full_name, specialty):
        doctor_name_entry.delete(0, tk.END)
        doctor_spec_entry.delete(0, tk.END)
        refresh_doctors_tree()
        refresh_doctors_combobox()


def on_delete_doctor():
    selected = doctors_tree.selection()
    if not selected:
        messagebox.showwarning("Выбор", "Выберите врача для удаления")
        return
    doctor_id = doctors_tree.item(selected[0])['values'][0]
    delete_doctor(doctor_id)
    refresh_doctors_tree()
    refresh_doctors_combobox()


def on_doctor_select(event):
    selected = doctors_tree.selection()
    if not selected:
        return
    doctor_id, full_name = doctors_tree.item(selected[0])['values'][0:2]
    doctor_name_entry.delete(0, tk.END)
    doctor_name_entry.insert(0, full_name)


def refresh_doctors_tree():
    for row in doctors_tree.get_children():
        doctors_tree.delete(row)
    for doc in get_doctors():
        doctors_tree.insert("", "end", values=(doc[0], doc[1]))


#Остальные функции
def apply_theme(theme_name):
    global current_theme
    current_theme = theme_name
    theme = themes[theme_name]

    root.config(bg=theme["bg"])
    style = ttk.Style()

    style.configure("TNotebook", background=theme["notebook_bg"])
    style.configure("TNotebook.Tab",
                    background=theme["tab_bg"],
                    foreground=theme["tab_fg"],
                    padding=[10, 5])
    style.map("TNotebook.Tab",
              background=[("selected", theme["bg"])],
              foreground=[("selected", theme["fg"])])

    style.configure("TFrame", background=theme["bg"])

    style.configure("TLabel",
                    background=theme["bg"],
                    foreground=theme["fg"])

    style.configure("TEntry",
                    fieldbackground=theme["entry_bg"],
                    foreground=theme["entry_fg"],
                    insertcolor=theme["entry_fg"])

    style.configure("TCombobox",
                    fieldbackground=theme["entry_bg"],
                    background=theme["entry_bg"],
                    foreground=theme["entry_fg"])

    style.configure("TButton",
                    background=theme["button_bg"],
                    foreground=theme["button_fg"],
                    borderwidth=1)
    style.map("TButton",
              background=[("active", theme["button_bg"])])

    style.configure("Treeview",
                    background=theme["tree_bg"],
                    foreground=theme["tree_fg"],
                    fieldbackground=theme["tree_bg"])
    style.configure("Treeview.Heading",
                    background=theme["tree_heading_bg"],
                    foreground=theme["tree_heading_fg"])

    update_widget_colors(root, theme)


def update_widget_colors(widget, theme):
    try:
        if isinstance(widget, (tk.Label, tk.Button)):
            widget.config(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, tk.Entry):
            widget.config(bg=theme["entry_bg"], fg=theme["entry_fg"],
                          insertbackground=theme["entry_fg"])
        elif isinstance(widget, tk.Text) or isinstance(widget, scrolledtext.ScrolledText):
            widget.config(bg=theme["text_bg"], fg=theme["text_fg"])
        elif isinstance(widget, tk.Frame) or isinstance(widget, ttk.Frame):
            widget.config(style="TFrame")
    except tk.TclError:
        pass

    for child in widget.winfo_children():
        update_widget_colors(child, theme)


def init_db():
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()

    #Таблица пользователей в бд
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Таблица врачей в бд
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            specialty TEXT
        )
    ''')

    # Таблица пациентов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            diagnosis TEXT,
            prescription TEXT,
            medical_history TEXT,
            doctor_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )
    ''')

    # Создаю фиктивного пользователя
    cursor.execute("SELECT id FROM users WHERE id = 1")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("user1", "pass"))
    conn.commit()
    conn.close()


def get_doctors():
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name FROM doctors")
    doctors = cursor.fetchall()
    conn.close()
    return doctors


def add_doctor(full_name, specialty):
    if not full_name.strip():
        messagebox.showerror("Ошибка", "Введите ФИО врача")
        return False
    if not specialty.strip():
        messagebox.showerror("Ошибка", "Введите специальность врача")
        return False
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO doctors (full_name, specialty) VALUES (?, ?)",
                   (full_name.lstrip().rstrip(), specialty.lstrip().rstrip()))
    conn.commit()
    conn.close()
    return True


def delete_doctor(doctor_id):
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients WHERE doctor_id = ?", (doctor_id,))
    patient_count = cursor.fetchone()[0]
    if patient_count > 0:
        messagebox.showerror("Ошибка", "Нельзя удалить врача, у которого есть пациенты")
        conn.close()
        return False
    cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
    conn.commit()
    conn.close()
    return True


def update_doctor(doctor_id, full_name, specialty):
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE doctors SET full_name = ?, specialty = ? WHERE id = ?",
                   (full_name.lstrip().rstrip(), specialty.lstrip().rstrip(), doctor_id))
    conn.commit()
    conn.close()


def add_patient(full_name, birth_date, diagnosis, prescription, medical_history, doctor_name):
    if not (full_name.strip() and birth_date.strip() and doctor_name.strip() and diagnosis.strip()):
        messagebox.showerror("Ошибка", "Заполните обязательные поля (ФИО, дата рождения, диагноз, врач)")
        return False

    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM doctors WHERE full_name = ?", (doctor_name,))
    doctor = cursor.fetchone()
    doctor_id = doctor[0] if doctor else None

    cursor.execute("""
        INSERT INTO patients (user_id, full_name, birth_date, diagnosis, prescription, medical_history, doctor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                   (current_user_id, full_name.lstrip().rstrip(), birth_date.lstrip().rstrip(),
                    diagnosis.lstrip().rstrip(), prescription.lstrip().rstrip(),
                    medical_history.lstrip().rstrip(), doctor_id))
    conn.commit()
    conn.close()
    return True


def delete_patient(patient_id):
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()


def update_patient(patient_id, full_name, birth_date, diagnosis, prescription, medical_history, doctor_name):
    if not full_name.strip() or not birth_date.strip():
        messagebox.showerror("Ошибка", "Введите ФИО и дату рождения пациента")
        return False

    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM doctors WHERE full_name = ?", (doctor_name,))
    doctor = cursor.fetchone()
    doctor_id = doctor[0] if doctor else None

    cursor.execute("""
        UPDATE patients
        SET full_name = ?, birth_date = ?, diagnosis = ?, prescription = ?, medical_history = ?, doctor_id = ?
        WHERE id = ?""",
                   (full_name.lstrip().rstrip(), birth_date.lstrip().rstrip(),
                    diagnosis.lstrip().rstrip(), prescription.lstrip().rstrip(),
                    medical_history.lstrip().rstrip(), doctor_id, patient_id))
    conn.commit()
    conn.close()
    return True


def get_patients():
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.full_name, p.birth_date, p.diagnosis, p.prescription, d.full_name
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.id
        WHERE p.user_id = ?
        """, (current_user_id,))
    patients = cursor.fetchall()
    conn.close()
    return patients


def get_patient_details(patient_id):
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.full_name, p.birth_date, p.diagnosis, p.prescription, p.medical_history, d.full_name, d.specialty
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.id
        WHERE p.id = ?
        """, (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    return patient


def export_doctors_to_excel():
    doctors = get_doctors()
    if not doctors:
        messagebox.showwarning("Экспорт", "Нет данных для экспорта")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")],
        title="Сохранить список врачей как"
    )

    if not file_path:
        return

    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Врачи"

        ws.append(["ID", "ФИО врача", "Специальность"])

        conn = sqlite3.connect("medical_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, specialty FROM doctors")
        doctors_full = cursor.fetchall()
        conn.close()

        for doctor in doctors_full:
            ws.append(doctor)

        wb.save(file_path)
        messagebox.showinfo("Экспорт", "Данные врачей успешно экспортированы в Excel")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")


def export_patients_to_excel():
    patients = get_patients()
    if not patients:
        messagebox.showwarning("Экспорт", "Нет данных для экспорта")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")],
        title="Сохранить список пациентов как"
    )

    if not file_path:
        return

    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Пациенты"

        ws.append(["ID", "ФИО пациента", "Дата рождения", "Диагноз", "Рецепт", "Лечащий врач"])

        conn = sqlite3.connect("medical_system.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.full_name, p.birth_date, p.diagnosis, p.prescription, 
                   COALESCE(d.full_name, 'Не назначен') as doctor_name
            FROM patients p
            LEFT JOIN doctors d ON p.doctor_id = d.id
            WHERE p.user_id = ?
        """, (current_user_id,))
        patients_full = cursor.fetchall()
        conn.close()

        for patient in patients_full:
            ws.append(patient)

        wb.save(file_path)
        messagebox.showinfo("Экспорт", "Данные пациентов успешно экспортированы в Excel")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")


#GUI
root = tk.Tk()
root.title("Медицинская система")
root.geometry("1000x1000")

style = ttk.Style()
style.theme_use("clam")

menubar = tk.Menu(root)
theme_menu = tk.Menu(menubar, tearoff=0)
theme_menu.add_command(label="Стандартная", command=lambda: apply_theme("default"))
theme_menu.add_command(label="Темная", command=lambda: apply_theme("dark"))
theme_menu.add_command(label="Кремовая", command=lambda: apply_theme("cream"))
theme_menu.add_command(label="Контрастная", command=lambda: apply_theme("contrast"))
menubar.add_cascade(label="Темы", menu=theme_menu)
root.config(menu=menubar)

tabs = ttk.Notebook(root)
tab_doctors = ttk.Frame(tabs)
tab_patients = ttk.Frame(tabs)

tabs.add(tab_doctors, text="Врачи")
tabs.add(tab_patients, text="Пациенты")
tabs.pack(expand=1, fill="both")



ttk.Label(tab_doctors, text="ФИО врача:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
doctor_name_entry = ttk.Entry(tab_doctors, width=40)
doctor_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

ttk.Label(tab_doctors, text="Специальность:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
doctor_spec_entry = ttk.Entry(tab_doctors, width=40)
doctor_spec_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)


btn_frame_doctors = ttk.Frame(tab_doctors)
btn_frame_doctors.grid(row=2, column=0, columnspan=2, pady=5)

ttk.Button(btn_frame_doctors, text="Добавить врача", command=on_add_doctor).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame_doctors, text="Удалить врача", command=on_delete_doctor).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame_doctors, text="Экспорт в Excel", command=export_doctors_to_excel).pack(side=tk.LEFT, padx=5)

doctors_tree = ttk.Treeview(tab_doctors, columns=("ID", "ФИО"), show="headings", height=15)
doctors_tree.heading("ID", text="ID")
doctors_tree.heading("ФИО", text="ФИО врача")
doctors_tree.column("ID", width=40)
doctors_tree.column("ФИО", width=250)
doctors_tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

scrollbar_doctors = ttk.Scrollbar(tab_doctors, orient="vertical", command=doctors_tree.yview)
scrollbar_doctors.grid(row=3, column=2, sticky="ns")
doctors_tree.configure(yscrollcommand=scrollbar_doctors.set)

doctors_tree.bind("<<TreeviewSelect>>", on_doctor_select)


ttk.Label(tab_patients, text="ФИО пациента:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
patient_name_entry = ttk.Entry(tab_patients, width=40)
patient_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

ttk.Label(tab_patients, text="Дата рождения:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
patient_birth_entry = ttk.Entry(tab_patients, width=40)
patient_birth_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

ttk.Label(tab_patients, text="Диагноз:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
patient_diag_entry = ttk.Entry(tab_patients, width=40)
patient_diag_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

ttk.Label(tab_patients, text="Рецепт:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
patient_presc_entry = ttk.Entry(tab_patients, width=40)
patient_presc_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

ttk.Label(tab_patients, text="История болезни:").grid(row=4, column=0, sticky="nw", padx=5, pady=5)
patient_history_text = scrolledtext.ScrolledText(tab_patients, width=37, height=5)
patient_history_text.grid(row=4, column=1, sticky="w", padx=5, pady=5)

ttk.Label(tab_patients, text="Врач:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
doctor_combobox = ttk.Combobox(tab_patients, state="readonly", width=38)
doctor_combobox.grid(row=5, column=1, sticky="w", padx=5, pady=5)


btn_frame_patients = ttk.Frame(tab_patients)
btn_frame_patients.grid(row=6, column=0, columnspan=2, pady=5)

ttk.Button(btn_frame_patients, text="Добавить пациента", command=on_add_patient).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame_patients, text="Редактировать пациента", command=on_edit_patient).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame_patients, text="Экспорт в Excel", command=export_patients_to_excel).pack(side=tk.LEFT, padx=5)

patients_tree = ttk.Treeview(tab_patients, columns=("ID", "ФИО", "Дата рождения", "Диагноз", "Рецепт", "Врач"),
                             show="headings", height=15)
patients_tree.heading("ID", text="ID")
patients_tree.heading("ФИО", text="ФИО пациента")
patients_tree.heading("Дата рождения", text="Дата рождения")
patients_tree.heading("Диагноз", text="Диагноз")
patients_tree.heading("Рецепт", text="Рецепт")
patients_tree.heading("Врач", text="Врач")

patients_tree.column("ID", width=40)
patients_tree.column("ФИО", width=180)
patients_tree.column("Дата рождения", width=100)
patients_tree.column("Диагноз", width=150)
patients_tree.column("Рецепт", width=150)
patients_tree.column("Врач", width=120)

patients_tree.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")


scrollbar_patients = ttk.Scrollbar(tab_patients, orient="vertical", command=patients_tree.yview)
scrollbar_patients.grid(row=7, column=2, sticky="ns")
patients_tree.configure(yscrollcommand=scrollbar_patients.set)

patients_tree.bind("<<TreeviewSelect>>", on_patient_select)


btn_frame_patients2 = ttk.Frame(tab_patients)
btn_frame_patients2.grid(row=8, column=0, columnspan=2, pady=5)

ttk.Button(btn_frame_patients2, text="Просмотр карты", command=show_patient_details).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame_patients2, text="Удалить пациента", command=on_delete_patient).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame_patients2, text="Очистить поля", command=clear_patient_entries).pack(side=tk.LEFT, padx=5)


tab_doctors.grid_rowconfigure(3, weight=1)
tab_doctors.grid_columnconfigure(1, weight=1)

tab_patients.grid_rowconfigure(7, weight=1)
tab_patients.grid_columnconfigure(1, weight=1)

#Запуск
init_db()
refresh_doctors_tree()
refresh_doctors_combobox()
refresh_patients_tree()
apply_theme("default")

root.mainloop()