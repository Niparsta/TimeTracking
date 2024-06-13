import datetime

from PySide6.QtCore import Qt, QRegularExpression, QDate, QTime, QDateTime
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QMessageBox,
    QDialog,
    QDateEdit,
    QRadioButton, QComboBox, QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, QTimeEdit, QAbstractItemView
)
from PySide6.QtGui import QIcon
from sqlalchemy import text, func
from sqlalchemy.orm import joinedload

from models import Clients, Departments, Positions, Employees, Projects, Tasks, TimeEntries
import database


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Учёт времени работы сотрудников компании")
        self.setWindowIcon(QIcon("icon.ico"))
        self.resize(1100, 600)
        self.setMinimumSize(1100, 600)

        self.session = database.Session()

        self.button_add_department = QPushButton("Добавить отдел")
        self.button_add_department.clicked.connect(self.open_add_department_dialog)
        self.button_add_position = QPushButton("Добавить должность")
        self.button_add_position.clicked.connect(self.open_add_position_dialog)
        self.button_add_client = QPushButton("Добавить клиента")
        self.button_add_client.clicked.connect(self.open_add_client_dialog)
        self.button_add_employee = QPushButton("Добавить сотрудника")
        self.button_add_employee.clicked.connect(self.open_add_employee_dialog)
        self.button_add_project = QPushButton("Добавить проект")
        self.button_add_project.clicked.connect(self.open_add_project_dialog)

        self.button_add_task = QPushButton("Добавить задачу")
        self.button_add_task.clicked.connect(self.open_add_task_dialog)
        self.button_add_task.setEnabled(False)

        self.button_add_time_entry = QPushButton("Добавить временную метку")
        self.button_add_time_entry.clicked.connect(self.open_add_time_entry_dialog)
        self.button_add_time_entry.setEnabled(False)

        self.button_delete_employee = QPushButton("Удалить сотрудника(-ов)")
        self.button_delete_employee.clicked.connect(self.delete_selected_employees)
        self.button_delete_employee.setEnabled(False)

        self.button_delete_client = QPushButton("Удалить клиента(-ов)")
        self.button_delete_client.clicked.connect(self.delete_selected_clients)
        self.button_delete_client.setEnabled(False)

        self.button_delete_project = QPushButton("Удалить проект(-ы)")
        self.button_delete_project.clicked.connect(self.delete_selected_projects)
        self.button_delete_project.setEnabled(False)

        self.button_delete_task = QPushButton("Удалить задачу(-и)")
        self.button_delete_task.clicked.connect(self.delete_selected_tasks)
        self.button_delete_task.setEnabled(False)

        self.button_delete_position = QPushButton("Удалить должность(-и)")
        self.button_delete_position.clicked.connect(self.delete_selected_positions)
        self.button_delete_position.setEnabled(False)

        self.button_delete_department = QPushButton("Удалить отдел(-ы)")
        self.button_delete_department.clicked.connect(self.delete_selected_departments)
        self.button_delete_department.setEnabled(False)

        self.button_edit_position = QPushButton("Изменить данные должности")
        self.button_edit_position.clicked.connect(self.open_edit_position_dialog)
        self.button_edit_position.setEnabled(False)

        self.button_edit_department = QPushButton("Изменить данные отдела")
        self.button_edit_department.clicked.connect(self.open_edit_department_dialog)
        self.button_edit_department.setEnabled(False)

        self.button_edit_client = QPushButton("Изменить данные клиента")
        self.button_edit_client.clicked.connect(self.open_edit_client_dialog)
        self.button_edit_client.setEnabled(False)

        self.button_edit_employee = QPushButton("Изменить данные сотрудника")
        self.button_edit_employee.clicked.connect(self.open_edit_employee_dialog)
        self.button_edit_employee.setEnabled(False)

        self.button_edit_project = QPushButton("Изменить данные проекта")
        self.button_edit_project.clicked.connect(self.open_edit_project_dialog)
        self.button_edit_project.setEnabled(False)

        self.button_edit_task = QPushButton("Изменить данные задачи")
        self.button_edit_task.clicked.connect(self.open_edit_task_dialog)
        self.button_edit_task.setEnabled(False)

        self.button_edit_time_entry = QPushButton("Изменить данные временной метки")
        self.button_edit_time_entry.clicked.connect(self.open_edit_time_entry_dialog)
        self.button_edit_time_entry.setEnabled(False)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(QWidget(), "Сотрудники")
        self.tab_widget.addTab(QWidget(), "Клиенты")
        self.tab_widget.addTab(QWidget(), "Проекты")
        self.tab_widget.addTab(QWidget(), "Должности")
        self.tab_widget.addTab(QWidget(), "Отделы")
        self.tab_widget.addTab(QWidget(), "Отчёт")
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setMovable(True)

        employees_layout = QVBoxLayout()
        employees_buttons_layout = QHBoxLayout()
        employees_buttons_layout.addWidget(self.button_add_employee)
        employees_buttons_layout.addWidget(self.button_edit_employee)
        employees_buttons_layout.addWidget(self.button_delete_employee)
        employees_layout.addLayout(employees_buttons_layout)
        self.employees_table_widget = QTableWidget()
        self.employees_table_widget.setColumnCount(12)
        self.employees_table_widget.setHorizontalHeaderLabels(
            ['Фамилия', 'Имя', 'Отчество', 'Дата рождения', 'Пол', 'Дата приема на работу', 'Отдел', 'Должность',
             'Заработная плата (в месяц)', 'Адрес электронной почты', 'Контактный телефон', 'ID'])
        self.employees_table_widget.setColumnHidden(11, True)
        self.employees_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        employees_layout.addWidget(self.employees_table_widget)
        self.tab_widget.widget(0).setLayout(employees_layout)
        self.employees_table_widget.selectionModel().selectionChanged.connect(self.employees_selection_changed)

        clients_layout = QVBoxLayout()
        clients_buttons_layout = QHBoxLayout()
        clients_buttons_layout.addWidget(self.button_add_client)
        clients_buttons_layout.addWidget(self.button_edit_client)
        clients_buttons_layout.addWidget(self.button_delete_client)
        clients_layout.addLayout(clients_buttons_layout)
        self.clients_table_widget = QTableWidget()
        self.clients_table_widget.setColumnCount(5)
        self.clients_table_widget.setHorizontalHeaderLabels(
            ['Наименование', 'Контактное лицо', 'Адрес электронной почты', 'Контактный телефон', 'ID'])
        self.clients_table_widget.setColumnHidden(4, True)
        self.clients_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        clients_layout.addWidget(self.clients_table_widget)
        self.tab_widget.widget(1).setLayout(clients_layout)
        self.clients_table_widget.selectionModel().selectionChanged.connect(self.clients_selection_changed)

        projects_layout = QVBoxLayout()
        projects_buttons_layout = QHBoxLayout()
        projects_buttons_layout.addWidget(self.button_add_project)
        projects_buttons_layout.addWidget(self.button_edit_project)
        projects_buttons_layout.addWidget(self.button_delete_project)
        projects_layout.addLayout(projects_buttons_layout)
        self.projects_table_widget = QTableWidget()
        self.projects_table_widget.setColumnCount(7)
        self.projects_table_widget.setHorizontalHeaderLabels(
            ['Название', 'Клиент', 'Руководитель проекта', 'Дата начала', 'Дата окончания', 'Описание', 'ID'])
        self.projects_table_widget.setColumnHidden(6, True)
        self.projects_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        projects_layout.addWidget(self.projects_table_widget)
        self.projects_table_widget.cellClicked.connect(self.show_project_tasks)
        self.projects_table_widget.selectionModel().selectionChanged.connect(self.projects_selection_changed)

        tasks_layout = QVBoxLayout()
        tasks_buttons_layout = QHBoxLayout()
        tasks_buttons_layout.addWidget(self.button_add_task)
        tasks_buttons_layout.addWidget(self.button_edit_task)
        tasks_buttons_layout.addWidget(self.button_delete_task)
        tasks_layout.addLayout(tasks_buttons_layout)
        self.tasks_table_widget = QTableWidget()
        self.tasks_table_widget.setColumnCount(6)
        self.tasks_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tasks_table_widget.selectionModel().selectionChanged.connect(self.tasks_selection_changed)
        self.tasks_table_widget.setHorizontalHeaderLabels(
            ['Проект', 'Задача', 'Дата начала', 'Дата окончания', 'Описание', 'ID']
        )
        self.tasks_table_widget.setColumnHidden(5, True)
        tasks_layout.addWidget(self.tasks_table_widget)

        time_entries_layout = QVBoxLayout()
        self.time_entries_table_widget = QTableWidget()
        self.time_entries_table_widget.setColumnCount(5)
        self.time_entries_table_widget.selectionModel().selectionChanged.connect(self.time_entries_selection_changed)
        self.time_entries_table_widget.setHorizontalHeaderLabels(
            ['Задача', 'Сотрудник', 'Время начала', 'Время окончания', 'ID']
        )
        self.time_entries_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.time_entries_table_widget.setColumnHidden(4, True)
        self.tasks_table_widget.cellClicked.connect(self.show_task_time_entries)
        time_entries_layout.addWidget(self.time_entries_table_widget)

        time_entries_buttons_layout = QHBoxLayout()
        time_entries_buttons_layout.addWidget(self.button_add_time_entry)
        self.button_delete_time_entry = QPushButton("Удалить временную(-ые) метку(-и)")
        self.button_delete_time_entry.setEnabled(False)
        self.button_delete_time_entry.clicked.connect(self.delete_selected_time_entries)
        time_entries_buttons_layout.addWidget(self.button_edit_time_entry)
        time_entries_buttons_layout.addWidget(self.button_delete_time_entry)

        tasks_time_entries_layout = QVBoxLayout()
        tasks_time_entries_layout.addLayout(tasks_layout)
        tasks_time_entries_layout.addLayout(time_entries_buttons_layout)
        tasks_time_entries_layout.addLayout(time_entries_layout)

        projects_tasks_layout = QHBoxLayout()
        projects_tasks_layout.addLayout(projects_layout)
        projects_tasks_layout.addLayout(tasks_time_entries_layout)
        self.tab_widget.widget(2).setLayout(projects_tasks_layout)

        positions_layout = QVBoxLayout()
        positions_buttons_layout = QHBoxLayout()
        positions_buttons_layout.addWidget(self.button_add_position)
        positions_buttons_layout.addWidget(self.button_edit_position)
        positions_buttons_layout.addWidget(self.button_delete_position)
        positions_layout.addLayout(positions_buttons_layout)
        self.positions_table_widget = QTableWidget()
        self.positions_table_widget.setColumnCount(3)
        self.positions_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.positions_table_widget.setHorizontalHeaderLabels(['Название', 'Количество сотрудников', 'ID'])
        self.positions_table_widget.setColumnHidden(2, True)
        positions_layout.addWidget(self.positions_table_widget)
        self.positions_table_widget.selectionModel().selectionChanged.connect(self.positions_selection_changed)
        self.tab_widget.widget(3).setLayout(positions_layout)

        departments_layout = QVBoxLayout()
        departments_buttons_layout = QHBoxLayout()
        departments_buttons_layout.addWidget(self.button_add_department)
        departments_buttons_layout.addWidget(self.button_edit_department)
        departments_buttons_layout.addWidget(self.button_delete_department)
        departments_layout.addLayout(departments_buttons_layout)
        self.departments_table_widget = QTableWidget()
        self.departments_table_widget.setColumnCount(3)
        self.departments_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.departments_table_widget.setHorizontalHeaderLabels(['Название', 'Количество сотрудников', 'ID'])
        self.departments_table_widget.setColumnHidden(2, True)
        departments_layout.addWidget(self.departments_table_widget)
        self.departments_table_widget.selectionModel().selectionChanged.connect(self.departments_selection_changed)
        self.tab_widget.widget(4).setLayout(departments_layout)

        report_layout = QVBoxLayout()

        period_label = QLabel("Период анализа:")
        self.start_date_edit = QDateEdit(QDate.currentDate().addDays(-QDate.currentDate().day() + 1))
        self.end_date_edit = QDateEdit(
            QDate.currentDate().addDays(QDate.currentDate().daysInMonth() - QDate.currentDate().day()))

        period_layout = QHBoxLayout()
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.start_date_edit)
        period_layout.addWidget(self.end_date_edit)
        report_layout.addLayout(period_layout)

        department_layout = QHBoxLayout()
        department_label = QLabel("Отдел:")
        self.department_combobox = QComboBox()
        department_layout.addWidget(department_label)
        department_layout.addWidget(self.department_combobox)
        report_layout.addLayout(department_layout)

        position_layout = QHBoxLayout()
        position_label = QLabel("Должность:")
        self.position_combobox = QComboBox()
        position_layout.addWidget(position_label)
        position_layout.addWidget(self.position_combobox)
        report_layout.addLayout(position_layout)

        project_layout = QHBoxLayout()
        project_label = QLabel("Проект:")
        self.project_combobox = QComboBox()
        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_combobox)
        report_layout.addLayout(project_layout)

        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton("Подтвердить")
        self.confirm_button.clicked.connect(self.update_report_table_widget)
        self.confirm_button.setEnabled(False)
        button_layout.addWidget(self.confirm_button)

        self.reset_button = QPushButton("Сбросить")
        self.reset_button.clicked.connect(self.reset_report_table_widget)
        self.reset_button.setEnabled(False)
        button_layout.addWidget(self.reset_button)
        report_layout.addLayout(button_layout)

        self.report_table_widget = QTableWidget()
        self.report_table_widget.setColumnCount(6)
        self.report_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.report_table_widget.setHorizontalHeaderLabels(
            ['Сотрудник', 'Отдел', 'Должность', 'Адрес электронной почты', 'Контактный телефон', 'Суммарное время'])
        report_layout.addWidget(self.report_table_widget)

        self.department_combobox.currentTextChanged.connect(self.enable_confirm_button)
        self.position_combobox.currentTextChanged.connect(self.enable_confirm_button)
        self.project_combobox.currentTextChanged.connect(self.enable_confirm_button)
        self.start_date_edit.dateChanged.connect(self.enable_confirm_button)
        self.end_date_edit.dateChanged.connect(self.enable_confirm_button)

        self.tab_widget.widget(5).setLayout(report_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        self.current_project_id = None
        self.current_task_id = None
        self.update_all_tables_widgets()

    def update_report_comboBoxes(self):
        self.project_combobox.clear()
        self.position_combobox.clear()
        self.department_combobox.clear()

        projects = self.session.query(Projects).all()
        if projects:
            self.project_combobox.addItem("Все проекты")
            self.project_combobox.addItems([pr.name for pr in projects])
            self.project_combobox.setCurrentIndex(0)
            self.project_combobox.setEnabled(True)
        else:
            self.project_combobox.addItem("Пусто")
            self.project_combobox.setEnabled(False)

        positions = self.session.query(Positions).all()
        if positions:
            self.position_combobox.addItem("Все должности")
            self.position_combobox.addItems([p.name for p in positions])
            self.position_combobox.setCurrentIndex(0)
            self.position_combobox.setEnabled(True)
        else:
            self.position_combobox.addItem("Пусто")
            self.position_combobox.setEnabled(False)

        departments = self.session.query(Departments).all()
        if departments:
            self.department_combobox.addItem("Все отделы")
            self.department_combobox.addItems([d.name for d in departments])
            self.department_combobox.setCurrentIndex(0)
            self.department_combobox.setEnabled(True)
        else:
            self.department_combobox.addItem("Пусто")
            self.department_combobox.setEnabled(False)

    def open_add_department_dialog(self):
        dialog = AddDepartmentDialog(self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_edit_department_dialog(self):
        selected_row = self.departments_table_widget.currentRow()
        department_id = self.departments_table_widget.item(selected_row, 2).text()
        department_id = int(department_id)
        dialog = EditDepartmentDialog(department_id, self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_add_position_dialog(self):
        dialog = AddPositionDialog(self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_edit_position_dialog(self):
        selected_row = self.positions_table_widget.currentRow()
        position_id = self.positions_table_widget.item(selected_row, 2).text()
        position_id = int(position_id)
        dialog = EditPositionDialog(position_id, self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_add_client_dialog(self):
        dialog = AddClientDialog(self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_edit_client_dialog(self):
        selected_row = self.clients_table_widget.currentRow()
        client_id = self.clients_table_widget.item(selected_row, 4).text()
        client_id = int(client_id)
        dialog = EditClientDialog(client_id, self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_add_employee_dialog(self):
        dialog = AddEmployeeDialog(self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_edit_employee_dialog(self):
        selected_row = self.employees_table_widget.currentRow()
        employee_id = self.employees_table_widget.item(selected_row, 11).text()
        employee_id = int(employee_id)
        dialog = EditEmployeeDialog(employee_id, self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_add_project_dialog(self):
        dialog = AddProjectDialog(self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_edit_project_dialog(self):
        selected_row = self.projects_table_widget.currentRow()
        project_id = self.projects_table_widget.item(selected_row, 6).text()
        project_id = int(project_id)
        dialog = EditProjectDialog(project_id, self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_add_task_dialog(self):
        dialog = AddTaskDialog(self, self.current_project_id)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_edit_task_dialog(self):
        selected_row = self.tasks_table_widget.currentRow()
        task_id = self.tasks_table_widget.item(selected_row, 5).text()
        task_id = int(task_id)
        dialog = EditTaskDialog(task_id, self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def open_add_time_entry_dialog(self):
        selected_row = self.tasks_table_widget.currentRow()
        if selected_row != -1:
            task_name = self.tasks_table_widget.item(selected_row, 1).text()
            task = self.session.query(Tasks).filter_by(name=task_name).first()
            if task:
                employee_id = self.session.query(Employees).all()[self.employees_table_widget.currentRow()].id
                dialog = AddTimeEntryDialog(self, employee_id, task.id)
                dialog.setWindowModality(Qt.ApplicationModal)
                dialog.finished.connect(self.update_all_tables_widgets)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти задачу")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу")

    def open_edit_time_entry_dialog(self):

        selected_row = self.time_entries_table_widget.currentRow()
        time_entry_id = self.time_entries_table_widget.item(selected_row, 4).text()
        time_entry_id = int(time_entry_id)
        dialog = EditTimeEntryDialog(time_entry_id, self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.finished.connect(self.update_all_tables_widgets)
        dialog.exec()

    def delete_selected_employees(self):
        selected_indexes = self.employees_table_widget.selectionModel().selectedIndexes()

        if selected_indexes:
            message_box = QMessageBox()
            message_box.setWindowTitle("Подтверждение удаления")
            message_box.setText(
                "Вы уверены, что хотите удалить выбранного(-ых) сотрудника(-ов) и все связанные временные метки?")
            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.button(QMessageBox.Yes).setText("Да")
            message_box.button(QMessageBox.No).setText("Нет")

            response = message_box.exec_()

            if response == QMessageBox.Yes:
                selected_rows = set(index.row() for index in selected_indexes)

                for row_index in selected_rows:
                    employee_id = int(self.employees_table_widget.item(row_index, 11).text())

                    employee = self.session.query(Employees).filter_by(id=employee_id).first()

                    if employee:
                        project = self.session.query(Projects).filter_by(manager_id=employee_id).first()

                        if project:
                            error_message = f"{employee.last_name} {employee.first_name} {employee.middle_name} является руководителем проекта '{project.name}'"
                            QMessageBox.critical(self, "Ошибка удаления", error_message)
                            break

                        self.session.query(TimeEntries).filter_by(employee_id=employee_id).delete()
                        self.session.delete(employee)
                        self.session.commit()

                self.update_employees_table_widget()

    def delete_selected_clients(self):
        selected_indexes = self.clients_table_widget.selectionModel().selectedIndexes()

        if selected_indexes:
            message_box = QMessageBox()
            message_box.setWindowTitle("Подтверждение удаления")
            message_box.setText("Вы уверены, что хотите удалить выбранного(-ых) клиента(-ов)?")
            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.button(QMessageBox.Yes).setText("Да")
            message_box.button(QMessageBox.No).setText("Нет")

            response = message_box.exec_()

            if response == QMessageBox.Yes:
                selected_rows = set(index.row() for index in selected_indexes)

                for row_index in selected_rows:
                    client_id = int(self.clients_table_widget.item(row_index, 4).text())

                    client = self.session.query(Clients).filter_by(id=client_id).first()

                    if client:
                        projects = self.session.query(Projects).filter_by(client_id=client_id).all()

                        if projects:
                            error_message = f"Клиент '{client.name}' имеет связанные проекты: {', '.join([project.name for project in projects])}"
                            QMessageBox.critical(self, "Ошибка удаления", error_message)
                            break

                        self.session.delete(client)
                        self.session.commit()

                self.update_clients_table_widget()

    def delete_selected_projects(self):
        session = database.Session()

        selected_indexes = self.projects_table_widget.selectionModel().selectedIndexes()

        if selected_indexes:
            message_box = QMessageBox()
            message_box.setWindowTitle("Подтверждение удаления")
            message_box.setText(
                "Вы уверены, что хотите удалить выбранный(-ые) проект(-ы) и все связанные с ним(-и) задачи?")
            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.button(QMessageBox.Yes).setText("Да")
            message_box.button(QMessageBox.No).setText("Нет")

            response = message_box.exec_()

            if response == QMessageBox.Yes:
                try:
                    for index in selected_indexes:
                        row_index = index.row()
                        project_id = int(
                            self.projects_table_widget.item(row_index, 6).text())

                        project = session.query(Projects).filter_by(id=project_id).first()

                        if project:
                            tasks = session.query(Tasks).filter_by(project_id=project_id).all()
                            for task in tasks:
                                time_entries = session.query(TimeEntries).filter_by(task_id=task.id).all()
                                for time_entry in time_entries:
                                    session.delete(time_entry)
                                session.delete(task)

                            session.delete(project)

                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                finally:
                    self.update_projects_table_widget()
                    self.update_tasks_table_widget()
                    self.show_task_time_entries(0)

    def delete_selected_tasks(self):
        selected_indexes = self.tasks_table_widget.selectionModel().selectedIndexes()

        if selected_indexes:
            message_box = QMessageBox()
            message_box.setWindowTitle("Подтверждение удаления")
            message_box.setText(
                "Вы уверены, что хотите удалить выбранную(-ые) задачу(-и) и все связанные временные метки?")
            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.button(QMessageBox.Yes).setText("Да")
            message_box.button(QMessageBox.No).setText("Нет")

            response = message_box.exec_()

            if response == QMessageBox.Yes:
                for index in selected_indexes:
                    row_index = index.row()
                    task_id = int(self.tasks_table_widget.item(row_index, 5).text())

                    task = self.session.query(Tasks).filter_by(id=task_id).first()

                    if task:
                        time_entries = self.session.query(TimeEntries).filter_by(task_id=task_id).all()
                        for time_entry in time_entries:
                            self.session.delete(time_entry)

                        self.session.delete(task)
                        self.session.commit()

                    self.show_project_tasks(0)
                    self.show_task_time_entries(0)

    def delete_selected_positions(self):
        selected_indexes = self.positions_table_widget.selectionModel().selectedIndexes()

        if selected_indexes:
            message_box = QMessageBox()
            message_box.setWindowTitle("Подтверждение удаления")
            message_box.setText("Вы уверены, что хотите удалить выбранную(-ые) должность(-и)?")

            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.button(QMessageBox.Yes).setText("Да")
            message_box.button(QMessageBox.No).setText("Нет")

            response = message_box.exec_()

            if response == QMessageBox.Yes:
                for index in selected_indexes:
                    row_index = index.row()
                    position_id = int(self.positions_table_widget.item(row_index, 2).text())

                    position = self.session.query(Positions).filter_by(id=position_id).first()

                    if position:
                        employees = self.session.query(Employees).filter_by(position_id=position_id).all()
                        if employees:
                            error_message = f"Должность '{position.name}' назначена следующему количеству сотрудников: {len(employees)}"
                            QMessageBox.critical(self, "Ошибка удаления", error_message)
                            break
                        else:
                            self.session.delete(position)
                            self.session.commit()

                self.update_positions_table_widget()

    def delete_selected_departments(self):
        selected_indexes = self.departments_table_widget.selectionModel().selectedIndexes()

        if selected_indexes:
            message_box = QMessageBox()
            message_box.setWindowTitle("Подтверждение удаления")
            message_box.setText("Вы уверены, что хотите удалить выбранный(-ые) отдел(-ы)?")

            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.button(QMessageBox.Yes).setText("Да")
            message_box.button(QMessageBox.No).setText("Нет")

            response = message_box.exec_()

            if response == QMessageBox.Yes:
                for index in selected_indexes:
                    row_index = index.row()
                    department_id = int(self.departments_table_widget.item(row_index, 2).text())

                    department = self.session.query(Departments).filter_by(id=department_id).first()

                    if department:
                        employees = self.session.query(Employees).filter_by(department_id=department_id).all()
                        if employees:
                            error_message = f"В отделе '{department.name}' работает следующее количество сотрудников: {len(employees)}"
                            QMessageBox.critical(self, "Ошибка удаления", error_message)
                            break
                        else:
                            self.session.delete(department)
                            self.session.commit()

                self.update_departments_table_widget()

    def delete_selected_time_entries(self):
        selected_indexes = self.time_entries_table_widget.selectionModel().selectedIndexes()

        if selected_indexes:
            message_box = QMessageBox()
            message_box.setWindowTitle("Подтверждение удаления")
            message_box.setText("Вы уверены, что хотите удалить выбранные временные метки?")

            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.button(QMessageBox.Yes).setText("Да")
            message_box.button(QMessageBox.No).setText("Нет")

            response = message_box.exec_()

            if response == QMessageBox.Yes:
                rows_to_delete = [index.row() for index in selected_indexes]
                for row_index in sorted(rows_to_delete, reverse=True):
                    time_entry_id = self.time_entries_table_widget.item(row_index, 4).text()

                    time_entry = self.session.query(TimeEntries).filter_by(id=time_entry_id).first()

                    if time_entry:
                        self.session.delete(time_entry)
                        self.time_entries_table_widget.removeRow(row_index)
                        self.session.commit()
                        self.update_tasks_table_widget()
                    else:
                        QMessageBox.warning(self, "Ошибка", "Не удалось найти временную метку в базе данных.")

    def update_employees_table_widget(self):
        employees = self.session.query(Employees).all()
        self.employees_table_widget.setRowCount(len(employees))
        for row, employee in enumerate(employees):
            self.employees_table_widget.setItem(row, 0, QTableWidgetItem(employee.last_name))
            self.employees_table_widget.setItem(row, 1, QTableWidgetItem(employee.first_name))
            self.employees_table_widget.setItem(row, 2, QTableWidgetItem(employee.middle_name))
            self.employees_table_widget.setItem(row, 3, QTableWidgetItem(employee.birth_date.strftime("%Y-%m-%d")))
            self.employees_table_widget.setItem(row, 4,
                                                QTableWidgetItem("Мужской" if employee.gender == 0 else "Женский"))
            self.employees_table_widget.setItem(row, 5, QTableWidgetItem(employee.hire_date.strftime("%Y-%m-%d")))
            self.employees_table_widget.setItem(row, 6, QTableWidgetItem(str(employee.department.name)))
            self.employees_table_widget.setItem(row, 7, QTableWidgetItem(employee.position.name))
            self.employees_table_widget.setItem(row, 8, QTableWidgetItem(str(employee.salary)))
            self.employees_table_widget.setItem(row, 9, QTableWidgetItem(employee.email))
            self.employees_table_widget.setItem(row, 10, QTableWidgetItem(employee.phone_number))
            self.employees_table_widget.setItem(row, 11, QTableWidgetItem(str(employee.id)))
        self.employees_table_widget.resizeColumnsToContents()

    def update_projects_table_widget(self):
        projects = self.session.query(Projects).all()
        self.projects_table_widget.setRowCount(len(projects))

        for row, project in enumerate(projects):
            self.projects_table_widget.setItem(row, 0, QTableWidgetItem(project.name))
            self.projects_table_widget.setItem(row, 1, QTableWidgetItem(project.client.name))
            self.projects_table_widget.setItem(row, 2, QTableWidgetItem(
                f"{project.manager.last_name} {project.manager.first_name} {project.manager.middle_name}"))
            self.projects_table_widget.setItem(row, 3, QTableWidgetItem(project.start_date.strftime("%Y-%m-%d")))
            self.projects_table_widget.setItem(row, 4, QTableWidgetItem(project.end_date.strftime("%Y-%m-%d")))
            self.projects_table_widget.setItem(row, 5, QTableWidgetItem(str(project.description)))
            self.projects_table_widget.setItem(row, 6, QTableWidgetItem(str(project.id)))
        self.projects_table_widget.resizeColumnsToContents()
        self.projects_table_widget.clearSelection()

    def update_tasks_table_widget(self):
        if self.current_project_id:
            tasks = self.session.query(Tasks).filter_by(project_id=self.current_project_id).all()
        else:
            top_project_id = self.session.query(Projects.id).order_by(Projects.id).first()
            if top_project_id:
                tasks = self.session.query(Tasks).filter_by(project_id=top_project_id[0]).all()
            else:
                tasks = []

        self.tasks_table_widget.setRowCount(len(tasks))

        if self.current_task_id is not None:
            for row, task in enumerate(tasks):
                if task.id == self.current_task_id:
                    self.tasks_table_widget.setCurrentCell(row, 0)
                    break

        for row, task in enumerate(tasks):
            self.tasks_table_widget.setItem(row, 0, QTableWidgetItem(task.project.name))
            self.tasks_table_widget.setItem(row, 1, QTableWidgetItem(task.name))
            self.tasks_table_widget.setItem(row, 2, QTableWidgetItem(task.start_date.strftime("%Y-%m-%d")))
            self.tasks_table_widget.setItem(row, 3, QTableWidgetItem(task.end_date.strftime("%Y-%m-%d")))
            self.tasks_table_widget.setItem(row, 4, QTableWidgetItem(task.description or ""))
            self.tasks_table_widget.setItem(row, 5, QTableWidgetItem(str(task.id)))

        self.tasks_table_widget.resizeColumnsToContents()
        self.tasks_table_widget.clearSelection()

    def update_time_entries_table_widget(self, task_id=None):
        if task_id is None:
            first_time_entry = self.session.query(TimeEntries).first()
            if first_time_entry:
                task_id = first_time_entry.task_id
            else:
                self.time_entries_table_widget.setRowCount(0)
                return

        query = self.session.query(TimeEntries)
        if task_id is not None:
            query = query.filter_by(task_id=task_id)

        time_entries = query.order_by(TimeEntries.timestamp_start).all()
        self.time_entries_table_widget.setRowCount(len(time_entries))

        for row, time_entry in enumerate(time_entries):
            task = self.session.query(Tasks).filter_by(id=time_entry.task_id).first()
            task_name = task.name if task else "Неизвестная задача"

            employee = self.session.query(Employees).filter_by(id=time_entry.employee_id).first()
            employee_fio = f"{employee.last_name} {employee.first_name} {employee.middle_name}" if employee else "Неизвестный сотрудник"

            self.time_entries_table_widget.setItem(row, 0, QTableWidgetItem(task_name))
            self.time_entries_table_widget.setItem(row, 1, QTableWidgetItem(employee_fio))
            self.time_entries_table_widget.setItem(row, 2, QTableWidgetItem(
                time_entry.timestamp_start.strftime("%Y-%m-%d %H:%M:%S")))
            self.time_entries_table_widget.setItem(row, 3, QTableWidgetItem(
                time_entry.timestamp_end.strftime("%Y-%m-%d %H:%M:%S")))
            self.time_entries_table_widget.setItem(row, 4, QTableWidgetItem(str(time_entry.id)))

        self.time_entries_table_widget.resizeColumnsToContents()
        self.time_entries_table_widget.clearSelection()

    def update_clients_table_widget(self):
        clients = self.session.query(Clients).all()
        self.clients_table_widget.setRowCount(len(clients))
        for row, client in enumerate(clients):
            self.clients_table_widget.setItem(row, 0, QTableWidgetItem(client.name))
            self.clients_table_widget.setItem(row, 1, QTableWidgetItem(client.contact_name))
            self.clients_table_widget.setItem(row, 2, QTableWidgetItem(client.email))
            self.clients_table_widget.setItem(row, 3, QTableWidgetItem(client.phone_number))
            self.clients_table_widget.setItem(row, 4, QTableWidgetItem(str(client.id)))
        self.clients_table_widget.resizeColumnsToContents()

    def update_positions_table_widget(self):
        positions = self.session.query(Positions).all()
        self.positions_table_widget.setRowCount(len(positions))
        for row, position in enumerate(positions):
            self.positions_table_widget.setItem(row, 0, QTableWidgetItem(position.name))
            employee_count = self.session.query(Employees).filter_by(position_id=position.id).count()
            self.positions_table_widget.setItem(row, 1, QTableWidgetItem(str(employee_count)))
            self.positions_table_widget.setItem(row, 2, QTableWidgetItem(str(position.id)))
        self.positions_table_widget.resizeColumnsToContents()

    def update_departments_table_widget(self):
        departments = self.session.query(Departments).all()
        self.departments_table_widget.setRowCount(len(departments))
        for row, department in enumerate(departments):
            self.departments_table_widget.setItem(row, 0, QTableWidgetItem(department.name))
            employee_count = self.session.query(Employees).filter_by(department_id=department.id).count()
            self.departments_table_widget.setItem(row, 1, QTableWidgetItem(str(employee_count)))
            self.departments_table_widget.setItem(row, 2, QTableWidgetItem(str(department.id)))
        self.departments_table_widget.resizeColumnsToContents()

    def update_report_table_widget(self):
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()
        selected_department = self.department_combobox.currentText()
        selected_position = self.position_combobox.currentText()
        selected_project = self.project_combobox.currentText()

        base_query = """
            SELECT 
                Employees.first_name, Employees.last_name, Employees.middle_name, 
                Departments.name AS Department, Employees.email, Employees.phone_number,
                Positions.name AS Position,
                SUM(time_entries.timestamp_end - time_entries.timestamp_start) AS total_time
            FROM Employees
            LEFT OUTER JOIN time_entries ON Employees.id = time_entries.employee_id
            LEFT OUTER JOIN Departments ON Employees.department_id = Departments.id
            LEFT OUTER JOIN Positions ON Employees.position_id = Positions.id
            LEFT OUTER JOIN Tasks ON time_entries.task_id = Tasks.id
            LEFT OUTER JOIN Projects ON Tasks.project_id = Projects.id
            WHERE DATE(time_entries.timestamp_start) >= :start_date
                AND DATE(time_entries.timestamp_end) <= :end_date
        """

        params = {'start_date': start_date, 'end_date': end_date}

        conditions = []

        if selected_project and selected_project != "Все проекты":
            conditions.append("Projects.name = :selected_project")
            params['selected_project'] = selected_project
        if selected_position and selected_position != "Все должности":
            conditions.append("Positions.name = :selected_position")
            params['selected_position'] = selected_position
        if selected_department and selected_department != "Все отделы":
            conditions.append("Departments.name = :selected_department")
            params['selected_department'] = selected_department

        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        base_query += """
            GROUP BY Employees.id, Departments.name, Employees.first_name, Employees.last_name, Employees.middle_name, Employees.email, Employees.phone_number, Positions.name
            ORDER BY total_time DESC
        """

        sql_query = text(base_query)

        report_data = self.session.execute(sql_query, params).fetchall()

        self.report_table_widget.setRowCount(len(report_data))

        for row, (first_name, last_name, middle_name, department, email, phone, position, total_time) in enumerate(
                report_data):
            self.report_table_widget.setItem(row, 0, QTableWidgetItem(f'{last_name} {first_name} {middle_name}'))
            self.report_table_widget.setItem(row, 1, QTableWidgetItem(department))
            self.report_table_widget.setItem(row, 2, QTableWidgetItem(position))
            self.report_table_widget.setItem(row, 3, QTableWidgetItem(email))
            self.report_table_widget.setItem(row, 4, QTableWidgetItem(phone))
            self.report_table_widget.setItem(row, 5, QTableWidgetItem(str(total_time)))

        self.report_table_widget.resizeColumnsToContents()

    def update_all_tables_widgets(self):
        self.update_report_comboBoxes()
        self.update_employees_table_widget()
        self.update_projects_table_widget()

        if self.projects_table_widget.rowCount() > 0:
            self.show_project_tasks(0)

        self.update_tasks_table_widget()

        if self.tasks_table_widget.rowCount() > 0:
            self.show_task_time_entries(0)

        self.update_clients_table_widget()
        self.update_positions_table_widget()
        self.update_departments_table_widget()
        self.update_report_table_widget()

    def employees_selection_changed(self, selected, deselected):
        self.button_edit_employee.setEnabled(len(selected.indexes()) > 0)
        self.button_delete_employee.setEnabled(len(selected.indexes()) > 0)

    def clients_selection_changed(self, selected, deselected):
        self.button_edit_client.setEnabled(len(selected.indexes()) > 0)
        self.button_delete_client.setEnabled(len(selected.indexes()) > 0)

    def projects_selection_changed(self, selected, deselected):
        self.button_edit_project.setEnabled(len(selected.indexes()) > 0)
        self.button_delete_project.setEnabled(len(selected.indexes()) > 0)
        self.button_add_task.setEnabled(len(selected.indexes()) > 0)

    def tasks_selection_changed(self, selected, deselected):
        self.button_edit_task.setEnabled(len(selected.indexes()) > 0)
        self.button_delete_task.setEnabled(len(selected.indexes()) > 0)
        self.button_add_time_entry.setEnabled(len(selected.indexes()) > 0)

    def time_entries_selection_changed(self, selected, deselected):
        self.button_edit_time_entry.setEnabled(len(selected.indexes()) > 0)
        self.button_delete_time_entry.setEnabled(len(selected.indexes()) > 0)

    def positions_selection_changed(self, selected, deselected):
        self.button_edit_position.setEnabled(len(selected.indexes()) > 0)
        self.button_delete_position.setEnabled(len(selected.indexes()) > 0)

    def departments_selection_changed(self, selected, deselected):
        self.button_edit_department.setEnabled(len(selected.indexes()) > 0)
        self.button_delete_department.setEnabled(len(selected.indexes()) > 0)

    def on_tab_changed(self, index):
        match index:
            case 0:
                self.update_employees_table_widget()
            case 1:
                self.update_clients_table_widget()
            case 2:
                self.update_projects_table_widget()
                if self.projects_table_widget.rowCount() > 0:
                    self.show_project_tasks(0)
                if self.tasks_table_widget.rowCount() > 0:
                    self.show_task_time_entries(0)
            case 3:
                self.update_positions_table_widget()
            case 4:
                self.update_departments_table_widget()
            case 5:
                self.update_report_comboBoxes()
                self.update_report_table_widget()

    def enable_confirm_button(self):

        start_date_str = self.start_date_edit.text()
        end_date_str = self.end_date_edit.text()

        if (self.department_combobox.currentText() == "Пусто" or
                self.position_combobox.currentText() == "Пусто" or
                self.project_combobox.currentText() == "Пусто"):
            self.reset_button.setEnabled(False)
            self.confirm_button.setEnabled(False)
            return

        try:
            start_date = QDate.fromString(start_date_str, "dd.MM.yyyy").toPython()
            end_date = QDate.fromString(end_date_str, "dd.MM.yyyy").toPython()
        except ValueError:
            self.confirm_button.setEnabled(False)
            return

        if start_date <= end_date:
            if self.session.query(TimeEntries).count() > 0:
                if (self.department_combobox.currentText() != "Пусто" or
                        self.position_combobox.currentText() != "Пусто" or
                        self.project_combobox.currentText() != "Пусто"):
                    self.confirm_button.setEnabled(True)
                    self.reset_button.setEnabled(True)
                else:
                    self.confirm_button.setEnabled(False)
                    self.reset_button.setEnabled(False)
            else:
                self.confirm_button.setEnabled(False)
                self.reset_button.setEnabled(False)
        else:
            self.confirm_button.setEnabled(False)
            self.reset_button.setEnabled(False)

    def show_project_tasks(self, row):
        project_id_str = self.projects_table_widget.item(row, 6).text()
        self.current_project_id = int(project_id_str) if project_id_str else None

        if self.current_project_id is not None:
            project = self.session.query(Projects).filter_by(id=self.current_project_id).first()

            if project:
                self.update_tasks_table_widget()

                top_project_id = self.session.query(Projects.id).order_by(Projects.id).first()

                if top_project_id:
                    tasks = self.session.query(Tasks).filter_by(project_id=top_project_id[0]).all()

                    if tasks:
                        self.show_task_time_entries(0)
                    else:
                        self.time_entries_table_widget.setRowCount(0)
                else:
                    self.time_entries_table_widget.setRowCount(0)
            else:
                self.current_project_id = None

        if self.current_project_id is None:
            self.update_tasks_table_widget()
            self.time_entries_table_widget.setRowCount(0)

    def show_task_time_entries(self, row):
        if self.tasks_table_widget.rowCount() > 0:
            task_id_str = self.tasks_table_widget.item(row, 5).text()
            self.current_task_id = int(task_id_str) if task_id_str else None

            if self.current_task_id is not None:
                task = self.session.query(Tasks).filter_by(id=self.current_task_id).first()

                if task:
                    self.update_time_entries_table_widget(task_id=self.current_task_id)
                else:
                    self.current_task_id = None
                    self.time_entries_table_widget.setRowCount(0)

            if self.current_task_id is None:
                self.time_entries_table_widget.setRowCount(0)
        else:
            self.time_entries_table_widget.setRowCount(0)

    def reset_report_table_widget(self):
        self.report_table_widget.clearContents()
        self.report_table_widget.setRowCount(0)
        self.report_table_widget.setHorizontalHeaderLabels([])

        self.project_combobox.setCurrentText("Все проекты")
        self.position_combobox.setCurrentText("Все должности")
        self.department_combobox.setCurrentText("Все отделы")

        current_date = QDate.currentDate()
        first_day_of_month = QDate(current_date.year(), current_date.month(), 1)
        last_day_of_month = QDate(current_date.year(), current_date.month(), current_date.daysInMonth())

        self.start_date_edit.setDate(first_day_of_month)
        self.end_date_edit.setDate(last_day_of_month)

        self.update_report_table_widget()

        self.report_table_widget.resizeColumnsToContents()


class AddPositionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание новой должности")
        self.setFixedSize(350, 70)

        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(255)

        self.name_input.textChanged.connect(self.enable_create_button)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)

        hbox = QHBoxLayout()
        hbox.addWidget(self.name_input)
        self.create_button = QPushButton("Сохранить")
        self.create_button.clicked.connect(self.save_position)
        self.create_button.setEnabled(False)
        hbox.addWidget(self.create_button)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def enable_create_button(self):
        self.create_button.setEnabled(bool(self.name_input.text()))

    def save_position(self):
        name = self.name_input.text()
        session = database.Session()

        existing_position = session.query(Positions).filter_by(name=name).first()
        if existing_position:
            QMessageBox.warning(self, "Предупреждение", "Должность с таким названием уже существует")
            session.close()
            return

        try:
            new_position = Positions(name=name)
            session.add(new_position)
            session.commit()
            session.close()

            QMessageBox.information(self, "Успешно", "Должность успешно создана")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать должность: {e}")
            session.rollback()
            session.close()


class EditPositionDialog(QDialog):
    def __init__(self, position_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование должности")
        self.setFixedSize(350, 70)

        self.position_id = position_id
        self.original_name = None

        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(255)

        self.load_position_data()

        self.name_input.textChanged.connect(self.enable_save_button)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)

        hbox = QHBoxLayout()
        hbox.addWidget(self.name_input)
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_position)
        self.save_button.setEnabled(False)
        hbox.addWidget(self.save_button)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def load_position_data(self):
        session = database.Session()
        position = session.query(Positions).filter_by(id=self.position_id).first()
        session.close()

        if position:
            self.name_input.setText(position.name)
            self.original_name = position.name
        else:
            QMessageBox.warning(self, "Ошибка", "Должность не найдена")
            self.close()

    def enable_save_button(self):
        new_name = self.name_input.text()
        self.save_button.setEnabled(bool(new_name) and new_name != self.original_name)

    def save_position(self):
        new_name = self.name_input.text()

        session = database.Session()
        existing_position = session.query(Positions).filter_by(name=new_name).first()
        session.close()

        if existing_position and existing_position.id != self.position_id:
            QMessageBox.warning(self, "Предупреждение", "Должность с таким названием уже существует")
            return

        session = database.Session()
        try:
            position = session.query(Positions).filter_by(id=self.position_id).first()
            if position:
                position.name = new_name
                session.commit()
                QMessageBox.information(self, "Успешно", "Должность успешно обновлена")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Должность не найдена")
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить должность: {e}")
            session.rollback()
            session.close()


class AddDepartmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание нового отдела")
        self.setFixedSize(350, 70)

        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(255)

        self.name_input.textChanged.connect(self.enable_create_button)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)

        hbox = QHBoxLayout()
        hbox.addWidget(self.name_input)
        self.create_button = QPushButton("Сохранить")
        self.create_button.clicked.connect(self.save_department)
        self.create_button.setEnabled(False)
        hbox.addWidget(self.create_button)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def enable_create_button(self):
        self.create_button.setEnabled(bool(self.name_input.text()))

    def save_department(self):
        name = self.name_input.text()
        session = database.Session()

        existing_department = session.query(Departments).filter_by(name=name).first()
        if existing_department:
            QMessageBox.warning(self, "Предупреждение", "Отдел с таким названием уже существует")
            session.close()
            return

        try:
            new_department = Departments(name=name)
            session.add(new_department)
            session.commit()
            session.close()

            QMessageBox.information(self, "Успешно", "Отдел успешно создан")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать отдел: {e}")
            session.rollback()
            session.close()


class EditDepartmentDialog(QDialog):
    def __init__(self, department_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование отдела")
        self.setFixedSize(350, 70)

        self.department_id = department_id
        self.original_name = None

        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(255)

        self.load_department_data()

        self.name_input.textChanged.connect(self.enable_save_button)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)

        hbox = QHBoxLayout()
        hbox.addWidget(self.name_input)
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_department)
        self.save_button.setEnabled(False)
        hbox.addWidget(self.save_button)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def load_department_data(self):
        session = database.Session()
        department = session.query(Departments).filter_by(id=self.department_id).first()
        session.close()

        if department:
            self.name_input.setText(department.name)
            self.original_name = department.name
        else:
            QMessageBox.warning(self, "Ошибка", "Отдел не найден")
            self.close()

    def enable_save_button(self):
        new_name = self.name_input.text()
        self.save_button.setEnabled(bool(new_name) and new_name != self.original_name)

    def save_department(self):
        new_name = self.name_input.text()

        session = database.Session()
        existing_department = session.query(Departments).filter_by(name=new_name).first()
        session.close()

        if existing_department and existing_department.id != self.department_id:
            QMessageBox.warning(self, "Предупреждение", "Отдел с таким названием уже существует")
            return

        session = database.Session()
        try:
            department = session.query(Departments).filter_by(id=self.department_id).first()
            if department:
                department.name = new_name
                session.commit()
                QMessageBox.information(self, "Успешно", "Отдел успешно обновлен")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Отдел не найден")
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить отдел: {e}")
            session.rollback()
            session.close()


class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание нового сотрудника")
        self.setFixedSize(360, 584)

        session = database.Session()

        layout = QVBoxLayout()

        self.last_name_label = QLabel("Фамилия:")
        self.last_name_edit = QLineEdit()
        layout.addWidget(self.last_name_label)
        layout.addWidget(self.last_name_edit)

        self.first_name_label = QLabel("Имя:")
        self.first_name_edit = QLineEdit()
        layout.addWidget(self.first_name_label)
        layout.addWidget(self.first_name_edit)

        self.middle_name_label = QLabel("Отчество:")
        self.middle_name_edit = QLineEdit()
        layout.addWidget(self.middle_name_label)
        layout.addWidget(self.middle_name_edit)

        self.birth_date_label = QLabel("Дата рождения:")
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.birth_date_label)
        layout.addWidget(self.birth_date_edit)

        self.gender_label = QLabel("Пол:")
        self.male_radio = QRadioButton("Мужской")
        self.female_radio = QRadioButton("Женский")
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        layout.addWidget(self.gender_label)
        layout.addLayout(gender_layout)

        self.hire_date_label = QLabel("Дата приема на работу:")
        self.hire_date_edit = QDateEdit()
        self.hire_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.hire_date_label)
        layout.addWidget(self.hire_date_edit)

        self.department_label = QLabel("Отдел:")
        self.department_combo = QComboBox()
        departments = session.query(database.Departments).all()
        if departments:
            self.department_combo.addItems([d.name for d in departments])
        else:
            self.department_combo.addItem("Пусто")
            self.department_combo.setEnabled(False)
        layout.addWidget(self.department_label)
        layout.addWidget(self.department_combo)

        self.position_label = QLabel("Должность:")
        self.position_combo = QComboBox()
        positions = session.query(database.Positions).all()
        if positions:
            self.position_combo.addItems([p.name for p in positions])
        else:
            self.position_combo.addItem("Пусто")
            self.position_combo.setEnabled(False)
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_combo)

        self.salary_label = QLabel("Заработная плата (в месяц):")
        self.salary_edit = QLineEdit()
        layout.addWidget(self.salary_label)
        layout.addWidget(self.salary_edit)

        self.email_label = QLabel("Адрес электронной почты:")
        self.email_edit = QLineEdit()
        self.email_edit.setMaxLength(255)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_edit)

        self.phone_number_label = QLabel("Контактный телефон:")
        self.phone_number_edit = QLineEdit()
        self.phone_number_edit.setMaxLength(255)
        layout.addWidget(self.phone_number_label)
        layout.addWidget(self.phone_number_edit)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_employee)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.last_name_edit.textChanged.connect(self.enable_save_button)
        self.first_name_edit.textChanged.connect(self.enable_save_button)
        self.birth_date_edit.dateChanged.connect(self.enable_save_button)
        self.male_radio.toggled.connect(self.enable_save_button)
        self.female_radio.toggled.connect(self.enable_save_button)
        self.hire_date_edit.dateChanged.connect(self.enable_save_button)
        self.department_combo.currentTextChanged.connect(self.enable_save_button)
        self.position_combo.currentTextChanged.connect(self.enable_save_button)
        self.salary_edit.textChanged.connect(self.enable_save_button)
        self.email_edit.textChanged.connect(self.enable_save_button)
        self.phone_number_edit.textChanged.connect(self.enable_save_button)

    def enable_save_button(self):
        last_name_valid = bool(self.last_name_edit.text())
        first_name_valid = bool(self.first_name_edit.text())
        birth_date_valid = bool(self.birth_date_edit.date())
        hire_date_valid = bool(self.hire_date_edit.date())
        department_valid = self.department_combo.currentText() != "Пусто"
        position_valid = self.position_combo.currentText() != "Пусто"
        salary_valid = bool(self.salary_edit.text())
        email_valid = bool(self.email_edit.text())
        phone_number_valid = bool(self.phone_number_edit.text())
        gender_valid = self.male_radio.isChecked() or self.female_radio.isChecked()

        birth_date = self.birth_date_edit.date().toPython()
        hire_date = self.hire_date_edit.date().toPython()

        if birth_date > hire_date:
            birth_date_valid = False

        self.save_button.setEnabled(
            last_name_valid
            and first_name_valid
            and birth_date_valid
            and hire_date_valid
            and department_valid
            and position_valid
            and salary_valid
            and email_valid
            and phone_number_valid
            and gender_valid
        )

    def save_employee(self):
        first_name = self.first_name_edit.text()
        last_name = self.last_name_edit.text()
        middle_name = self.middle_name_edit.text()
        birth_date = datetime.date(self.birth_date_edit.date().year(), self.birth_date_edit.date().month(),
                                   self.birth_date_edit.date().day())
        gender = self.female_radio.isChecked()
        hire_date = datetime.date(self.hire_date_edit.date().year(), self.hire_date_edit.date().month(),
                                  self.hire_date_edit.date().day())
        department_name = self.department_combo.currentText()
        position_name = self.position_combo.currentText()
        salary = self.salary_edit.text()
        email = self.email_edit.text()
        phone_number = self.phone_number_edit.text()
        session = database.Session()

        if not self.validate_salary(salary):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Заработная плата\"")
            return
        if not self.validate_email(email):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Адрес электронной почты\"")
            return
        if not self.validate_phone_number(phone_number):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Контактный телефон\"")
            return

        existing_email = session.query(database.Employees).filter_by(email=email).first()
        if existing_email:
            QMessageBox.warning(self, "Предупреждение", "Сотрудник с таким адресом электронной почты уже существует")
            return
        existing_phone_number = session.query(database.Employees).filter_by(phone_number=phone_number).first()
        if existing_phone_number:
            QMessageBox.warning(self, "Предупреждение", "Сотрудник с таким контактным телефоном уже существует")
            return

        department = session.query(database.Departments).filter_by(name=department_name).first()
        position = session.query(database.Positions).filter_by(name=position_name).first()

        try:
            employee = database.Employees(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                birth_date=birth_date,
                gender=gender,
                hire_date=hire_date,
                department=department,
                position=position,
                salary=salary,
                email=email,
                phone_number=phone_number
            )

            session.add(employee)
            session.commit()
            session.close()

            QMessageBox.information(self, "Успешно", "Сотрудник успешно создан")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать сотрудника: {e}")
            session.rollback()
            session.close()

    def validate_salary(self, salary):
        regex = QRegularExpression(r"^\d+(\.\d{1,2})?$")
        return regex.match(salary).hasMatch()

    def validate_email(self, email):
        regex = QRegularExpression(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{1,}$")
        return regex.match(email).hasMatch()

    def validate_phone_number(self, phone_number):
        regex = QRegularExpression(r"^[0-9]{1,}$")
        return regex.match(phone_number).hasMatch()


class EditEmployeeDialog(QDialog):
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование сотрудника")
        self.setFixedSize(360, 584)

        self.employee_id = employee_id
        self.original_first_name = None
        self.original_last_name = None
        self.original_middle_name = None
        self.original_birth_date = None
        self.original_gender = None
        self.original_hire_date = None
        self.original_department_name = None
        self.original_position_name = None
        self.original_salary = None
        self.original_email = None
        self.original_phone_number = None

        session = database.Session()
        session.close()

        layout = QVBoxLayout()

        self.last_name_label = QLabel("Фамилия:")
        self.last_name_edit = QLineEdit()
        layout.addWidget(self.last_name_label)
        layout.addWidget(self.last_name_edit)

        self.first_name_label = QLabel("Имя:")
        self.first_name_edit = QLineEdit()
        layout.addWidget(self.first_name_label)
        layout.addWidget(self.first_name_edit)

        self.middle_name_label = QLabel("Отчество:")
        self.middle_name_edit = QLineEdit()
        layout.addWidget(self.middle_name_label)
        layout.addWidget(self.middle_name_edit)

        self.birth_date_label = QLabel("Дата рождения:")
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.birth_date_label)
        layout.addWidget(self.birth_date_edit)

        self.gender_label = QLabel("Пол:")
        self.male_radio = QRadioButton("Мужской")
        self.female_radio = QRadioButton("Женский")
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        layout.addWidget(self.gender_label)
        layout.addLayout(gender_layout)

        self.hire_date_label = QLabel("Дата приема на работу:")
        self.hire_date_edit = QDateEdit()
        self.hire_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.hire_date_label)
        layout.addWidget(self.hire_date_edit)

        self.department_label = QLabel("Отдел:")
        self.department_combo = QComboBox()
        layout.addWidget(self.department_label)
        layout.addWidget(self.department_combo)

        self.position_label = QLabel("Должность:")
        self.position_combo = QComboBox()
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_combo)

        self.salary_label = QLabel("Заработная плата (в месяц):")
        self.salary_edit = QLineEdit()
        layout.addWidget(self.salary_label)
        layout.addWidget(self.salary_edit)

        self.email_label = QLabel("Адрес электронной почты:")
        self.email_edit = QLineEdit()
        self.email_edit.setMaxLength(255)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_edit)

        self.phone_number_label = QLabel("Контактный телефон:")
        self.phone_number_edit = QLineEdit()
        self.phone_number_edit.setMaxLength(255)
        layout.addWidget(self.phone_number_label)
        layout.addWidget(self.phone_number_edit)

        self.fill_combo_boxes(session)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_employee)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.last_name_edit.textChanged.connect(self.enable_save_button)
        self.first_name_edit.textChanged.connect(self.enable_save_button)
        self.middle_name_edit.textChanged.connect(self.enable_save_button)
        self.birth_date_edit.dateChanged.connect(self.enable_save_button)
        self.male_radio.toggled.connect(self.enable_save_button)
        self.female_radio.toggled.connect(self.enable_save_button)
        self.hire_date_edit.dateChanged.connect(self.enable_save_button)
        self.department_combo.currentTextChanged.connect(self.enable_save_button)
        self.position_combo.currentTextChanged.connect(self.enable_save_button)
        self.salary_edit.textChanged.connect(self.enable_save_button)
        self.email_edit.textChanged.connect(self.enable_save_button)
        self.phone_number_edit.textChanged.connect(self.enable_save_button)

        self.load_employee_data()

    def fill_combo_boxes(self, session):
        departments = session.query(Departments).all()
        if departments:
            self.department_combo.addItems([d.name for d in departments])
        else:
            self.department_combo.addItem("Пусто")
            self.department_combo.setEnabled(False)

        positions = session.query(Positions).all()
        if positions:
            self.position_combo.addItems([p.name for p in positions])
        else:
            self.position_combo.addItem("Пусто")
            self.position_combo.setEnabled(False)

    def load_employee_data(self):
        session = database.Session()
        try:
            employee = session.query(Employees).options(
                joinedload(Employees.department),
                joinedload(Employees.position)
            ).filter_by(id=self.employee_id).first()

            if employee:
                self.last_name_edit.setText(employee.last_name)
                self.original_last_name = employee.last_name
                self.first_name_edit.setText(employee.first_name)
                self.original_first_name = employee.first_name
                self.middle_name_edit.setText(employee.middle_name)
                self.original_middle_name = employee.middle_name
                self.birth_date_edit.setDate(
                    QDate(employee.birth_date.year, employee.birth_date.month, employee.birth_date.day))
                self.original_birth_date = employee.birth_date
                if employee.gender:
                    self.female_radio.setChecked(True)
                    self.original_gender = True
                else:
                    self.male_radio.setChecked(True)
                    self.original_gender = False
                self.hire_date_edit.setDate(
                    QDate(employee.hire_date.year, employee.hire_date.month, employee.hire_date.day))
                self.original_hire_date = employee.hire_date
                if employee.department:
                    self.department_combo.setCurrentText(employee.department.name)
                    self.original_department_name = employee.department.name
                else:
                    self.department_combo.setCurrentText("Пусто")
                if employee.position:
                    self.position_combo.setCurrentText(employee.position.name)
                    self.original_position_name = employee.position.name
                else:
                    self.position_combo.setCurrentText("Пусто")
                self.salary_edit.setText(str(employee.salary))
                self.original_salary = employee.salary
                self.email_edit.setText(employee.email)
                self.original_email = employee.email
                self.phone_number_edit.setText(employee.phone_number)
                self.original_phone_number = employee.phone_number

                self.save_button.setEnabled(False)
            else:
                QMessageBox.warning(self, "Ошибка", "Сотрудник не найден")
                self.close()
        finally:
            session.close()

    def enable_save_button(self):
        last_name_valid = bool(self.last_name_edit.text())
        first_name_valid = bool(self.first_name_edit.text())
        birth_date_valid = bool(self.birth_date_edit.date())
        hire_date_valid = bool(self.hire_date_edit.date())
        department_valid = self.department_combo.currentText() != "Пусто"
        position_valid = self.position_combo.currentText() != "Пусто"
        salary_valid = bool(self.salary_edit.text())
        email_valid = bool(self.email_edit.text())
        phone_number_valid = bool(self.phone_number_edit.text())
        gender_valid = self.male_radio.isChecked() or self.female_radio.isChecked()

        birth_date = self.birth_date_edit.date().toPython()
        hire_date = self.hire_date_edit.date().toPython()

        if birth_date > hire_date:
            birth_date_valid = False

        session = database.Session()
        try:
            employee = session.query(Employees).filter_by(id=self.employee_id).first()
            if employee:
                projects = session.query(Projects).filter_by(manager_id=self.employee_id).all()
                if projects:
                    latest_project_end_date = max(project.end_date for project in projects)
                    if latest_project_end_date is not None and latest_project_end_date >= hire_date:
                        hire_date_valid = False

            latest_time_entry_end = session.query(func.max(TimeEntries.timestamp_end)).filter_by(
                employee_id=self.employee_id).scalar()

            hire_date_timestamp = datetime.datetime.combine(hire_date, datetime.datetime.min.time())

            if latest_time_entry_end:
                if hire_date_timestamp >= latest_time_entry_end:
                    hire_date_valid = False

            self.save_button.setEnabled(
                last_name_valid
                and first_name_valid
                and birth_date_valid
                and hire_date_valid
                and department_valid
                and position_valid
                and salary_valid
                and email_valid
                and phone_number_valid
                and gender_valid)
        finally:
            session.close()

    def save_employee(self):
        first_name = self.first_name_edit.text()
        last_name = self.last_name_edit.text()
        middle_name = self.middle_name_edit.text()
        birth_date = datetime.date(self.birth_date_edit.date().year(), self.birth_date_edit.date().month(),
                                   self.birth_date_edit.date().day())
        gender = self.female_radio.isChecked()
        hire_date = datetime.date(self.hire_date_edit.date().year(), self.hire_date_edit.date().month(),
                                  self.hire_date_edit.date().day())
        department_name = self.department_combo.currentText()
        position_name = self.position_combo.currentText()
        salary = self.salary_edit.text()
        email = self.email_edit.text()
        phone_number = self.phone_number_edit.text()
        session = database.Session()

        if not self.validate_salary(salary):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Заработная плата\"")
            return
        if not self.validate_email(email):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Адрес электронной почты\"")
            return
        if not self.validate_phone_number(phone_number):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Контактный телефон\"")
            return

        existing_email = session.query(Employees).filter_by(email=email).first()
        if existing_email and existing_email.id != self.employee_id:
            QMessageBox.warning(self, "Предупреждение", "Сотрудник с таким адресом электронной почты уже существует")
            return
        existing_phone_number = session.query(Employees).filter_by(phone_number=phone_number).first()
        if existing_phone_number and existing_phone_number.id != self.employee_id:
            QMessageBox.warning(self, "Предупреждение", "Сотрудник с таким контактным телефоном уже существует")
            return

        try:
            employee = session.query(Employees).filter_by(id=self.employee_id).first()
            if employee:
                employee.first_name = first_name
                employee.last_name = last_name
                employee.middle_name = middle_name
                employee.birth_date = birth_date
                employee.gender = gender
                employee.hire_date = hire_date
                if department_name != "Пусто":
                    department = session.query(Departments).filter_by(name=department_name).first()
                    employee.department_id = department.id
                if position_name != "Пусто":
                    position = session.query(Positions).filter_by(name=position_name).first()
                    employee.position_id = position.id
                employee.salary = float(salary)
                employee.email = email
                employee.phone_number = phone_number
                session.commit()
                QMessageBox.information(self, "Успех", "Данные сотрудника успешно обновлены")
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Сотрудник не найден")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при сохранении данных сотрудника: {e}")
        finally:
            session.close()

    def validate_salary(self, salary):
        try:
            return float(salary) > 0
        except ValueError:
            return False

    def validate_email(self, email):
        regex = QRegularExpression(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{1,}$")
        return regex.match(email).hasMatch()

    def validate_phone_number(self, phone_number):
        regex = QRegularExpression(r"^[0-9]{1,}$")
        return regex.match(phone_number).hasMatch()


class AddClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание нового клиента")
        self.setFixedSize(360, 290)

        layout = QVBoxLayout()

        self.name_label = QLabel("Наименование клиента:")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(255)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)

        self.contact_name_label = QLabel("Контактное лицо:")
        self.contact_name_edit = QLineEdit()
        self.contact_name_edit.setMaxLength(255)
        layout.addWidget(self.contact_name_label)
        layout.addWidget(self.contact_name_edit)

        self.email_label = QLabel("Адрес электронной почты:")
        self.email_edit = QLineEdit()
        self.email_edit.setMaxLength(255)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_edit)

        self.phone_number_label = QLabel("Контактный телефон:")
        self.phone_number_edit = QLineEdit()
        self.phone_number_edit.setMaxLength(255)
        layout.addWidget(self.phone_number_label)
        layout.addWidget(self.phone_number_edit)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_client)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)

        self.name_edit.textChanged.connect(self.enable_save_button)
        self.contact_name_edit.textChanged.connect(self.enable_save_button)
        self.email_edit.textChanged.connect(self.enable_save_button)
        self.phone_number_edit.textChanged.connect(self.enable_save_button)

        self.setLayout(layout)

    def enable_save_button(self):
        self.save_button.setEnabled(
            bool(self.name_edit.text())
            and bool(self.contact_name_edit.text())
            and bool(self.email_edit.text())
            and bool(self.phone_number_edit.text())
        )

    def save_client(self):
        session = database.Session()
        name = self.name_edit.text()
        contact_name = self.contact_name_edit.text()
        email = self.email_edit.text()
        phone_number = self.phone_number_edit.text()

        if not self.validate_email(email):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Адрес электронной почты\"")
            return
        if not self.validate_phone_number(phone_number):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Контактный телефон\"")
            return

        existing_client_by_name = session.query(Clients).filter_by(name=name).first()
        if existing_client_by_name:
            QMessageBox.warning(self, "Предупреждение", "Клиент с таким наименованием уже существует")
            session.close()
            return

        try:
            client = Clients(
                name=name,
                contact_name=contact_name,
                email=email,
                phone_number=phone_number,
            )

            session.add(client)
            session.commit()
            session.close()

            QMessageBox.information(self, "Успешно", "Клиент успешно создан")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать клиента: {e}")
            session.rollback()
            session.close()

    def validate_email(self, email):
        regex = QRegularExpression(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{1,}$")
        return regex.match(email).hasMatch()

    def validate_phone_number(self, phone_number):
        regex = QRegularExpression(r"^[0-9]{1,}$")
        return regex.match(phone_number).hasMatch()


class EditClientDialog(QDialog):
    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование клиента")
        self.setFixedSize(360, 290)

        self.client_id = client_id
        self.original_name = None
        self.original_contact_name = None
        self.original_email = None
        self.original_phone_number = None

        layout = QVBoxLayout()

        self.name_label = QLabel("Наименование клиента:")
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(255)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)

        self.contact_name_label = QLabel("Контактное лицо:")
        self.contact_name_edit = QLineEdit()
        self.contact_name_edit.setMaxLength(255)
        layout.addWidget(self.contact_name_label)
        layout.addWidget(self.contact_name_edit)

        self.email_label = QLabel("Адрес электронной почты:")
        self.email_edit = QLineEdit()
        self.email_edit.setMaxLength(255)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_edit)

        self.phone_number_label = QLabel("Контактный телефон:")
        self.phone_number_edit = QLineEdit()
        self.phone_number_edit.setMaxLength(255)
        layout.addWidget(self.phone_number_label)
        layout.addWidget(self.phone_number_edit)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_client)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)

        self.name_edit.textChanged.connect(self.enable_save_button)
        self.contact_name_edit.textChanged.connect(self.enable_save_button)
        self.email_edit.textChanged.connect(self.enable_save_button)
        self.phone_number_edit.textChanged.connect(self.enable_save_button)

        self.setLayout(layout)

        self.load_client_data()

    def load_client_data(self):
        session = database.Session()
        client = session.query(Clients).filter_by(id=self.client_id).first()
        session.close()

        if client:
            self.name_edit.setText(client.name)
            self.original_name = client.name

            self.contact_name_edit.setText(client.contact_name)
            self.original_contact_name = client.contact_name

            self.email_edit.setText(client.email)
            self.original_email = client.email

            self.phone_number_edit.setText(client.phone_number)
            self.original_phone_number = client.phone_number

            self.save_button.setEnabled(False)
        else:
            QMessageBox.warning(self, "Ошибка", "Клиент не найден")
            self.close()

    def enable_save_button(self):
        changed = (
                self.name_edit.text() != self.original_name
                or self.contact_name_edit.text() != self.original_contact_name
                or self.email_edit.text() != self.original_email
                or self.phone_number_edit.text() != self.original_phone_number
        )
        self.save_button.setEnabled(changed)

    def save_client(self):
        session = database.Session()
        name = self.name_edit.text()
        contact_name = self.contact_name_edit.text()
        email = self.email_edit.text()
        phone_number = self.phone_number_edit.text()

        if not self.validate_email(email):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Адрес электронной почты\"")
            return
        if not self.validate_phone_number(phone_number):
            QMessageBox.warning(self, "Предупреждение", "Некорректное значение в поле \"Контактный телефон\"")
            return

        existing_client = session.query(Clients).filter(
            Clients.name == name, Clients.id != self.client_id
        ).first()

        if existing_client:
            QMessageBox.warning(self, "Предупреждение", "Клиент с таким наименованием уже существует")
            session.close()
            return

        try:
            client = session.query(Clients).filter_by(id=self.client_id).first()
            if client:
                client.name = name
                client.contact_name = contact_name
                client.email = email
                client.phone_number = phone_number
                session.commit()
                QMessageBox.information(self, "Успешно", "Клиент успешно обновлен")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Клиент не найден")
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить клиента: {e}")
            session.rollback()
            session.close()

    def validate_email(self, email):
        regex = QRegularExpression(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{1,}$")
        return regex.match(email).hasMatch()

    def validate_phone_number(self, phone_number):
        regex = QRegularExpression(r"^[0-9]{1,}$")
        return regex.match(phone_number).hasMatch()


class AddProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание нового проекта")
        self.setFixedSize(390, 500)

        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(255)
        self.name_input.textChanged.connect(self.enable_create_button)

        self.client_label = QLabel("Наименование клиента:")
        self.client_combo = QComboBox()
        session = database.Session()
        clients = session.query(Clients).all()
        session.close()
        if clients:
            for client in clients:
                self.client_combo.addItem(client.name, client.id)
        else:
            self.client_combo.addItem("Пусто")
            self.client_combo.setEnabled(False)
        self.client_combo.currentIndexChanged.connect(self.enable_create_button)

        self.manager_label = QLabel("Руководитель:")
        self.manager_combo = QComboBox()
        session = database.Session()
        managers = session.query(Employees).all()
        session.close()
        if managers:
            for manager in managers:
                manager_full_name = f"{manager.last_name} {manager.first_name} {manager.middle_name}"
                self.manager_combo.addItem(manager_full_name, manager.id)
        else:
            self.manager_combo.addItem("Пусто")
            self.manager_combo.setEnabled(False)
        self.manager_combo.currentIndexChanged.connect(self.enable_create_button)

        self.start_date_label = QLabel("Дата начала:")
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.dateChanged.connect(self.enable_create_button)

        self.end_date_label = QLabel("Дата окончания:")
        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.dateChanged.connect(self.enable_create_button)

        self.description_label = QLabel("Описание:")
        self.description_input = QTextEdit()
        self.description_input.textChanged.connect(self.enable_create_button)

        self.create_button = QPushButton("Сохранить")
        self.create_button.clicked.connect(self.save_project)
        self.create_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.client_label)
        layout.addWidget(self.client_combo)
        layout.addWidget(self.manager_label)
        layout.addWidget(self.manager_combo)
        layout.addWidget(self.start_date_label)
        layout.addWidget(self.start_date_input)
        layout.addWidget(self.end_date_label)
        layout.addWidget(self.end_date_input)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

    def enable_create_button(self):
        name_valid = bool(self.name_input.text())
        client_valid = self.client_combo.currentText() != "Пусто"
        manager_valid = self.manager_combo.currentText() != "Пусто"
        start_date_valid = bool(self.start_date_input.date())
        end_date_valid = bool(self.end_date_input.date())
        if end_date_valid and start_date_valid and self.end_date_input.date() < self.start_date_input.date():
            end_date_valid = False
        description_valid = len(self.description_input.toPlainText()) <= 65535

        if start_date_valid and manager_valid:
            manager_id = self.manager_combo.currentData()
            session = database.Session()
            manager = session.query(Employees).filter_by(id=manager_id).first()
            session.close()
            if manager and self.start_date_input.date() < manager.hire_date:
                start_date_valid = False

        self.create_button.setEnabled(
            name_valid
            and client_valid
            and manager_valid
            and start_date_valid
            and end_date_valid
            and description_valid
        )

    def save_project(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        client_id = self.client_combo.currentData()
        manager_id = self.manager_combo.currentData()
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()

        session = database.Session()

        existing_project = session.query(Projects).filter_by(name=name).first()
        if existing_project:
            QMessageBox.warning(self, "Предупреждение", "Проект с таким названием уже существует")
            session.close()
            return

        try:
            new_project = Projects(
                name=name,
                description=description,
                client_id=client_id,
                manager_id=manager_id,
                start_date=start_date,
                end_date=end_date,
            )
            session.add(new_project)
            session.commit()
            session.close()

            QMessageBox.information(self, "Успешно", "Проект успешно создан")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать проект: {e}")
            session.rollback()
            session.close()


class EditProjectDialog(QDialog):
    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование проекта")
        self.setFixedSize(390, 500)

        self.project_id = project_id
        self.original_name = None
        self.original_description = None
        self.original_client_id = None
        self.original_manager_id = None
        self.original_start_date = None
        self.original_end_date = None

        session = database.Session()
        try:
            clients = session.query(database.Clients).all()
            managers = session.query(database.Employees).all()
        finally:
            session.close()

        layout = QVBoxLayout()

        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(255)
        self.name_input.textChanged.connect(self.enable_save_button)

        self.client_label = QLabel("Наименование клиента:")
        self.client_combo = QComboBox()
        if clients:
            for client in clients:
                self.client_combo.addItem(client.name, client.id)
        else:
            self.client_combo.addItem("Пусто")
            self.client_combo.setEnabled(False)
        self.client_combo.currentIndexChanged.connect(self.enable_save_button)

        self.manager_label = QLabel("Руководитель:")
        self.manager_combo = QComboBox()
        if managers:
            for manager in managers:
                manager_full_name = f"{manager.last_name} {manager.first_name} {manager.middle_name}"
                self.manager_combo.addItem(manager_full_name, manager.id)
        else:
            self.manager_combo.addItem("Пусто")
            self.manager_combo.setEnabled(False)
        self.manager_combo.currentIndexChanged.connect(self.enable_save_button)

        self.start_date_label = QLabel("Дата начала:")
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.dateChanged.connect(self.enable_save_button)

        self.end_date_label = QLabel("Дата окончания:")
        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.dateChanged.connect(self.enable_save_button)

        self.description_label = QLabel("Описание:")
        self.description_input = QTextEdit()
        self.description_input.textChanged.connect(self.enable_save_button)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_project)
        self.save_button.setEnabled(False)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.client_label)
        layout.addWidget(self.client_combo)
        layout.addWidget(self.manager_label)
        layout.addWidget(self.manager_combo)
        layout.addWidget(self.start_date_label)
        layout.addWidget(self.start_date_input)
        layout.addWidget(self.end_date_label)
        layout.addWidget(self.end_date_input)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.load_project_data()

    def load_project_data(self):
        session = database.Session()
        try:
            project = session.query(database.Projects).filter_by(id=self.project_id).first()

            if project:
                self.name_input.setText(project.name)
                self.original_name = project.name
                self.client_combo.setCurrentIndex(self.client_combo.findData(project.client_id))
                self.original_client_id = project.client_id
                self.manager_combo.setCurrentIndex(self.manager_combo.findData(project.manager_id))
                self.original_manager_id = project.manager_id
                self.original_start_date = project.start_date
                self.original_end_date = project.end_date
                self.start_date_input.setDate(
                    QDate(project.start_date.year, project.start_date.month, project.start_date.day))
                self.end_date_input.setDate(QDate(project.end_date.year, project.end_date.month, project.end_date.day))
                self.description_input.setText(project.description)
                self.original_description = project.description

                self.enable_save_button()
            else:
                QMessageBox.warning(self, "Ошибка", "Проект не найден")
                self.close()
        finally:
            session.close()

    def enable_save_button(self):
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()

        session = database.Session()
        try:
            tasks = session.query(database.Tasks).filter_by(project_id=self.project_id).all()

            if tasks:
                earliest_task_start = min(task.start_date for task in tasks)
                latest_task_end = max(task.end_date for task in tasks)

                changed = (
                        self.name_input.text() != self.original_name
                        or self.client_combo.currentData() != self.original_client_id
                        or self.manager_combo.currentData() != self.original_manager_id
                        or start_date != self.original_start_date
                        or end_date != self.original_end_date
                        or self.description_input.toPlainText() != self.original_description
                )

                valid_dates = start_date <= earliest_task_start and end_date >= latest_task_end

                manager_id = self.manager_combo.currentData()
                if manager_id:
                    manager = session.query(Employees).filter_by(id=manager_id).first()
                    if manager and start_date < manager.hire_date:
                        valid_dates = False

                self.save_button.setEnabled(changed and valid_dates and start_date <= end_date)
                return

        finally:
            session.close()

        changed = (
                self.name_input.text() != self.original_name
                or self.client_combo.currentData() != self.original_client_id
                or self.manager_combo.currentData() != self.original_manager_id
                or start_date != self.original_start_date
                or end_date != self.original_end_date
                or self.description_input.toPlainText() != self.original_description
        )

        manager_id = self.manager_combo.currentData()
        if manager_id:
            session = database.Session()
            manager = session.query(Employees).filter_by(id=manager_id).first()
            session.close()
            if manager and start_date < manager.hire_date:
                changed = False

        self.save_button.setEnabled(changed and start_date <= end_date)

    def save_project(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        client_id = self.client_combo.currentData()
        manager_id = self.manager_combo.currentData()
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()

        session = database.Session()

        existing_project = session.query(database.Projects).filter_by(name=name).first()
        if existing_project and existing_project.id != self.project_id:
            QMessageBox.warning(self, "Предупреждение", "Проект с таким названием уже существует")
            session.close()
            return

        try:
            project = session.query(database.Projects).filter_by(id=self.project_id).first()
            if project:
                project.name = name
                project.description = description
                project.client_id = client_id
                project.manager_id = manager_id
                project.start_date = start_date
                project.end_date = end_date

                session.commit()
                QMessageBox.information(self, "Успех", "Данные проекта успешно обновлены")
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Проект не найден")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при сохранении данных проекта: {e}")
        finally:
            session.close()


