# utils.py
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

def get_docx_temp_dir():
    return os.path.abspath(config['Paths']['docx_temp_dir'])

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
