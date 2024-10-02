# File: utils.py
import os
import sys
import subprocess
from configparser import ConfigParser

# Load configuration
config = ConfigParser()
config.read('config.ini')

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (" ", "_", "-")).rstrip()

def get_template_dir():
    return os.path.abspath(config['Paths']['template_dir'])

def get_project_dir():
    return os.path.abspath(config['Paths']['project_dir'])

def get_project_folder_name(project):
    parts = []
    if project.main_contractor and project.main_contractor.lower() != "none":
        parts.append(project.main_contractor)
    if project.name:
        parts.append(project.name)
    if project.number:
        parts.append(str(project.number))
    folder_name = " - ".join(parts) if parts else "Unnamed_Project"
    return sanitize_filename(folder_name)

def get_docx_temp_dir():
    return os.path.abspath(config['Paths']['docx_temp_dir'])

def get_logs_dir():
    return os.path.abspath(config['Paths']['logs_dir'])

def get_main_contractors_file():
    project_dir = get_project_dir()
    return os.path.join(project_dir, "main_contractors.txt")

def check_template_files():
    template_dir = get_template_dir()
    required_files = ["Innregulering.docx", "Sjekkliste.docx"]
    missing_files = [file for file in required_files if not os.path.exists(os.path.join(template_dir, file))]
    if missing_files:
        return False, f"Missing template files: {', '.join(missing_files)}"
    return True, "All template files are present."

def open_docx_file(filepath):
    try:
        if sys.platform.startswith('darwin'):
            subprocess.call(['open', filepath])
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(['xdg-open', filepath])
        return True, "Opened successfully."
    except Exception as e:
        return False, f"Failed to open file: {str(e)}"

def load_main_contractors():
    """
    Loads the list of main contractors from a text file.
    """
    contractors_file = get_main_contractors_file()
    if not os.path.exists(contractors_file):
        # If the file doesn't exist, create it with default contractors
        with open(contractors_file, 'w') as f:
            f.write("Lindal\nLohne\n")
    with open(contractors_file, 'r') as f:
        contractors = [line.strip() for line in f if line.strip()]
    return contractors

def add_main_contractor(contractor_name):
    """
    Adds a new main contractor to the storage file.
    """
    contractors_file = get_main_contractors_file()
    contractors = load_main_contractors()
    if contractor_name not in contractors:
        with open(contractors_file, 'a') as f:
            f.write(f"{contractor_name}\n")
