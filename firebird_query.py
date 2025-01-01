import fdb
import os
import json
from prettytable import PrettyTable


def load_config(config_path="config.json"):
    if not os.path.exists(config_path):
        raise FileNotFoundError("Файл config.json не найден. Настройте подключение через интерфейс.")
    if os.path.getsize(config_path) == 0:
        raise ValueError("Файл config.json пуст. Настройте подключение через интерфейс.")
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def read_query(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()
    

def print_results(cursor, results):
    if results:
            columns =[column[0] for column in cursor.description]

            table = PrettyTable()
            table.field_names = columns

            for row in results:
                table.add_row(row)

            print(table)
    else:
        print("Запрос выполнен, но данных для вывода нет")


def try_query(sql):
    try:
        config = load_config()
        connection = fdb.connect(**config)
        cursor = connection.cursor()

        queries = sql.strip().split(';')


        for query in queries:
            if query.strip():
                cursor.execute(query)
                print(f"SQL-запрос выполнен успешно: {query}")
                if query.strip().upper().startswith("SELECT"):
                    results = cursor.fetchall()
                    print_results(cursor, results)

        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")

if __name__ == "__main__":
    sql_file = "query.txt"
    try:
        sql_query = read_query(sql_file)
        try_query(sql_query)
    except Exception as err:
        print(f"Произошла ошибка: {err}")
    input("Нажмите Enter для выхода")
