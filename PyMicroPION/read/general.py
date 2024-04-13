"""
Reading functions for the input file
"""
import configparser
import sys
from PyMicroPION.tools import setup_logger
import os
from PyMicroPION.tools import messages as msg


# Create a logger named "my_app_logger" that logs to "app.log" file
logger = setup_logger("Para", "pymicropion_activity.log")

class InI_Reader:

    def __init__(self, file):
        self.file_path = file

    def ini_reader(self):

        try:
            parser = configparser.ConfigParser()
            parser.read(self.file_path)
            logger.debug("The input file is an INI file.")

        except (configparser.MissingSectionHeaderError, configparser.ParsingError):
            logger.error("The input file is not an INI file.")
            logger.error("Set your input ini file properly")
            sys.exit(msg.ExitMsg) # Exit with a non-zero status code

        # Create a ConfigParser object
        config = configparser.ConfigParser()

        try:
            # Read the INI file
            config.read(self.file_path)
            logger.info(f"Reading input parameter file: {self.file_path}")

            # ****************************************************************************
            # SECTION: General
            # Access values from the sections General
            if config.has_section('General'):
                '''
                Read General parameters
                '''
                # KEY: Task
                if 'Task' not in config['General']:
                    logger.error("Task not specified.")
                    config['General']['Task'] = ""
                else:
                    Task = config.get('General', 'Task')
                    if Task.lower() not in msg.TaskList:  # for invalid key
                        logger.error(f"Invalid PyMicroPION Task Key")
                        config['General']['Task'] = ""
                    if not Task:  # for empty key
                        logger.error("No Task Error")
                        config['General']['Task'] = ""

                # KEY: Output Path
                if 'OutputDir' not in config['General']:
                    logger.error("Output directory path not specified.")
                    config['General']['OutputDir'] = ""
                else:
                    output_dir = config.get('General', 'OutputDir')
                    if not output_dir.endswith('/'):
                        config['General']['OutputDir'] = output_dir + '/'
                    if not output_dir:
                        logger.error("Empty output directory path key.")
                        config['General']['OutputDir'] = ""

                # KEY: Output File
                if 'OutputFile' not in config['General']:
                    logger.warn("Output file key not specified. Default output file assigned.")
                    outputfile = msg.package.lower() + "_output.txt"
                    config['General']['OutputFile'] = outputfile
                else:
                    outputfile = config.get('General', 'OutputFile')
                    if not outputfile:
                        logger.warn("Empty output filename key, default file assigned.")
                        outputfile = msg.package.lower() + "_output.txt"
                        config['General']['OutputFile'] = outputfile


            # If the General section is absent, proceed with the exit
            else:
                logger.error("No section General found")
                logger.error("Set your input file properly")
                sys.exit(msg.ExitMsg)

            # make dictionary and return
            return dict(config['General'])
            # ****************************************************************************


        # if error reading ini file, then exit
        except configparser.Error as e:
            logger.error(f"Error reading INI file: {e}")
            sys.exit(msg.ExitMsg)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            sys.exit(msg.ExitMsg)
