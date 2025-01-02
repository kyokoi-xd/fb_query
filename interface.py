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


def dynamic_interfrace():
    if connection_type_var.get() == "local":
        local_frame.pack(fill="x", pady=10)
        remote_frame.pack_forget()
    else:
        local_frame.pack_forget()
        remote_frame.pack(fill="x", pady=10)

root = tk.Tk()
root.title("Настройки подключения")
root.geometry("475x480")

tk.Label(root, text="Настройки подключения к базе данных", font=("Arial", 14, "bold")).pack(pady=10)

connection_type_var = tk.StringVar(value="local")
type_frame = tk.Frame(root, pady=5)
type_frame.pack(fill="x")
tk.Label(type_frame, text="Тип подключения:", font=("Arial", 12)).pack(anchor="w")
tk.Radiobutton(type_frame, text="Локальное", variable=connection_type_var, value="local", command=dynamic_interfrace).pack(anchor="w")
tk.Radiobutton(type_frame, text="Сетевое", variable=connection_type_var, value="remote", command=dynamic_interfrace).pack(anchor="w")

local_frame = tk.Frame(root, pady=5)
tk.Label(local_frame, text="Путь к локальной базе данных:", font=("Arial", 12)).pack(anchor="w")
local_db_path_var = tk.StringVar()
tk.Entry(local_frame, textvariable=local_db_path_var, width=50).pack(anchor="w", padx=10, pady=5)
tk.Button(local_frame, text="Обзор", command=browse_file).pack(anchor="w", padx=10, pady=5)

remote_frame = tk.Frame(root, pady=5)
tk.Label(remote_frame, text="Хост:", font=("Arial", 12)).pack(anchor="w")
remote_host_var = tk.StringVar()
tk.Entry(remote_frame, textvariable=remote_host_var, width=40).pack(anchor="w", padx=10, pady=5)

tk.Label(remote_frame, text="Имя базы данных:", font=("Arial", 12)).pack(anchor="w")
remote_db_name_var = tk.StringVar()
tk.Entry(remote_frame, textvariable=remote_db_name_var, width=40).pack(anchor="w", padx=10, pady=5)


user_frame = tk.Frame(root, pady=5)
user_frame.pack(fill="x")
tk.Label(user_frame, text="Пользователь:", font=("Arial", 12)).pack(anchor="w")
user_var = tk.StringVar(value="SYSDBA")
tk.Entry(user_frame, textvariable=user_var, width=40).pack(anchor="w", padx=10, pady=5)

tk.Label(user_frame, text="Пароль:", font=("Arial", 12)).pack(anchor="w")
password_var = tk.StringVar(value="masterkey")
tk.Entry(user_frame,textvariable=password_var, show="*", width=40).pack(anchor="w", padx=10, pady=5)


button_frame = tk.Frame(root, pady=10)
button_frame.pack(fill="x", side="bottom")
tk.Button(button_frame, text="Сохранить настройки",  command=save_config, font=("Arial", 12)).pack(pady=20)

dynamic_interfrace()

root.mainloop()

