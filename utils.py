# utils.py
import re
import os

def sanitize_filename(name):
    """
    Sanitize the filename to remove or replace invalid characters.
    """
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_template_dir():
    """
    Returns the absolute path to the 'Template' directory within the 'gui' folder.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, "gui", "Template")
    return template_dir