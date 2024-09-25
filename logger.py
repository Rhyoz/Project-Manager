# logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser

# Load configuration
config = ConfigParser()
config.read('config.ini')

# Create logs directory if it doesn't exist
logs_dir = os.path.abspath(config['Paths']['logs_dir'])
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(
            os.path.join(logs_dir, 'app.log'),
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=5
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger