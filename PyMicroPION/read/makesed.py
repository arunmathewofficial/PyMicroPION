"""
Reading functions for the input file
"""
import configparser
import sys
from PyMicroPION.tools import setup_logger
import os
from PyMicroPION.tools import constants as const
from PyMicroPION.tools import messages as msg

# Create a logger named "my_app_logger" that logs to "app.log" file
logger = setup_logger("MakeSED-Param", "pymicropion_activity.log")



class InI_Reader:

    def __init__(self, file):
        self.file_path = file


    def ini_reader(self, General):
        '''

        :param General:
        :return:
        '''

        # Get output directory and file
        OutputDir = General['outputdir']
        OutputFile = General['outputdir'] + General['outputfilename']


        config = configparser.ConfigParser()
        config.read(self.file_path)

        if config.has_section('MakeSED'):
            '''
            Read SED Section
            '''

            MakeSEDDictionary = {}

            ModelError = 0
            # Get the SeD Model
            if 'Model' not in config['MakeSED']:  # if model key is not specified
                logger.error("SED Model Key Not Specified.")
                with open(OutputFile, 'a') as outfile:
                    outfile.write(msg.AtlasMetallicityNoKeyError)  # todo
                ModelError +=1
            else:
                Model = config.get('MakeSED', 'Model')
                if Model.lower() not in const.SEDModels:  # for invalid model
                    logger.error(f"Invalid SED Model Key")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasMetallicityInvalidKeyError) # todo
                    ModelError +=1
                if not Model:  # for empty model key
                    logger.error("Empty SED Model Key")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasMetallicityEmptyKeyError)
                    ModelError +=1
                else:
                    MakeSEDDictionary['Model'] = Model

            # if no model is specified, the leave Model parameter empty
            if ModelError != 0: Model = ''

            #############################################################################
            ############################## POWR MODEL ###################################
            PoWRErrorCount = 0
            if Model.lower() == 'powr':  # PoWR Model

                # Read MakeSED for PoWR and check for requirements and errors

                # **********************************************************************
                # KEY: POWR Metallicity
                if 'Metallicity' not in config['MakeSED']:  # if key is not specified
                    logger.error("Metallicity Key Not Specified.")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasMetallicityNoKeyError) #todo
                    PoWRErrorCount += 1
                else:
                    Metallicity = config.get('MakeSED', 'Metallicity')
                    if Metallicity.lower() not in const.PoWRMetallicity:  # for invalid key
                        logger.error(f"Invalid Metallicity Key for PoWR")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityInvalidKeyError) #todo
                        PoWRErrorCount += 1
                    if not Metallicity:  # for empty metallicity key
                        logger.error("Empty Metallicity Key")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityEmptyKeyError) # todo
                        PoWRErrorCount += 1
                    else:
                        MakeSEDDictionary['Metallicity'] = Metallicity
                # **********************************************************************
                # **********************************************************************
                # KEY: POWR Composition
                if 'Composition' not in config['MakeSED']:  # if key is not specified
                    logger.error("Composition Key Not Specified.")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasMetallicityNoKeyError) #todo
                    PoWRErrorCount += 1
                else:
                    Composition = config.get('MakeSED', 'Composition')
                    if Composition.lower() not in const.PoWRComposition:  # for invalid key
                        logger.error(f"Invalid Composition Key for PoWR")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityInvalidKeyError) #todo
                        PoWRErrorCount += 1
                    if not Composition:  # for empty metallicity key
                        logger.error("Empty Composition Key")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityEmptyKeyError) # todo
                        PoWRErrorCount += 1
                    else:
                        MakeSEDDictionary['Composition'] = Composition
                # **********************************************************************
                # **********************************************************************
                # KEY: Mdot
                if 'Mdot' not in config['MakeSED']:  # if key is not specified
                    logger.error("Mdot Key Not Specified.")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasMetallicityNoKeyError) #todo
                    PoWRErrorCount += 1
                else:
                    Mdot = config.get('MakeSED', 'Mdot')

                    if not Mdot:
                        logger.error("Empty Mdot Key.")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityEmptyKeyError)  # todo
                        PoWRErrorCount += 1
                    elif not (const.PoWRMdotMin <= float(Mdot) <= const.PoWRMdotMax):
                            logger.error(f"Invalid Range for Mdot Key.")
                            with open(OutputFile, 'a') as outfile:
                                outfile.write(msg.AtlasMetallicityInvalidKeyError)  # todo
                            PoWRErrorCount += 1
                    else: MakeSEDDictionary['Mdot'] = Mdot
                # **********************************************************************
                # **********************************************************************
                # KEY: atlas energy bin
                if 'EnergyBins' not in config['MakeSED']:
                    logger.error("Energy Bins Not Specified.")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasEnergyBinNoKeyError)
                    PoWRErrorCount += 1
                else:
                    EnergyBins = config['MakeSED']['EnergyBins']
                    if EnergyBins == '':
                        logger.error("Empty Energy-Bins Key.")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasEnergyBinEmptyKeyError)
                        PoWRErrorCount += 1
                    else:
                        EnergyBinArray = eval(EnergyBins)
                        # Check whether the energy bin array is correctly configured.
                        if len(EnergyBinArray) == 0:
                            logger.error("Empty Energy-Bins Key.")
                            with open(OutputFile, 'a') as outfile:
                                outfile.write(msg.AtlasEnergyBinEmptyKeyError)
                            PoWRErrorCount += 1
                        # Check if list
                        if not isinstance(EnergyBinArray, list):
                            logger.error("Invalid Energy-Bins Format.")
                            with open(OutputFile, 'a') as outfile:
                                outfile.write(msg.AtlasEnergyBinInvalidKeyError)
                            PoWRErrorCount += 1
                        else:
                            MakeSEDDictionary['EnergyBins'] = EnergyBinArray
                # **********************************************************************
                # **********************************************************************
                # Key: Plot
                if 'Plot' not in config['MakeSED']:
                    MakeSEDDictionary['Plot'] = False
                else:
                    Plot = config['MakeSED']['Plot']
                    if not Plot:
                        logger.warn(f"Empty Plot Key: Assigning Default Value")
                        MakeSEDDictionary['Plot'] = False
                    else:
                        string_to_bool = {'true': True, 'false': False}
                        boolean_value = string_to_bool.get(Plot.lower())
                        if boolean_value is not None:
                            MakeSEDDictionary['Plot'] = boolean_value
                        else:
                            logger.error(f"Plot value must be a Boolean")
                # **********************************************************************
                # **********************************************************************
                # Key: plot path
                if MakeSEDDictionary['Plot']:
                    if 'PlotPath' not in config['MakeSED']:
                        MakeSEDDictionary['PlotPath'] = OutputDir
                    else:
                        PlotPath = config['MakeSED']['PlotPath']
                        if not PlotPath:
                            logger.warn(f"Empty Plot Path Key: Assigning Default Path")
                            MakeSEDDictionary['PlotPath'] = OutputDir
                        else:
                            if not PlotPath.endswith('/'):
                                PlotPath = PlotPath + "/"
                            MakeSEDDictionary['PlotPath'] = PlotPath
                # **********************************************************************
                # **********************************************************************
                # Key: PIONFormat
                if 'PIONFormat' not in config['MakeSED']:
                    MakeSEDDictionary['PIONFormat'] = False
                else:
                    Plot = config['MakeSED']['PIONFormat']
                    if not Plot:
                        logger.warn(f"Empty PION Format Key: Assigning Default Value.")
                        MakeSEDDictionary['PIONFormat'] = False
                    else:
                        string_to_bool = {'true': True, 'false': False}
                        boolean_value = string_to_bool.get(Plot.lower())
                        if boolean_value is not None:
                            MakeSEDDictionary['PIONFormat'] = boolean_value
                        else:
                            logger.error(f"PIONFormat Value Must Be Boolean.")
                # **********************************************************************
                # **********************************************************************
                # Key:  PIONFormat
                if MakeSEDDictionary['PIONFormat']:
                    if 'PIONFormatPath' not in config['MakeSED']:
                        MakeSEDDictionary['PIONFormatPath'] = OutputDir
                    else:
                        PIONFormatPath = config['MakeSED']['PIONFormatPath']
                        if not PIONFormatPath:
                            logger.warn(f"Empty PION Format Path Key: Assigning Default Path")
                            MakeSEDDictionary['PIONFormatPath'] = OutputDir
                        else:
                            if not PIONFormatPath.endswith('/'):
                                PIONFormatPath = PIONFormatPath + "/"
                            MakeSEDDictionary['PIONFormatPath'] = PIONFormatPath
                # **********************************************************************


            ########################### END POWR MODEL ##################################
            #############################################################################



            #############################################################################
            ############################# ATLAS MODEL ###################################
            AtlasErrorCount = 0
            if Model.lower() == 'atlas':  # PoWR Model

                # Read MakeSED for Atlas and check for requirements and errors

                # **********************************************************************
                # KEY: POWR Metallicity
                if 'Metallicity' not in config['MakeSED']:  # if key is not specified
                    logger.error("Metallicity Key Not Specified.")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasMetallicityNoKeyError)  # todo
                    AtlasErrorCount += 1
                else:
                    Metallicity = config.get('MakeSED', 'Metallicity')
                    if Metallicity not in const.AtlasMetallicity:  # for invalid key
                        logger.error(f"Invalid Metallicity Key for PoWR")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityInvalidKeyError)  # todo
                        AtlasErrorCount += 1
                    if not Metallicity:  # for empty metallicity key
                        logger.error("Empty Metallicity Key")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityEmptyKeyError)  # todo
                        AtlasErrorCount += 1
                    else:
                        MakeSEDDictionary['Metallicity'] = Metallicity
                # **********************************************************************
                # **********************************************************************
                # KEY: Atlas Gravity
                if 'Gravity' not in config['MakeSED']:  # if key is not specified
                    logger.error("Gravity Key Not Specified.")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasMetallicityNoKeyError)  # todo
                    AtlasErrorCount += 1
                else:
                    Gravity = config.get('MakeSED', 'Gravity')
                    if Gravity not in const.AtlasGravity:  # for invalid key
                        logger.error(f"Invalid Gravity Key for PoWR")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityInvalidKeyError)  # todo
                        AtlasErrorCount += 1
                    if not Gravity:
                        logger.error("Empty Gravity Key")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasMetallicityEmptyKeyError)  # todo
                        AtlasErrorCount += 1
                    else:
                        MakeSEDDictionary['Gravity'] = Gravity
                # **********************************************************************
                # **********************************************************************
                # KEY: atlas energy bin
                if 'EnergyBins' not in config['MakeSED']:
                    logger.error("Energy Bins Not Specified.")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasEnergyBinNoKeyError)
                    AtlasErrorCount += 1
                else:
                    EnergyBins = config['MakeSED']['EnergyBins']
                    if EnergyBins == '':
                        logger.error("Empty Energy-Bins Key.")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasEnergyBinEmptyKeyError)
                        AtlasErrorCount += 1
                    else:
                        EnergyBinArray = eval(EnergyBins)
                        # Check whether the energy bin array is correctly configured.
                        if len(EnergyBinArray) == 0:
                            logger.error("Empty Energy-Bins Key.")
                            with open(OutputFile, 'a') as outfile:
                                outfile.write(msg.AtlasEnergyBinEmptyKeyError)
                            AtlasErrorCount += 1
                        # Check if list
                        if not isinstance(EnergyBinArray, list):
                            logger.error("Invalid Energy-Bins Format.")
                            with open(OutputFile, 'a') as outfile:
                                outfile.write(msg.AtlasEnergyBinInvalidKeyError)
                            AtlasErrorCount += 1
                        else:
                            MakeSEDDictionary['EnergyBins'] = EnergyBinArray
                # **********************************************************************
                # **********************************************************************
                # Key: Plot
                if 'Plot' not in config['MakeSED']:
                    MakeSEDDictionary['Plot'] = False
                else:
                    Plot = config['MakeSED']['Plot']
                    if not Plot:
                        logger.warn(f"Empty Plot Key: Assigning Default Value")
                        MakeSEDDictionary['Plot'] = False
                    else:
                        string_to_bool = {'true': True, 'false': False}
                        boolean_value = string_to_bool.get(Plot.lower())
                        if boolean_value is not None:
                            MakeSEDDictionary['Plot'] = boolean_value
                        else:
                            logger.error(f"Plot value must be a Boolean")
                            MakeSEDDictionary['Plot'] = False
                # **********************************************************************
                # **********************************************************************
                # Key: plot path
                if MakeSEDDictionary['Plot']:
                    if 'PlotPath' not in config['MakeSED']:
                        MakeSEDDictionary['PlotPath'] = OutputDir
                    else:
                        PlotPath = config['MakeSED']['PlotPath']
                        if not PlotPath:
                            logger.warn(f"Empty Plot Path Key: Assigning Default Path")
                            MakeSEDDictionary['PlotPath'] = OutputDir
                        else:
                            if not PlotPath.endswith('/'):
                                PlotPath = PlotPath + "/"
                            MakeSEDDictionary['PlotPath'] = PlotPath
                # **********************************************************************
                # **********************************************************************
                # Key: PIONFormat
                if 'PIONFormat' not in config['MakeSED']:
                    MakeSEDDictionary['PIONFormat'] = False
                else:
                    Plot = config['MakeSED']['PIONFormat']
                    if not Plot:
                        logger.warn(f"Empty PION Format Key: Assigning Default Value.")
                        MakeSEDDictionary['PIONFormat'] = False
                    else:
                        string_to_bool = {'true': True, 'false': False}
                        boolean_value = string_to_bool.get(Plot.lower())
                        if boolean_value is not None:
                            MakeSEDDictionary['PIONFormat'] = boolean_value
                        else:
                            logger.error(f"PION Format Value Must Be Boolean.")
                            MakeSEDDictionary['PIONFormat'] = False
                # **********************************************************************
                # **********************************************************************
                # Key:  PIONFormat
                if MakeSEDDictionary['PIONFormat']:
                    if 'PIONFormatPath' not in config['MakeSED']:
                        MakeSEDDictionary['PIONFormatPath'] = OutputDir
                    else:
                        PIONFormatPath = config['MakeSED']['PIONFormatPath']
                        if not PIONFormatPath:
                            logger.warn(f"Empty PION Format Path Key: Assigning Default Path")
                            MakeSEDDictionary['PIONFormatPath'] = OutputDir
                        else:
                            if not PIONFormatPath.endswith('/'):
                                PIONFormatPath = PIONFormatPath + "/"
                            MakeSEDDictionary['PIONFormatPath'] = PIONFormatPath
                # **********************************************************************


            ########################### END ATLAS MODEL #################################
            #############################################################################



            #############################################################################
            ############################# BLACK BODY ####################################
            BBErrorCount = 0
            if Model.lower() == 'blackbody':  # PoWR Model

                # Read MakeSED for blaCK body and check for requirements and errors
                # **********************************************************************
                # KEY: atlas energy bin
                if 'EnergyBins' not in config['MakeSED']:
                    logger.error("Energy Bins Not Specified.")
                    with open(OutputFile, 'a') as outfile:
                        outfile.write(msg.AtlasEnergyBinNoKeyError)
                    BBErrorCount += 1
                else:
                    EnergyBins = config['MakeSED']['EnergyBins']
                    if EnergyBins == '':
                        logger.error("Empty Energy-Bins Key.")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasEnergyBinEmptyKeyError)
                        BBErrorCount += 1
                    else:
                        EnergyBinArray = eval(EnergyBins)
                        # Check whether the energy bin array is correctly configured.
                        if len(EnergyBinArray) == 0:
                            logger.error("Empty Energy-Bins Key.")
                            with open(OutputFile, 'a') as outfile:
                                outfile.write(msg.AtlasEnergyBinEmptyKeyError)
                            BBErrorCount += 1
                        # Check if list
                        if not isinstance(EnergyBinArray, list):
                            logger.error("Invalid Energy-Bins Format.")
                            with open(OutputFile, 'a') as outfile:
                                outfile.write(msg.AtlasEnergyBinInvalidKeyError)
                            BBErrorCount += 1
                        else:
                            MakeSEDDictionary['EnergyBins'] = EnergyBinArray
                # **********************************************************************
                # **********************************************************************
                # Key: Q_H
                if 'Q_H' not in config['MakeSED']:
                    MakeSEDDictionary['Q_H'] = False
                else:
                    QH = config['MakeSED']['Q_H']
                    if not QH:
                        logger.warn(f"Empty Q_H Key: Assigning None")
                        MakeSEDDictionary['Q_H'] = False
                    else:
                        string_to_bool = {'true': True, 'false': False}
                        boolean_value = string_to_bool.get(QH.lower())
                        if boolean_value is not None:
                            MakeSEDDictionary['Q_H'] = boolean_value
                        else:
                            logger.warn(f"Q_H, Invalid Species, Assigning None")
                            MakeSEDDictionary['Q_H'] = False
                # **********************************************************************
                # **********************************************************************
                # Key: Rstar
                if MakeSEDDictionary['Q_H']:
                    if 'Rstar' not in config['MakeSED']:
                        logger.error(f"No RStar Key Found.")
                        with open(OutputFile, 'a') as outfile:
                            outfile.write(msg.AtlasEnergyBinInvalidKeyError)
                        BBErrorCount += 1
                    else:
                        Rstar = config['MakeSED']['Rstar']
                        if Rstar == '':
                            logger.error("Empty Rstar Key.")
                            with open(OutputFile, 'a') as outfile:
                                outfile.write(msg.AtlasEnergyBinEmptyKeyError)
                            BBErrorCount += 1
                        try:
                            Rstar = float(Rstar)
                        except ValueError:
                            if not isinstance(Rstar, (float, int)):
                                logger.error("Invalid Rstar Key.")
                                with open(OutputFile, 'a') as outfile:
                                    outfile.write(msg.AtlasEnergyBinEmptyKeyError)
                                BBErrorCount += 1
                        else:
                            MakeSEDDictionary['Rstar'] = Rstar
                # **********************************************************************
                # **********************************************************************
                # Key: Plot
                if 'Plot' not in config['MakeSED']:
                    MakeSEDDictionary['Plot'] = False
                else:
                    Plot = config['MakeSED']['Plot']
                    if not Plot:
                        logger.warn(f"Empty Plot Key: Assigning Default Value")
                        MakeSEDDictionary['Plot'] = False
                    else:
                        string_to_bool = {'true': True, 'false': False}
                        boolean_value = string_to_bool.get(Plot.lower())
                        if boolean_value is not None:
                            MakeSEDDictionary['Plot'] = boolean_value
                        else:
                            logger.error(f"Plot value must be a Boolean")
                            MakeSEDDictionary['Plot'] = False
                # **********************************************************************
                # **********************************************************************
                # Key: plot path
                if MakeSEDDictionary['Plot']:
                    if 'PlotPath' not in config['MakeSED']:
                        MakeSEDDictionary['PlotPath'] = OutputDir
                    else:
                        PlotPath = config['MakeSED']['PlotPath']
                        if not PlotPath:
                            logger.warn(f"Empty Plot Path Key: Assigning Default Path")
                            MakeSEDDictionary['PlotPath'] = OutputDir
                        else:
                            if not PlotPath.endswith('/'):
                                PlotPath = PlotPath + "/"
                                if os.path.exists(PlotPath):
                                    pass
                                else:
                                    logger.error(f"Specified plot directory, {PlotPath} does not exist")
                                    BBErrorCount += 1
                            MakeSEDDictionary['PlotPath'] = PlotPath
                # **********************************************************************
                # **********************************************************************
                # Key: PIONFormat
                if 'PIONFormat' not in config['MakeSED']:
                    MakeSEDDictionary['PIONFormat'] = False
                else:
                    Plot = config['MakeSED']['PIONFormat']
                    if not Plot:
                        logger.warn(f"Empty PION Format Key: Assigning Default Value.")
                        MakeSEDDictionary['PIONFormat'] = False
                    else:
                        string_to_bool = {'true': True, 'false': False}
                        boolean_value = string_to_bool.get(Plot.lower())
                        if boolean_value is not None:
                            MakeSEDDictionary['PIONFormat'] = boolean_value
                        else:
                            logger.error(f"PION Format Value Must Be Boolean.")
                            MakeSEDDictionary['PIONFormat'] = False
                # **********************************************************************
                # **********************************************************************
                # Key:  PIONFormat
                if MakeSEDDictionary['PIONFormat']:
                    if 'PIONFormatPath' not in config['MakeSED']:
                        MakeSEDDictionary['PIONFormatPath'] = OutputDir
                    else:
                        PIONFormatPath = config['MakeSED']['PIONFormatPath']
                        if not PIONFormatPath:
                            logger.warn(f"Empty PION Format Path Key: Assigning Default Path")
                            MakeSEDDictionary['PIONFormatPath'] = OutputDir
                        else:
                            if not PIONFormatPath.endswith('/'):
                                PIONFormatPath = PIONFormatPath + "/"
                            MakeSEDDictionary['PIONFormatPath'] = PIONFormatPath
                # **********************************************************************


            ########################### END BLACK BODY ##################################
            #############################################################################


            # if No model is specified
            if ModelError != 0:
                MakeSEDDictionary = dict()

            # If any error in PoWR Section
            if PoWRErrorCount != 0:
                logger.error(f"PoWR: Input Requirements Incomplete, Returning Empty Dictionary")
                MakeSEDDictionary = dict()

            # If any error in Atlas Section
            if AtlasErrorCount != 0:
                logger.error(f"ATLAS: Input Requirements Incomplete, Returning Empty Dictionary")
                MakeSEDDictionary = dict()

            # If any error in Atlas Section
            if BBErrorCount != 0:
                logger.error(f"Blackbody: Input Requirements Incomplete, Returning Empty Dictionary")
                MakeSEDDictionary = dict()



            return MakeSEDDictionary

