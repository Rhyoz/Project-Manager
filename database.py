# database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from project import Project
from logger import get_logger
import os
from configparser import ConfigParser

logger = get_logger(__name__)

# Load configuration
config = ConfigParser()
config.read('config.ini')

# Retrieve paths from config
project_dir = os.path.abspath(config['Paths'].get('project_dir', 'Boligventilasjon_Prosjekter'))
database_file = config['Paths'].get('database_file', 'projects.db')

# Ensure project_dir exists
if not os.path.exists(project_dir):
    try:
        os.makedirs(project_dir)
        logger.info(f"Created project directory at {project_dir}")
    except Exception as e:
        logger.error(f"Failed to create project directory at {project_dir}: {e}")
        raise

# Construct full database path
db_path = os.path.join(project_dir, database_file)

Base = declarative_base()

class ProjectModel(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    number = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    status = Column(String, nullable=False)
    is_residential_complex = Column(Boolean, default=False)
    number_of_units = Column(Integer, default=0)
    residential_details = Column(String, default="")
    worker = Column(String, nullable=False)
    extra = Column(String, default="")

class Database:
    def __init__(self):
        try:
            self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logger.info(f"Database initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database at {db_path}: {e}")
            raise

    def add_project(self, project: Project):
        try:
            project_model = ProjectModel(
                name=project.name,
                number=project.number,
                start_date=project.start_date,
                end_date=project.end_date,
                status=project.status,
                is_residential_complex=project.is_residential_complex,
                number_of_units=project.number_of_units,
                residential_details=project.residential_details,
                worker=project.worker,
                extra=project.extra
            )
            self.session.add(project_model)
            self.session.commit()
            logger.info(f"Added project: {project.name} ({project.number})")
            return project_model.id
        except Exception as e:
            logger.error(f"Failed to add project: {e}")
            self.session.rollback()
            raise

    def update_project(self, project: Project):
        try:
            project_model = self.session.query(ProjectModel).filter_by(id=project.id).first()
            if project_model:
                project_model.name = project.name
                project_model.number = project.number
                project_model.start_date = project.start_date
                project_model.end_date = project.end_date
                project_model.status = project.status
                project_model.is_residential_complex = project.is_residential_complex
                project_model.number_of_units = project.number_of_units
                project_model.residential_details = project.residential_details
                project_model.worker = project.worker
                project_model.extra = project.extra
                self.session.commit()
                logger.info(f"Updated project ID {project.id}: {project.name} ({project.number})")
        except Exception as e:
            logger.error(f"Failed to update project ID {project.id}: {e}")
            self.session.rollback()
            raise

    def delete_project(self, project_id: int):
        try:
            project_model = self.session.query(ProjectModel).filter_by(id=project_id).first()
            if project_model:
                self.session.delete(project_model)
                self.session.commit()
                logger.info(f"Deleted project ID {project_id}")
        except Exception as e:
            logger.error(f"Failed to delete project ID {project_id}: {e}")
            self.session.rollback()
            raise

    def load_projects(self, status=None):
        try:
            query = self.session.query(ProjectModel)
            if status:
                query = query.filter_by(status=status)
            projects = query.all()
            logger.info(f"Loaded projects with status='{status}'" if status else "Loaded all projects")
            return [Project(
                id=p.id,
                name=p.name,
                number=p.number,
                start_date=p.start_date,
                end_date=p.end_date,
                status=p.status,
                is_residential_complex=p.is_residential_complex,
                number_of_units=p.number_of_units,
                residential_details=p.residential_details,
                worker=p.worker,
                extra=p.extra
            ) for p in projects]
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")
            raise

    def get_project_by_id(self, project_id: int):
        try:
            p = self.session.query(ProjectModel).filter_by(id=project_id).first()
            if p:
                logger.info(f"Retrieved project ID {project_id}")
                return Project(
                    id=p.id,
                    name=p.name,
                    number=p.number,
                    start_date=p.start_date,
                    end_date=p.end_date,
                    status=p.status,
                    is_residential_complex=p.is_residential_complex,
                    number_of_units=p.number_of_units,
                    residential_details=p.residential_details,
                    worker=p.worker,
                    extra=p.extra
                )
            logger.warning(f"Project ID {project_id} not found.")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve project ID {project_id}: {e}")
            raise

    def close(self):
        self.session.close()
        logger.info("Database session closed.")
