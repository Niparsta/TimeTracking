import sys
import os
import json
import psycopg2
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Departments, Positions, Clients, Employees, Projects, Tasks, TimeEntries
from PySide6.QtWidgets import QApplication, QMessageBox

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    "DATABASE_HOST": "localhost",
    "DATABASE_PORT": 5432,
    "DATABASE_USER": "postgres",
    "DATABASE_PASSWORD": "password",
    "DATABASE_NAME": "companydb"
}


def show_error_dialog(message):
    app = QApplication(sys.argv)
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setWindowTitle("Ошибка")
    error_dialog.setText(message)
    error_dialog.exec()
    app.exit()


def check_database_connection(host, port, user, password):
    try:
        test_conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        test_conn.close()
    except UnicodeDecodeError:
        show_error_dialog(f"Неправильные данные для авторизации в базе данных")
        sys.exit(1)
    except psycopg2.OperationalError as e:
        if 'password authentication failed' in str(e):
            show_error_dialog("Неправильные данные для авторизации в базе данных")
        elif 'could not connect to server' or 'Connection refused':
            show_error_dialog("Не удалось подключиться к базе данных")
        else:
            show_error_dialog(f"Ошибка при работе с базой данных: {e}")
        sys.exit(1)


if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(DEFAULT_CONFIG, config_file, indent=4)

with open(CONFIG_FILE, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

DATABASE_HOST = config["DATABASE_HOST"]
DATABASE_PORT = config["DATABASE_PORT"]
DATABASE_USER = config["DATABASE_USER"]
DATABASE_PASSWORD = config["DATABASE_PASSWORD"]
DATABASE_NAME = config["DATABASE_NAME"]
DATABASE_URL_NO_DB = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/"

check_database_connection(DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD)

conn = psycopg2.connect(DATABASE_URL_NO_DB)
conn.autocommit = True
cursor = conn.cursor()
print(f"User '{DATABASE_USER}' successfully authenticated to the database")

cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DATABASE_NAME,))
if cursor.rowcount == 0:
    cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
    print(f"Database '{DATABASE_NAME}' successfully created")
else:
    print(f"Database '{DATABASE_NAME}' already exists")

cursor.close()
conn.close()

DATABASE_URL = f"{DATABASE_URL_NO_DB}{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
print(f"Successfully connected to '{DATABASE_NAME}' database")

tables = [Departments, Positions, Clients, Employees, Projects, Tasks, TimeEntries]
for table in tables:
    inspector = inspect(engine)
    if not inspector.has_table(table.__tablename__):
        try:
            table.__table__.create(engine)
            print(f"Table '{table.__tablename__}' created successfully")
        except Exception as e:
            print(f"Error creating table '{table.__tablename__}': {e}")
            show_error_dialog(f"Ошибка при создании таблицы '{table.__tablename__}': {e}")
    else:
        print(f"Table '{table.__tablename__}' already exists")

session.close()