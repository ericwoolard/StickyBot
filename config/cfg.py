# System imports
from time import time
# Project imports
import file_manager

r = None
config_path = 'config/'  # Root of all configuration files
last_updated = 0
cached_returns = {}  # Used to, well, cache function returns. Not wildly


# Aliases of the file_manager functions to control the relative path
def read(relative_path):
    global config_path
    return file_manager.read(config_path + relative_path)


def readJson(relative_path):
    global config_path
    return file_manager.readJson(config_path + relative_path)


def save(relative_path, data):
    global config_path
    return file_manager.save(config_path + relative_path, data)


def saveJson(relative_path, data):
    global config_path
    return file_manager.saveJson(config_path + relative_path, data)


