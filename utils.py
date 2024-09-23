# utils.py
import re

def sanitize_filename(name):
    """
    Sanitize the filename to remove or replace invalid characters.
    """
    return re.sub(r'[\\/*?:"<>|]', "_", name)
