# database.py
import sqlite3
from project import Project
import os

DB_NAME = "projects.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                number TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT,
                is_residential_complex INTEGER,
                number_of_units INTEGER,
                residential_details TEXT,
                worker TEXT  -- New column added
            )
        """)
        self.conn.commit()

    def add_project(self, project: Project):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO projects (name, number, start_date, end_date, status, is_residential_complex, number_of_units, residential_details, worker)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project.name,
            project.number,
            project.start_date,  # Removed .isoformat()
            project.end_date,    # Removed .isoformat() if exists
            project.status,
            int(project.is_residential_complex),
            project.number_of_units,
            project.residential_details,
            project.worker  # New field added
        ))
        self.conn.commit()
        return cursor.lastrowid

    def update_project(self, project: Project):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE projects
            SET name = ?, number = ?, start_date = ?, end_date = ?, status = ?, is_residential_complex = ?, number_of_units = ?, residential_details = ?, worker = ?
            WHERE id = ?
        """, (
            project.name,
            project.number,
            project.start_date,  # Removed .isoformat()
            project.end_date,    # Removed .isoformat() if exists
            project.status,
            int(project.is_residential_complex),
            project.number_of_units,
            project.residential_details,
            project.worker,  # New field added
            project.id
        ))
        self.conn.commit()

    def delete_project(self, project_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

    def load_projects(self, status=None):
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM projects WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM projects")
        rows = cursor.fetchall()
        projects = []
        for row in rows:
            projects.append(Project(
                id=row[0],
                name=row[1],
                number=row[2],
                start_date=row[3],
                end_date=row[4],
                status=row[5],
                is_residential_complex=bool(row[6]),
                number_of_units=row[7],
                residential_details=row[8],
                worker=row[9]  # New field added
            ))
        return projects

    def get_project_by_id(self, project_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        if row:
            return Project(
                id=row[0],
                name=row[1],
                number=row[2],
                start_date=row[3],
                end_date=row[4],
                status=row[5],
                is_residential_complex=bool(row[6]),
                number_of_units=row[7],
                residential_details=row[8],
                worker=row[9]  # New field added
            )
        return None

    def close(self):
        self.conn.close()
