# PyMicroPION/__main__.py

"""
PyMicro Main File.
"""

import sys
import time
import argparse
import pandas as pd
from PyMicroPION.read import General
from PyMicroPION.read import MakeSED
from PyMicroPION.sed import PotsdamWolfRayet
from PyMicroPION.sed import CastelliKuruczAtlas
from PyMicroPION.sed import BlackBody
from PyMicroPION.tools import setup_logger
from PyMicroPION.tools import messages as msg
from PyMicroPION.write import GeneralWriter
from PyMicroPION.write import MakeSEDWriter

logger = setup_logger("Main", "pymicropion_activity.log")

def main():
    # getting input file
    # global MakeSED_StartTime
    PyMicroPION_StartTime = time.time()
    # package version
    logger.info(f'--------- Running' + msg.package + ' ---------')
    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument("input_file", help="path for your ini input parameter file")

    args = parser.parse_args()
    # Get the ini input file path
    ini_file = args.input_file



    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # General
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Read the general input parameters
    GeneralParameters = General(ini_file)
    GeneralData = GeneralParameters.ini_reader()

    if GeneralData["task"] == "" or GeneralData["outputdir"] == "":
        sys.exit(msg.ExitMsg)
    else:
        OutputFile = GeneralData['outputdir'] + GeneralData['outputfile']
        Task = GeneralData['task']
        GeneralOut = GeneralWriter(OutputFile)
        #GeneralOut.GeneralWriter()

    # Runtime
    RuntimeDict = {}
    # Task Counter
    TaskCounter = 0
    # **********************************************************************************************




    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Task: Make Spectral Energy Distributions
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if Task.lower() == "makesed":
        MakeSED_StartTime = time.time()
        # Read MakeSED parameter
        MakeSEDParameters = MakeSED(ini_file)
        MakeSEDData = MakeSEDParameters.ini_reader(GeneralData)

        # Atlas Model %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if MakeSEDData['Model'].lower() == 'atlas':
            logger.info(msg.AtlasInputINFO(MakeSEDData))
            AtlasObject = CastelliKuruczAtlas(MakeSEDData)
            BundledModels = AtlasObject.BundleUpModels()
            BundledModelsUnits_DF = pd.DataFrame([msg.AtlasModelsUnits])
            BundledModelsPlusUnits = pd.concat([BundledModelsUnits_DF, BundledModels], axis=0, ignore_index=True)
            SED = AtlasObject.SpectralEnergyDistributions()
            EBins_LamBins = SED['EBins_LamBins']
            BinnedFracSED = SED['BinnedFracSED']
            AtlasWriterObject = MakeSEDWriter(OutputFile)
            AtlasWriterObject.MakeSED_Atlas_Writer(MakeSEDData, BundledModelsPlusUnits, EBins_LamBins, BinnedFracSED)
            # Plot data into plot directory
            if MakeSEDData['Plot']: AtlasObject.PlotAtlas(MakeSEDData['PlotPath'])
            # PION Format
            if MakeSEDData['PIONFormat']: PIONFormat = AtlasObject.PionFormatAtlas(MakeSEDData['PIONFormatPath'])
            # Always add the Task Counter whenever you add a task.
            TaskCounter +=1
        #******************************************************************************************

        # PoWR Model %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if MakeSEDData['Model'].lower() == 'powr':
            logger.info(f'Initiating Binning Spectral Energy Distributions for PoWR')
            PoWRObject = PotsdamWolfRayet(MakeSEDData)
            BundledModels = PoWRObject.BundleUpGrids()
            BundledModelsUnits_DF = pd.DataFrame([msg.PoWRModelsUnits])
            BundledModelsPlusUnits = pd.concat([BundledModelsUnits_DF, BundledModels], axis=0, ignore_index=True)
            SED = PoWRObject.SpectralEnergyDistributions()
            EBins_LamBins = SED['EBins_LamBins']
            BinnedFracSED = SED['BinnedFracSED']
            # Plot data into plot directory
            if MakeSEDData['Plot']: PoWRObject.PlotPoWR(MakeSEDData['PlotPath'])
            # PION Format
            if MakeSEDData['PIONFormat']:PIONFormat = PoWRObject.PionFormatPoWR(MakeSEDData['PIONFormatPath'])
        #******************************************************************************************


        # BLACK BODY %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if MakeSEDData['Model'].lower() == 'blackbody':
            logger.info(f'Initiating Binning Spectral Energy Distributions for BlackBody')
            BlackBodyObject = BlackBody(MakeSEDData)
            SED = BlackBodyObject.SpectralEnergyDistributions()
            EBins_LamBins = SED['EBins_LamBins']
            BinnedFracSED = SED['BinnedFracSED']
            if MakeSEDData['Q_H']:
                QHSet = BlackBodyObject.CalculateQH(MakeSEDData['Rstar'])['QHSet']
            # Plot data into plot directory
            if MakeSEDData['Plot']:
                # Get the plot path
                PlotPath = MakeSEDData['PlotPath']
                FluxLambda = BlackBodyObject.PlotBB(PlotPath)['FluxLambda']
            # PION Format
            if MakeSEDData['PIONFormat']:
                # Get the plot path
                PIONFormatPath = MakeSEDData['PIONFormatPath']
                PIONFormat = BlackBodyObject.PionFormatPoWR(PIONFormatPath)
        #******************************************************************************************

    MakeSED_EndTime = time.time()
    RuntimeDict['MakeSED'] = MakeSED_EndTime - MakeSED_StartTime
    # **********************************************************************************************
    # End of Task: Make Spectral Energy Distributions



















    # **********************************************************************************************
    # put this towards the end of main
    if TaskCounter == 0:
        logger.warn("No Actionable Tasks Found.")
        with open(OutputFile, 'a') as outfile:
            outfile.write(msg.NoTaskError)
        sys.exit("PyMicroPION Exiting ...")

    if TaskCounter != 0:
        logger.info(GeneralData['taskname'] + ' Successfull')
        with open(OutputFile, 'a') as outfile:
            outfile.write('\n')
            outfile.write(' - Task Summary:\n')
            outfile.write("   - Task Status [Completed]\n")
            for key, value in RuntimeDict.items():
                outfile.write(f"   - Section {key} runtime: {value:.{6}f} sec\n")

    PyMicroPION_EndTime = time.time()
    PyMicroPION_OverallTime = PyMicroPION_EndTime - PyMicroPION_StartTime
    with open(OutputFile, 'a') as outfile:
            outfile.write(f"   - Overall runtime: {PyMicroPION_OverallTime:.{6}f} sec\n")
            outfile.write("\n")
            outfile.write(f"# End of File\n")
    logger.info(f'--------- PyMicroPIONv' + package_version + ' Finished ---------')
    # **********************************************************************************************

if __name__ == "__main__":
    main()