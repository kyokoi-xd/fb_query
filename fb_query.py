import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
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

def load_query_files():
    queries_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queries")
    if not os.path.exists(queries_folder):
        os.makedirs(queries_folder)
    return [f for f in os.listdir(queries_folder) if f.endswith('.txt')]

def create_query_dropdown_with_refresh():
    query_files = load_query_files()
    query_combobox = ttk.Combobox(query_frame, values=query_files, width=40, font=("Arial", 12))
    query_combobox.place(x=10, y=40)


    refresh_icon = PhotoImage(file='img/refresh.png')
    refresh_button = tk.Button(query_frame, image=refresh_icon, command=update_query_list, borderwidth=0)
    refresh_button.image = refresh_icon
    refresh_button.place(x=400, y=35)

    return query_combobox

def update_query_list():
    query_files = load_query_files()
    query_combobox['values'] = query_files

def try_query():
    try:
        selected_query = query_combobox.get()
        queries_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queries") 
        sql_file = os.path.join(queries_folder, selected_query)

        if not os.path.exists(sql_file):
            raise FileNotFoundError(f"Файл {sql_file} не найден.")
        
        
        sql = read_query(sql_file)
        config = load_config()
        connection = fdb.connect(**config)
        cursor = connection.cursor()

        queries = sql.strip().split(';')

        query_flag = True

        for query in queries:
            query = query.strip()
            if query:
                cursor.execute(query)
                print(f"SQL-запрос выполнен успешно: {query}")
                if query.strip().upper().startswith("SELECT"):
                    results = cursor.fetchall()
                    print_results(cursor, results)
                    query_flag = False

        connection.commit()
        if query_flag:
            messagebox.showinfo("Успех", "SQL-запрос выполнен успешно и изменения сохранены.")
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

tk.Label(remote_frame, text="Путь к базе данных на сервере (полный путь):", font=("Arial", 12)).pack(anchor="w")
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

tk.Label(query_frame, text="Выберите файл с запросами:", font=("Arial", 12)).place(x=10, y=10)
tk.Button(query_frame, text="Выполнить запросы", command=try_query, font=("Arial", 12)).pack(pady=100)

query_combobox = create_query_dropdown_with_refresh()


root.mainloop()