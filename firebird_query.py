import fdb
import os
from prettytable import PrettyTable


db_config = {"host": "localhost",
             "database": "C:/Users/Dima/Desktop/py/taskdubrov/test1.fdb",
             "user": "SYSDBA",
             "password": "masterkey",
             "charset": "UTF-8"}


def read_query(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
    

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
        return


def try_query(sql):
    try:
        connection = fdb.connect(**db_config)
        cursor = connection.cursor()

        queries = sql.strip().split(';')

        select_result = []

        for query in queries:
            if query.strip():
                cursor.execute(query)
                print(f"SQL-запрос выполнен успешно: {query}")
                if query.strip().upper().startswith("SELECT"):
                    results = cursor.fetchall()
                    select_result.append(results)

        for i, results in enumerate(select_result, start=1):
            print(f"Результаты SELECT запроса {i}:")
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
