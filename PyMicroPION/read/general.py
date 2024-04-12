"""
Reading functions for the input file
"""
import configparser
import sys
from PyMicroPION.tools import setup_logger
import os
from PyMicroPION.tools import messages as msg

# Create a logger named "my_app_logger" that logs to "app.log" file
logger = setup_logger("General-Param", "pymicropion_activity.log")



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
            sys.exit("PyMicroPION Exiting ...") # Exit with a non-zero status code

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

                # KEY: Output Path
                if 'OutputDir' not in config['General']:
                    logger.error("Output path key not specified.")
                else:
                    output_dir = config.get('General', 'OutputDir')
                    if os.path.exists(output_dir) and os.path.isdir(output_dir):
                        if not output_dir.endswith('/'):
                            default_output_dir = output_dir + "/"
                            config.set('General', 'OutputDir', default_output_dir)
                    else:
                        logger.error(f"Output directory '{output_dir}' does not exist.")
                        sys.exit("PyMicroPION Exiting ...")  # Exit with a non-zero status code
                    if not output_dir:
                        logger.warn("Empty output path key, default path assigned.")
                        output_dir = os.path.dirname(self.file_path)
                        config['General']['Output_path'] = output_dir


                # KEY: Output File
                if 'OutputFileName' not in config['General']:
                    logger.error("Output filename key not specified.")
                else:
                    outputfilename = config.get('General', 'OutputFileName')
                    if not outputfilename:
                        logger.warn("Empty output filename key, default filename assigned.")
                        outputfilename = "pymicropion_output.txt"
                        config['General']['OutputFileName'] = outputfilename


            # If the General section is absent, proceed with the exit
            else:
                logger.error("No section General found")
                logger.error("Set your input file properly")
                sys.exit("PyMicroPION Exiting ...")  # Exit with a non-zero status code

            # make dictionary and return
            return dict(config['General'])
            # ****************************************************************************


        # if error reading ini file, then exit
        except configparser.Error as e:
            logger.error(f"Error reading INI file: {e}")
            sys.exit("PyMicroPION Exiting ...")  # Exit with a non-zero status code
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            sys.exit("PyMicroPION Exiting ...")  # Exit with a non-zero status code
