# File: controllers/project_controller.py

from project import Project
from database import ProjectModel, UnitModel
from sqlalchemy.orm import Session
from typing import Optional, List
from logger import get_logger

logger = get_logger(__name__)

class ProjectController:
    def __init__(self, db):
        self.db = db  # The Database instance containing the session

    def load_projects(self, status: Optional[str] = None) -> List[Project]:
        try:
            return self.db.load_projects(status=status)
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")
            return []

    def add_project(self, project: Project) -> int:
        try:
            project_id = self.db.add_project(project)
            logger.info(f"Project '{project.name}' added with ID {project_id}")
            return project_id
        except Exception as e:
            logger.error(f"Failed to add project '{project.name}': {e}")
            raise

    def update_project(self, project: Project):
        try:
            self.db.update_project(project)
            logger.info(f"Project '{project.name}' updated.")
        except Exception as e:
            logger.error(f"Failed to update project '{project.name}': {e}")
            raise

    def delete_project(self, project_id: int):
        try:
            self.db.delete_project(project_id)
            logger.info(f"Project with ID {project_id} deleted.")
        except Exception as e:
            logger.error(f"Failed to delete project with ID {project_id}: {e}")
            raise

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        try:
            return self.db.get_project_by_id(project_id)
        except Exception as e:
            logger.error(f"Failed to retrieve project with ID {project_id}: {e}")
            return None

    def toggle_unit_status(self, project_id: int, unit_id: int, is_done: bool):
        try:
            self.db.toggle_unit_status(project_id, unit_id, is_done)
            logger.info(f"Unit with ID {unit_id} in project {project_id} status set to {'done' if is_done else 'not done'}.")
        except Exception as e:
            logger.error(f"Failed to toggle unit status for unit {unit_id} in project {project_id}: {e}")
            raise
