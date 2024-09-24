# logger.py
import logging
import os
from configparser import ConfigParser

# Load configuration
config = ConfigParser()
config.read('config.ini')

# Create logs directory if it doesn't exist
logs_dir = os.path.abspath(config['Paths']['logs_dir'])
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logging.basicConfig(
    filename=os.path.join(logs_dir, 'app.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)

def get_logger(name):
    return logging.getLogger(name)
