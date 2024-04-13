"""
Writing results to the output file
"""
import configparser
import sys
from PyMicroPION.tools import setup_logger
import os
from PyMicroPION.tools import messages as msg


# Create a logger named "my_app_logger" that logs to "app.log" file
logger = setup_logger("Write", "pymicropion_activity.log")

class GeneralWriter:

    def __init__(self, file):
        self.file_path = file
        with open(self.file_path, 'w') as self.outfile:
            self.outfile.write(msg.dashes + "\n")
            self.outfile.write(msg.package + "\n")
            home_page = next((line for line in msg.metadata.splitlines() if line.startswith('Home-page:')), None)
            if home_page:
                # Extract URL from the metadata line
                url = home_page.split(':', 1)[1].strip()
            self.outfile.write(url + "\n")
            self.outfile.write(msg.dashes + "\n")


    def renamegenWriter(self): # todo: rename this
        pass