class AddTaskDialog(QDialog):
    def __init__(self, parent=None, project_id=None):
        super().__init__(parent)
        self.setWindowTitle("Создание новой задачи")
        self.setFixedSize(390, 450)

        self.project_id = project_id

        self.project_label = QLabel("Проект:")
        self.project_input = QLineEdit()
        self.project_input.setReadOnly(True)

        session = database.Session()
        self.project = session.query(Projects).filter_by(id=self.project_id).first()
        if self.project:
            self.project_input.setText(self.project.name)
        else:
            self.project_input.setText("Неизвестный проект")
        session.close()

        self.name_label = QLabel("Название:")
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(255)

        self.start_date_label = QLabel("Дата начала:")
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())

        self.end_date_label = QLabel("Дата окончания:")
        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate())

        self.description_label = QLabel("Описание:")
        self.description_input = QTextEdit()

        self.create_button = QPushButton("Сохранить")
        self.create_button.clicked.connect(self.save_task)
        self.create_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.project_label)
        layout.addWidget(self.project_input)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.start_date_label)
        layout.addWidget(self.start_date_input)
        layout.addWidget(self.end_date_label)
        layout.addWidget(self.end_date_input)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

        self.start_date_input.dateChanged.connect(self.enable_save_button)
        self.end_date_input.dateChanged.connect(self.enable_save_button)
        self.description_input.textChanged.connect(self.enable_save_button)
        self.name_input.textChanged.connect(self.enable_save_button)

    def enable_save_button(self):
        name_valid = bool(self.name_input.text())
        start_date_valid = bool(self.start_date_input.date())
        end_date_valid = bool(self.end_date_input.date())

        if self.project:
            start_date_valid = start_date_valid and self.start_date_input.date() >= self.project.start_date

        if self.project:
            end_date_valid = end_date_valid and self.end_date_input.date() <= self.project.end_date

        if end_date_valid and start_date_valid:
            end_date_valid = self.end_date_input.date() >= self.start_date_input.date()

        self.create_button.setEnabled(
            name_valid
            and start_date_valid
            and end_date_valid
        )

    def save_task(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()

        session = database.Session()

        existing_task = session.query(Tasks).filter_by(project_id=self.project_id, name=name).first()
        if existing_task:
            QMessageBox.warning(self, "Предупреждение", "Задача с таким названием уже существует в проекте")
            session.close()
            return

        try:
            new_task = Tasks(
                project_id=self.project_id,
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
            )
            session.add(new_task)
            session.commit()
            session.close()

            QMessageBox.information(self, "Успешно", "Задача успешно создана")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {e}")
            session.rollback()
            session.close()


class EditTaskDialog(QDialog):
    def __init__(self, task_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование задачи")
        self.setFixedSize(390, 450)

        self.task_id = task_id
        self.original_name = None
        self.original_description = None
        self.original_start_date = None
        self.original_end_date = None
        self.is_valid = False

        session = database.Session()
        try:
            self.task = session.query(database.Tasks).filter_by(id=self.task_id).first()
            if not self.task:
                QMessageBox.warning(self, "Ошибка", "Задача не найдена")
                self.close()
                return

            self.project_start_date = self.task.project.start_date
            self.project_end_date = self.task.project.end_date

            self.project_label = QLabel("Проект:")
            self.project_input = QLineEdit()
            self.project_input.setReadOnly(True)
            self.project_input.setText(self.task.project.name)

            self.name_label = QLabel("Название:")
            self.name_input = QLineEdit()
            self.name_input.setMaxLength(255)
            self.name_input.setText(self.task.name)
            self.original_name = self.task.name

            self.start_date_label = QLabel("Дата начала:")
            self.start_date_input = QDateEdit()
            self.start_date_input.setDate(self.task.start_date)
            self.original_start_date = self.task.start_date

            self.end_date_label = QLabel("Дата окончания:")
            self.end_date_input = QDateEdit()
            self.end_date_input.setDate(self.task.end_date)
            self.original_end_date = self.task.end_date

            self.description_label = QLabel("Описание:")
            self.description_input = QTextEdit()
            self.description_input.setText(self.task.description)
            self.original_description = self.task.description

            self.save_button = QPushButton("Сохранить")
            self.save_button.clicked.connect(self.save_task)
            self.save_button.setEnabled(False)

            layout = QVBoxLayout()
            layout.addWidget(self.project_label)
            layout.addWidget(self.project_input)
            layout.addWidget(self.name_label)
            layout.addWidget(self.name_input)
            layout.addWidget(self.start_date_label)
            layout.addWidget(self.start_date_input)
            layout.addWidget(self.end_date_label)
            layout.addWidget(self.end_date_input)
            layout.addWidget(self.description_label)
            layout.addWidget(self.description_input)
            layout.addWidget(self.save_button)
            self.setLayout(layout)

            self.name_input.textChanged.connect(self.enable_save_button)
            self.start_date_input.dateChanged.connect(self.enable_save_button)
            self.end_date_input.dateChanged.connect(self.enable_save_button)
            self.description_input.textChanged.connect(self.enable_save_button)

        finally:
            session.close()

    def enable_save_button(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()

        start_date_valid = start_date >= self.project_start_date
        end_date_valid = end_date <= self.project_end_date

        if start_date_valid and end_date_valid:
            end_date_valid = end_date >= start_date

        changed = (
                name != self.original_name
                or description != self.original_description
                or start_date != self.original_start_date
                or end_date != self.original_end_date
        )

        self.save_button.setEnabled(
            changed
            and bool(name)
            and start_date_valid
            and end_date_valid
        )

    def save_task(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()

        session = database.Session()
        try:
            task = session.query(database.Tasks).filter_by(id=self.task_id).first()
            if not task:
                QMessageBox.warning(self, "Ошибка", "Задача не найдена")
                return

            existing_task = session.query(database.Tasks).filter_by(project_id=task.project_id, name=name).first()
            if existing_task and existing_task.id != self.task_id:
                QMessageBox.warning(self, "Предупреждение", "Задача с таким названием уже существует в проекте")
                return

            task.name = name
            task.description = description
            task.start_date = start_date
            task.end_date = end_date

            session.commit()
            QMessageBox.information(self, "Успешно", "Задача успешно обновлена")
            self.close()

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить задачу: {e}")
        finally:
            session.close()


class AddTimeEntryDialog(QDialog):
    def __init__(self, parent, employee_id, task_id):
        super().__init__(parent)
        self.setWindowTitle("Создание временной метки")
        self.setFixedSize(390, 340)
        self.employee_id = employee_id
        self.task_id = task_id

        session = database.Session()
        self.task = session.query(Tasks).filter_by(id=self.task_id).first()
        if self.task:
            self.task_start_date = self.task.start_date
            self.task_end_date = self.task.end_date
        session.close()

        self.task_label = QLabel("Задача:")
        self.task_input = QLineEdit()
        self.task_input.setReadOnly(True)
        self.task_input.setText(self.task.name if self.task else "Неизвестная задача")

        self.employee_label = QLabel("Сотрудник:")
        self.employee_combo = QComboBox()
        session = database.Session()
        employees = session.query(Employees).all()
        session.close()
        if employees:
            for employee in employees:
                self.employee_combo.addItem(f"{employee.last_name} {employee.first_name} {employee.middle_name}",
                                            employee.id)
        else:
            self.employee_combo.addItem("Пусто")
            self.employee_combo.setEnabled(False)
        self.employee_combo.currentTextChanged.connect(self.enable_save_button)

        self.start_date_label = QLabel("Дата начала:")
        self.start_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.dateChanged.connect(self.enable_save_button)

        self.start_time_label = QLabel("Время начала:")
        self.start_time_edit = QTimeEdit(QTime(12, 0, 0))
        self.start_time_edit.setDisplayFormat("HH:mm:ss")
        self.start_time_edit.timeChanged.connect(self.enable_save_button)

        self.end_date_label = QLabel("Дата окончания:")
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.dateChanged.connect(self.enable_save_button)

        self.end_time_label = QLabel("Время окончания:")
        self.end_time_edit = QTimeEdit(QTime(12, 0, 0))
        self.end_time_edit.setDisplayFormat("HH:mm:ss")
        self.end_time_edit.timeChanged.connect(self.enable_save_button)

        self.create_button = QPushButton("Сохранить")
        self.create_button.clicked.connect(self.save_time_entry)
        self.create_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.task_label)
        layout.addWidget(self.task_input)
        layout.addWidget(self.employee_label)
        layout.addWidget(self.employee_combo)
        layout.addWidget(self.start_date_label)
        layout.addWidget(self.start_date_edit)
        layout.addWidget(self.start_time_label)
        layout.addWidget(self.start_time_edit)
        layout.addWidget(self.end_date_label)
        layout.addWidget(self.end_date_edit)
        layout.addWidget(self.end_time_label)
        layout.addWidget(self.end_time_edit)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

        self.enable_save_button()

    def enable_save_button(self):
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()

        start_datetime = QDateTime(self.start_date_edit.date(), self.start_time_edit.time()).toPython()
        end_datetime = QDateTime(self.end_date_edit.date(), self.end_time_edit.time()).toPython()
        employee_valid = self.employee_combo.currentText() != "Пусто"

        valid_start = self.task_start_date <= start_date <= self.task_end_date
        valid_end = self.task_start_date <= end_date <= self.task_end_date
        time_difference = end_datetime - start_datetime

        employee_id = self.employee_combo.currentData()
        session = database.Session()
        employee = session.query(Employees).filter_by(id=employee_id).first()
        session.close()

        if employee:
            hire_date = employee.hire_date
            hire_datetime = datetime.datetime(hire_date.year, hire_date.month, hire_date.day, 0, 0, 0)
            valid_hire_date = hire_datetime <= start_datetime

            self.create_button.setEnabled(
                valid_start and valid_end and start_datetime <= end_datetime and time_difference.total_seconds() >= 1 and employee_valid and valid_hire_date
            )

        else:
            self.create_button.setEnabled(False)

    def save_time_entry(self):
        start_datetime = QDateTime(self.start_date_edit.date(), self.start_time_edit.time()).toPython()
        end_datetime = QDateTime(self.end_date_edit.date(), self.end_time_edit.time()).toPython()
        employee_id = self.employee_combo.currentData()

        session = database.Session()

        self.task = session.query(Tasks).filter_by(id=self.task_id).first()

        existing_entries = session.query(TimeEntries).filter_by(
            employee_id=employee_id
        ).all()

        for entry in existing_entries:
            existing_start = entry.timestamp_start
            existing_end = entry.timestamp_end
            conflicting_task = session.query(Tasks).filter_by(
                id=entry.task_id).first()
            project_name = conflicting_task.project.name if conflicting_task and conflicting_task.project else "Неизвестный проект"
            if (start_datetime <= existing_end and end_datetime >= existing_start) or \
                    (start_datetime >= existing_start and end_datetime <= existing_end):
                error_message = (
                    f"У выбранного сотрудника заданное время пересекается с существующими временными метками.\n"
                    f"Проект: {project_name}\n"
                    f"Задача: {conflicting_task.name if conflicting_task else 'Неизвестная задача'} "
                    f"({existing_start.strftime('%Y-%m-%d %H:%M:%S')} - {existing_end.strftime('%Y-%m-%d %H:%M:%S')})"
                )
                QMessageBox.warning(self, "Предупреждение", error_message)
                session.close()
                return

        try:
            new_time_entry = TimeEntries(
                employee_id=employee_id,
                task_id=self.task_id,
                timestamp_start=start_datetime,
                timestamp_end=end_datetime,
            )
            session.add(new_time_entry)
            session.commit()
            session.close()

            QMessageBox.information(self, "Успешно", "Временная метка успешно создана")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать временную метку: {e}")
            session.rollback()
            session.close()


class EditTimeEntryDialog(QDialog):
    def __init__(self, time_entry_id, parent):
        super().__init__(parent)
        self.setWindowTitle("Редактирование временной метки")
        self.setFixedSize(390, 340)
        self.time_entry_id = time_entry_id

        self.original_employee_id = None
        self.original_task_id = None
        self.original_start_datetime = None
        self.original_end_datetime = None

        session = database.Session()
        try:
            self.time_entry = session.query(database.TimeEntries).filter_by(id=self.time_entry_id).first()
            if not self.time_entry:
                QMessageBox.warning(self, "Ошибка", "Временная метка не найдена")
                self.close()
                return

            self.task = self.time_entry.task
            self.task_start_date = self.task.start_date
            self.task_end_date = self.task.end_date

            self.task_label = QLabel("Задача:")
            self.task_input = QLineEdit()
            self.task_input.setReadOnly(True)
            self.task_input.setText(self.task.name)

            self.employee_label = QLabel("Сотрудник:")
            self.employee_combo = QComboBox()
            employees = session.query(database.Employees).all()
            for employee in employees:
                self.employee_combo.addItem(f"{employee.last_name} {employee.first_name} {employee.middle_name}",
                                            employee.id)
            self.employee_combo.setCurrentText(
                f"{self.time_entry.employee.last_name} {self.time_entry.employee.first_name} {self.time_entry.employee.middle_name}")
            self.original_employee_id = self.time_entry.employee_id

            self.start_date_label = QLabel("Дата начала:")
            self.start_date_edit = QDateEdit(self.time_entry.timestamp_start.date())
            self.start_date_edit.setDisplayFormat("yyyy-MM-dd")

            self.start_time_label = QLabel("Время начала:")
            self.start_time_edit = QTimeEdit(self.time_entry.timestamp_start.time())
            self.start_time_edit.setDisplayFormat("HH:mm:ss")

            self.end_date_label = QLabel("Дата окончания:")
            self.end_date_edit = QDateEdit(self.time_entry.timestamp_end.date())
            self.end_date_edit.setDisplayFormat("yyyy-MM-dd")

            self.end_time_label = QLabel("Время окончания:")
            self.end_time_edit = QTimeEdit(self.time_entry.timestamp_end.time())
            self.end_time_edit.setDisplayFormat("HH:mm:ss")

            self.original_start_datetime = self.time_entry.timestamp_start
            self.original_end_datetime = self.time_entry.timestamp_end

            self.save_button = QPushButton("Сохранить")
            self.save_button.clicked.connect(self.save_time_entry)
            self.save_button.setEnabled(False)

            layout = QVBoxLayout()
            layout.addWidget(self.task_label)
            layout.addWidget(self.task_input)
            layout.addWidget(self.employee_label)
            layout.addWidget(self.employee_combo)
            layout.addWidget(self.start_date_label)
            layout.addWidget(self.start_date_edit)
            layout.addWidget(self.start_time_label)
            layout.addWidget(self.start_time_edit)
            layout.addWidget(self.end_date_label)
            layout.addWidget(self.end_date_edit)
            layout.addWidget(self.end_time_label)
            layout.addWidget(self.end_time_edit)
            layout.addWidget(self.save_button)
            self.setLayout(layout)

            self.employee_combo.currentTextChanged.connect(self.enable_save_button)
            self.start_date_edit.dateChanged.connect(self.enable_save_button)
            self.start_time_edit.timeChanged.connect(self.enable_save_button)
            self.end_date_edit.dateChanged.connect(self.enable_save_button)
            self.end_time_edit.timeChanged.connect(self.enable_save_button)
        finally:
            session.close()

    def enable_save_button(self):
        start_datetime = QDateTime(self.start_date_edit.date(), self.start_time_edit.time()).toPython()
        end_datetime = QDateTime(self.end_date_edit.date(), self.end_time_edit.time()).toPython()
        employee_id = self.employee_combo.currentData()

        time_difference = end_datetime - start_datetime

        task_start_datetime = QDateTime(self.task_start_date, QTime(0, 0)).toPython()
        task_end_datetime = QDateTime(self.task_end_date, QTime(23, 59, 59)).toPython()

        changed = (
            employee_id != self.original_employee_id
            or start_datetime != self.original_start_datetime
            or end_datetime != self.original_end_datetime
        )

        session = database.Session()
        employee = session.query(Employees).filter_by(id=employee_id).first()
        session.close()

        if employee:
            hire_date = employee.hire_date
            hire_datetime = datetime.datetime(hire_date.year, hire_date.month, hire_date.day, 0, 0, 0)
            valid_hire_date = hire_datetime <= start_datetime

            self.save_button.setEnabled(
                changed
                and start_datetime <= end_datetime
                and time_difference.total_seconds() >= 1
                and start_datetime >= task_start_datetime
                and end_datetime <= task_end_datetime
                and valid_hire_date
            )
        else:
            self.save_button.setEnabled(False)

    def save_time_entry(self):
        start_datetime = QDateTime(self.start_date_edit.date(), self.start_time_edit.time()).toPython()
        end_datetime = QDateTime(self.end_date_edit.date(), self.end_time_edit.time()).toPython()
        employee_id = self.employee_combo.currentData()

        task_start_datetime = QDateTime(self.task_start_date, QTime(0, 0)).toPython()
        task_end_datetime = QDateTime(self.task_end_date, QTime(23, 59, 59)).toPython()

        if start_datetime < task_start_datetime or end_datetime > task_end_datetime:
            QMessageBox.warning(self, "Ошибка", "Временная метка выходит за рамки дат задачи")
            return

        session = database.Session()
        try:
            time_entry = session.query(database.TimeEntries).filter_by(id=self.time_entry_id).first()
            if not time_entry:
                QMessageBox.warning(self, "Ошибка", "Временная метка не найдена")
                return

            existing_entries = session.query(database.TimeEntries).filter_by(
                employee_id=employee_id
            ).all()

            for entry in existing_entries:
                existing_start = entry.timestamp_start
                existing_end = entry.timestamp_end

                if entry.id != self.time_entry_id and (
                        (start_datetime <= existing_end and end_datetime >= existing_start) or
                        (start_datetime >= existing_start and end_datetime <= existing_end)
                ):
                    project_name = self.task.project.name if self.task and self.task.project else "Неизвестный проект"
                    error_message = (
                        f"У выбранного сотрудника заданное время пересекается с существующими временными метками.\n"
                        f"Проект: {project_name}\n"
                        f"Задача: {self.task.name if self.task else 'Неизвестная задача'} "
                        f"({existing_start.strftime('%Y-%m-%d %H:%M:%S')} - {existing_end.strftime('%Y-%m-%d %H:%M:%S')})"
                    )
                    QMessageBox.warning(self, "Предупреждение", error_message)
                    session.close()
                    return

            time_entry.employee_id = employee_id
            time_entry.timestamp_start = start_datetime
            time_entry.timestamp_end = end_datetime

            session.commit()
            QMessageBox.information(self, "Успешно", "Временная метка успешно обновлена")
            self.close()

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить временную метку: {e}")
        finally:
            session.close()