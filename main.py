import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib

#Инициализация базы данных
def init_db():
    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    #Создаю таблицу пользователей, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      full_name TEXT NOT NULL,
                      username TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL)''')
    #Создаю таблицу пациентов, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      full_name TEXT NOT NULL,
                      birth_date TEXT NOT NULL,
                      diagnosis TEXT,
                      prescription TEXT,
                      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    conn.commit()
    conn.close()

#Переменная для хранения ID текущего пользователя
current_user_id = None

#хеширование пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#Регистрация нового пользователя
def register_user():
    full_name = entry_fullname.get()
    username = entry_username.get()
    password = entry_password.get()

    #Проверка на заполненность всех полей
    if not (full_name and username and password):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
        return

    hashed_password = hash_password(password)
    try:
        conn = sqlite3.connect("medical_system.db")
        cursor = conn.cursor()
        #Добавление нового пользователя в таблицу
        cursor.execute("INSERT INTO users (full_name, username, password) VALUES (?, ?, ?)",(full_name, username, hashed_password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Регистрация прошла успешно!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")

#Авторизация пользвателя
def login_user():
    global current_user_id
    username = entry_login_username.get()
    password = entry_login_password.get()
    hashed_password = hash_password(password)

    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    #Поиск по логину и паролю
    cursor.execute("SELECT id, full_name FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()

    if user:
        current_user_id = user[0]
        messagebox.showinfo("Успех", f"Добро пожаловать, {user[1]}!")
        root.title("Медицинская система | Управление пациентами")
        show_patient_management()
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

#Очистка полей ввода пациентов
def clear_patient_fields():
    entry_patient_fullname.delete(0, tk.END)
    entry_patient_birthdate.delete(0, tk.END)
    entry_patient_diagnosis.delete(0, tk.END)
    entry_patient_prescription.delete(0, tk.END)

#Добавление пациента
def add_patient():
    if current_user_id is None:
        messagebox.showerror("Ошибка", "Вы не авторизованы!")
        return

    full_name = entry_patient_fullname.get()
    birth_date = entry_patient_birthdate.get()
    diagnosis = entry_patient_diagnosis.get()
    prescription = entry_patient_prescription.get()

    #проверка на заполненность полей при добавлении пациента
    if not (full_name and birth_date and diagnosis and prescription):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
        return

    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    #Вставка нового пациента в таблицу в БД
    cursor.execute("INSERT INTO patients (user_id, full_name, birth_date, diagnosis, prescription) VALUES (?, ?, ?, ?, ?)",(current_user_id, full_name, birth_date, diagnosis, prescription))

    conn.commit()
    conn.close()

    messagebox.showinfo("Успех", "Пациент успешно добавлен!")

    view_patients()

#Удаление пациента
def delete_patient():
    if current_user_id is None:
        messagebox.showerror("Ошибка", "Вы не авторизованы!")
        return

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите пациента для удаления")
        return

    patient_id = tree.item(selected_item, "values")[4]

    confirmation = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить пациента?")
    if confirmation:
        conn = sqlite3.connect("medical_system.db")
        cursor = conn.cursor()
        #Удаление пациента из таблицы в БД
        cursor.execute("DELETE FROM patients WHERE id = ? AND user_id = ?", (patient_id, current_user_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Пациент удалён!")
        view_patients()

#Отображение списка пациентов
def view_patients():
    if current_user_id is None:
        return

    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    #Получение списка пациентов для текущего пользователя
    cursor.execute("SELECT id, full_name, birth_date, diagnosis, prescription FROM patients WHERE user_id = ?",
                   (current_user_id,))
    patients = cursor.fetchall()
    conn.close()

    for patient in patients:
        tree.insert("", "end", values=(patient[1], patient[2], patient[3], patient[4], patient[0]))

#Выбор пациента из списка
def select_patient(event):
    selected_item = tree.focus()
    if not selected_item:
        return

    values = tree.item(selected_item, "values")

    if values:
        entry_patient_fullname.delete(0, tk.END)
        entry_patient_fullname.insert(0, values[0])

        entry_patient_birthdate.delete(0, tk.END)
        entry_patient_birthdate.insert(0, values[1])

        entry_patient_diagnosis.delete(0, tk.END)
        entry_patient_diagnosis.insert(0, values[2])

        entry_patient_prescription.delete(0, tk.END)
        entry_patient_prescription.insert(0, values[3])

#Редактирование данных пациента
def edit_patient():
    if current_user_id is None:
        messagebox.showerror("Ошибка", "Вы не авторизованы!")
        return

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите пациента для редактирования")
        return

    patient_id = tree.item(selected_item, "values")[4]
    full_name = entry_patient_fullname.get()
    birth_date = entry_patient_birthdate.get()
    diagnosis = entry_patient_diagnosis.get()
    prescription = entry_patient_prescription.get()

    conn = sqlite3.connect("medical_system.db")
    cursor = conn.cursor()
    #Обновление данных пациента в БД
    cursor.execute("UPDATE patients SET full_name = ?, birth_date = ?, diagnosis = ?, prescription = ? "
                   "WHERE id = ? AND user_id = ?", (full_name, birth_date, diagnosis, prescription, patient_id, current_user_id))
    conn.commit()
    conn.close()

    messagebox.showinfo("Успех", "Данные пациента обновлены!")
    view_patients()

#Интерфейс управления пациентами
def show_patient_management():
    global entry_patient_fullname, entry_patient_birthdate, entry_patient_diagnosis, entry_patient_prescription, tree

    for widget in root.winfo_children():
        widget.destroy()

    tabs = ttk.Notebook(root)

    frame_patient_manage = ttk.Frame(tabs)
    tabs.add(frame_patient_manage, text="Управление пациентами")
    tabs.pack(expand=1, fill="both")

    ttk.Label(frame_patient_manage, text="ФИО пациента:").pack(pady=5)
    entry_patient_fullname = ttk.Entry(frame_patient_manage)
    entry_patient_fullname.pack(pady=5)

    ttk.Label(frame_patient_manage, text="Дата рождения (ДД-ММ-ГГГГ):").pack(pady=5)
    entry_patient_birthdate = ttk.Entry(frame_patient_manage)
    entry_patient_birthdate.pack(pady=5)

    ttk.Label(frame_patient_manage, text="Диагноз:").pack(pady=5)
    entry_patient_diagnosis = ttk.Entry(frame_patient_manage)
    entry_patient_diagnosis.pack(pady=5)

    ttk.Label(frame_patient_manage, text="Рецепт:").pack(pady=5)
    entry_patient_prescription = ttk.Entry(frame_patient_manage)
    entry_patient_prescription.pack(pady=5)

    tk.Button(frame_patient_manage, text="Добавить пациента", command=add_patient, fg="green").pack(pady=10)
    tk.Button(frame_patient_manage, text="Удалить пациента", command=delete_patient, fg="red").pack(pady=10)
    tk.Button(frame_patient_manage, text="Очистить поля", command=clear_patient_fields, fg="red").pack(pady=10)


    tree = ttk.Treeview(frame_patient_manage, columns=("Full Name", "Birth Date", "Diagnosis", "Prescription", "ID"),
                        show="headings")
    tree.heading("Full Name", text="ФИО")
    tree.heading("Birth Date", text="Дата рождения")
    tree.heading("Diagnosis", text="Диагноз")
    tree.heading("Prescription", text="Рецепт")
    tree.heading("ID", text="ID")
    tree.bind("<<TreeviewSelect>>", select_patient)
    tree.pack(pady=20)


    tk.Button(frame_patient_manage, text="Редактировать данные", command=edit_patient, fg="#cc4100").pack(pady=10)

    view_patients()


#Главное окно приложения
root = tk.Tk()
root.title("Медицинская система | Вход и Регистрация")
root.geometry("600x500")
tabs = ttk.Notebook(root)
frame_login = ttk.Frame(tabs)
frame_register = ttk.Frame(tabs)
tabs.add(frame_login, text="Авторизация")
tabs.add(frame_register, text="Регистрация")
tabs.pack(expand=1, fill="both")

ttk.Label(frame_login, text="Логин:").pack(pady=5)
entry_login_username = ttk.Entry(frame_login)
entry_login_username.pack(pady=5)

ttk.Label(frame_login, text="Пароль:").pack(pady=5)
entry_login_password = ttk.Entry(frame_login, show="*")
entry_login_password.pack(pady=5)

tk.Button(frame_login, text="Войти", command=login_user, fg="blue").pack(pady=10)

ttk.Label(frame_register, text="ФИО:").pack(pady=5)
entry_fullname = ttk.Entry(frame_register)
entry_fullname.pack(pady=5)

ttk.Label(frame_register, text="Логин:").pack(pady=5)
entry_username = ttk.Entry(frame_register)
entry_username.pack(pady=5)

ttk.Label(frame_register, text="Пароль:").pack(pady=5)
entry_password = ttk.Entry(frame_register, show="*")
entry_password.pack(pady=5)

tk.Button(frame_register, text="Зарегистрироваться", command=register_user, fg="blue").pack(pady=10)

#Вызов функции инициализации базы данных и запуск самого приложения
init_db()
root.mainloop()