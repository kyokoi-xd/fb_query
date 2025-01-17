import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import fdb
import os
import sys
import json
from prettytable import PrettyTable
from pandas import DataFrame 

current_dir = os.path.dirname(os.path.abspath(__file__))
fdb.load_api(os.path.join(current_dir, 'fbclient.dll'))


def initialize_interface():
    try:
        config = load_config()
        connection_type_var.set("local" if config["host"] == "localhost" else "remote")
        dynamic_interface()

        if config["host"] == "localhost":
            local_db_path_var.set(config["database"])
        else:
            remote_host_var.set(config["host"])
            remote_db_name_var.set(config["database"])

        user_var.set(config.get("user", "SYSDBA"))
        password_var.set(config.get("password", "masterkey"))
    except FileNotFoundError:
        messagebox.showinfo("Информация","Файл config.json не найден. Пользователь должен настроить параметры вручную.")
    except ValueError:
        messagebox.showinfo("Информация","Файл config.json не найден. Пользователь должен настроить параметры вручную.")
    except Exception as e:
        messagebox.showerror("Ошибка",f"Ошибка инициализации интерфейса: {e}")

def save_config():
    connection_type = connection_type_var.get()
    config  = {
        "host" : "localhost" if connection_type == "local" else remote_host_var.get(),
        "database": local_db_path_var.get() if connection_type == "local" else remote_db_name_var.get(),
        "user": user_var.get(),
        "password": password_var.get(),
        "charset": "utf-8"
    }

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

def export_to_excel(data, columns):
    save_path = filedialog.asksaveasfilename(
        defaultextension="*.xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Сохранить результат в Excel"
    )
    if not save_path:
        return
    df = DataFrame(data, columns=columns)
    df.to_excel(save_path, index=False)
    messagebox.showinfo("Успех", f"Данные успешно сохранены в файл: {save_path}")
    
def print_results(cursos, results):
    if results:
        columns = [column[0] for column in cursos.description]
        table = PrettyTable()
        table.field_names = columns

        for row in results:
            table.add_row(row)

        result_window = tk.Toplevel(root)
        result_window.title("Результаты запроса")

        tk.Label(result_window, text=str(table), justify="left", font=("Courier", 10)).pack(padx=10, pady=10, fill="both", expand=True)
        tk.Button(result_window, text="Экспортировать в Excel", command=lambda: export_to_excel(results, columns)).pack(pady=10)
    else:
        messagebox.showinfo("Результат", "Запрос выполнен, но данных для вывода нет")

def get_queries_folder():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "queries")

def update_query_list(event=None):
    queries_folder = get_queries_folder()
    query_files = [f for f in os.listdir(queries_folder) if f.endswith(".txt")]
    query_combobox['values'] = query_files
    if query_files:
        query_combobox.set(query_files[0])
    else:
        query_combobox.set("")

def try_query():
    try:
        selected_query = query_combobox.get()
        queries_folder = get_queries_folder()
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

query_frame = ttk.Frame(notebook)
notebook.add(query_frame, text="SQL-запросы")

tk.Label(query_frame, text="Выберите SQL-запрос:", font=("Arial", 12)).place(x=10, y=30)

query_combobox = ttk.Combobox(query_frame, width=70)
query_combobox.place(x=10, y=60)
query_combobox.bind("<Button-1>", update_query_list)

execute_button = tk.Button(query_frame, text="Выполнить запросы", command=try_query, font=("Arial", 12))
execute_button.pack(pady=100)

dynamic_interface()
initialize_interface()

root.mainloop()