import os

command = None

# Required and wanted processing of final files
def file_manager(path):
    if os.path.exists(str(path)):
        os.remove(str(path))
