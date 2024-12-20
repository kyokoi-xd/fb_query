import tkinter as tk
from tkinter import filedialog, messagebox
import json

def save_config():
    connection_type = connection_type_var.get()
    config = {}

    if connection_type == "local":
        config["host"] = 'localhost'
        config["database"] = local_db_path_var.get()

    else:
        config["host"] = remote_host_var.get()
        config["database"] = remote_db_name_var.get()
    
    config["user"] = user_var.get()
    config["password"] = password_var.get()
    config["charset"] = "UTF-8"

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    messagebox.showinfo("Успех", "Конфигурация сохранена")

def browse_file():
    file_path = filedialog.askopenfilename(title="Выбирите файл базы данных", filetypes=[("FDB файлы","*.fdb")])
    local_db_path_var.set(file_path)

root = tk.Tk()
root.title("Настройки подключения")

connection_type_var = tk.StringVar(value="local")
tk.Label(root, text="Тип подключения:").pack(anchor="w")
tk.Radiobutton(root, text="Локальное", variable=connection_type_var, value="local").pack(anchor="w")
tk.Radiobutton(root, text="Сетевое", variable=connection_type_var, value="remote").pack(anchor="w")

tk.Label(root, text="Путь к локальной базе данных:").pack(anchor="w")
local_db_path_var = tk.StringVar()
tk.Entry(root, textvariable=local_db_path_var, width=50).pack(anchor="w")
tk.Button(root, text="Обзор", command=browse_file).pack(anchor="w")

tk.Label(root, text="Хост:").pack(anchor="w")
remote_host_var = tk.StringVar()
tk.Entry(root, textvariable=remote_host_var).pack(anchor="w")

tk.Label(root, text="Имя базы данных:").pack(anchor="w")
remote_db_name_var = tk.StringVar()
tk.Entry(root, textvariable=remote_db_name_var).pack(anchor="w")

tk.Label(root, text="Пользователь:").pack(anchor="w")
user_var = tk.StringVar(value="SYSDBA")
tk.Entry(root, textvariable=user_var).pack(anchor="w")

tk.Label(root, text="Пароль:").pack(anchor="w")
password_var = tk.StringVar(value="masterkey")
tk.Entry(root,textvariable=password_var, show="*").pack(anchor="w")

tk.Button

