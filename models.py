from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Employees(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    middle_name = Column(String(255))
    birth_date = Column(Date, nullable=False)
    gender = Column(Boolean, nullable=False)
    hire_date = Column(Date, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    position_id = Column(Integer, ForeignKey('positions.id'), nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(Text, unique=True)

    department = relationship("Departments")
    position = relationship("Positions")
    projects = relationship("Projects", backref="manager")
    time_entries = relationship("TimeEntries", backref="employee")


class Clients(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(Text, nullable=False)

    projects = relationship("Projects", backref="client")


class Projects(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    tasks = relationship("Tasks", backref="project")


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    time_entries = relationship("TimeEntries", backref="task")


class TimeEntries(Base):
    __tablename__ = 'time_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    timestamp_start = Column(TIMESTAMP, nullable=False)
    timestamp_end = Column(TIMESTAMP, nullable=False)


class Departments(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)


class Positions(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)