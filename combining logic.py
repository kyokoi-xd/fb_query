import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fdb
import os
import json
from prettytable import PrettyTable

def save_config():
    connection_type = connection_type_var.get()
    config  = {}

    if connection_type == "local":
        config["host"] = 'localhost'
        config["database"] = local_db_path_var.get()
    else:
        config["host"] = remote_host_var.get()
        config["database"] = remote_db_name_var.get()

    config["user"] = user_var.get()
    config["password"] = password_var.get()
    config["charset"]  = "UTF-8"

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    messagebox.showinfo("Успех", "Конфигурация сохранена")

def browse_file():
    file_path = filedialog.askopenfilename(title="Выберите файл базы данных", filetypes=[("FDB файлы", "*.fdb")])
    local_db_path_var.set(file_path)

def dynamic_interface():
    if connection_type_var.get() == "local":
        local_frame.pack(fill="x", pady=10)
        remote_frame.pack_forget()
    else:
        local_frame.pack_forget()
        remote_frame.pack(fill="x", pady=10)

def load_config(config_path="config.json"):
    if not os.path.exists(config_path):
        raise FileNotFoundError("Файл config.json не найден. Настройте подключение через интерфейс")
    if os.path.getsize(config_path) == 0:
        raise ValueError("Файл config.json пуст. Настройте подключение через интерфейс")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def read_query(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()
    
def print_results(cursos, results):
    if results:
        colums = [column[0] for column in cursos.description]
        table = PrettyTable()
        table.field_names = colums

        for row in results:
            table.add_row(row)

        result_window = tk.Toplevel(root)
        result_window.title("Результаты запроса")
        result_label = tk.Label(result_window, text=str(table), justify="left", font=("Courier", 10))
        result_label.pack(padx=10, pady=10, fill="both", expand=True)
    else:
        messagebox.showinfo("Результат", "Запрос выполнен, но данных для вывода нет")

def try_query():
    try:
        config = load_config()
        sql_file = "query.txt"

        if not os.path.exists(sql_file):
            raise FileNotFoundError(f"Файл {sql_file} не найден.")
        
        sql = read_query(sql_file)
        connection = fdb.connect(**config)
        cursor = connection.cursor()

        queries = sql.strip().split(';')

        for query in queries:
            if query.strip():
                cursor.execute(query)
                print(f"SQL-запрос выполнен успешно: {query}")
                if query.strip().upper.startswith("SELECT"):
                    results = cursor.fetchall()
                    print_results(cursor, results)

        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка выполнения запроса: {e}")



root = tk.Tk()
root.title("Управление базой данных")
root.geometry("475x480")
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

config_frame = ttk.Frame(notebook)
notebook.add(config_frame, text="Настройка подключения")

connection_type_var = tk.StringVar(value="local")
tk.Label(config_frame, text="Тип подключения:", font=("Arial", 12)).pack(anchor="w",pady=5)
tk.Radiobutton(config_frame, text="Локальное", variable=connection_type_var, value="local", command=dynamic_interface).pack(anchor="w")
tk.Radiobutton(config_frame, text="Сетевое", variable=connection_type_var, value="remote", command=dynamic_interface).pack(anchor="w")

local_frame = tk.Frame(config_frame, pady=5)
tk.Label(local_frame, text="Путь к локальной базе данных:", font=("Arial", 12)).pack(anchor="w")
local_db_path_var =tk.StringVar()
tk.Entry(local_frame, textvariable=local_db_path_var, width=50).pack(anchor="w", padx=10, pady=5)
tk.Button(local_frame, text="Обзор", command=browse_file).pack(anchor="w",padx=10, pady=5)

remote_frame = tk.Frame(config_frame, pady=5)
tk.Label(remote_frame, text="Хост:", font=("Arial", 12)).pack(anchor="w")
remote_host_var= tk.StringVar()
tk.Entry(remote_frame, textvariable=remote_host_var, width=40).pack(anchor="w", padx=10, pady=5)

tk.Label(remote_frame, text="Имя базы данных:", font=("Arial", 12)).pack(anchor="w")
remote_db_name_var = tk.StringVar()
tk.Entry(remote_frame, textvariable=remote_db_name_var, width=40).pack(anchor="w", padx=10, pady=5)

user_frame = tk.Frame(config_frame, pady=5)
user_frame.pack(fill="x")
tk.Label(user_frame, text="Пользователь:", font=("Arial", 12)).pack(anchor="w")
user_var = tk.StringVar(value="SYSDBA")
tk.Entry(user_frame, textvariable=user_var, width=40).pack(anchor="w", padx=10, pady=5)

tk.Label(user_frame, text="Пароль:", font=("Arial", 12)).pack(anchor="w")
password_var = tk.StringVar(value="masterkey")
tk.Entry(user_frame, textvariable=password_var, show="*", width=40).pack(anchor="w", padx=10, pady=5)

tk.Button(config_frame, text="Сохранить настройки", command=save_config, font=("Arial", 12)).pack(side="bottom", pady=10)

dynamic_interface()

query_frame = ttk.Frame(notebook)
notebook.add(query_frame, text="Выполнение запросов")
tk.Label(query_frame, text="SQL-запросы из файла query.txt будут выполнены", font=("Arial", 12)).pack(pady=10)
tk.Button(query_frame, text="Выполнить запросы", command=try_query, font=("Arial", 12)).pack(pady=20)

root.mainloop()