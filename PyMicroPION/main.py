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


logger = setup_logger("Main", "pymicropion_activity.log")

def main():
    #global MakeSED_StartTime
    PyMicroPION_StartTime = time.time()
    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument("input_file", help="file path for your ini input parameter file")

    args = parser.parse_args()

    # Get the ini input file path
    ini_file = args.input_file

    RuntimeDict = {}
    # Read the general input parameters
    General_StartTime = time.time()
    GeneralParameters = General(ini_file)
    GeneralData = GeneralParameters.ini_reader()
    General_EndTime = time.time()
    RuntimeDict['General'] = General_EndTime - General_StartTime
    # Task Counter
    TaskCounter = 0

    # Save Version and About information into output file
    OutputFile = GeneralData['outputdir'] + GeneralData['outputfilename']
    with open(OutputFile, 'w') as outfile:
        outfile.write('# ' + msg.VersionInfo + ' Output Summary')
        outfile.write("\n")

    # Read MakeSED parameter
    MakeSEDParameters = MakeSED(ini_file)
    MakeSEDData = MakeSEDParameters.ini_reader(GeneralData)

    # **********************************************************************************************
    # Task No. 1
    if MakeSEDData:
        MakeSED_StartTime = time.time()

        # Always add the Task Counter whenever you add a task.
        TaskCounter += 1

        # Atlas Model %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if MakeSEDData['Model'].lower() == 'atlas':
            logger.info(f'Initiating Binning Spectral Energy Distributions for Atlas')
            AtlasObject = CastelliKuruczAtlas(MakeSEDData)
            logger.info(f"Initiating Atlas Model Bundling from Grids for Parameters:")
            logger.info(f"  Metallicity: {MakeSEDData['Metallicity']}")
            logger.info(f"  Gravity: {MakeSEDData['Gravity']}")
            BundledModels = AtlasObject.BundleUpModels()
            BundledModelsUnits = {'MODEL': 'Name', 'T_EFF': '[K]', 'LOG_Z': '[M/H]', 'LOG_G': '[CGS]'}
            BundledModelsUnits_DF = pd.DataFrame([BundledModelsUnits])
            BundledModelsPlusUnits = pd.concat([BundledModelsUnits_DF, BundledModels], axis=0, ignore_index=True)
            SED = AtlasObject.SpectralEnergyDistributions()
            EBins_LamBins = SED['EBins_LamBins']
            BinnedFracSED = SED['BinnedFracSED']

            # Plot data into plot directory
            if MakeSEDData['Plot']:
                # Get the plot path
                PlotPath = MakeSEDData['PlotPath']
                AtlasObject.PlotAtlas(PlotPath)

            # PION Format
            if MakeSEDData['PIONFormat']:
                # Get the plot path
                PIONFormatPath = MakeSEDData['PIONFormatPath']
                PIONFormat = AtlasObject.PionFormatAtlas(PIONFormatPath)

            # Writting data into output file
            logger.info(f"Writting data into {OutputFile}")
            with open(OutputFile, 'a') as outfile:
                # Converting data frame to string to write to a file
                BundledModelsPlusUnits = BundledModelsPlusUnits.to_string(index=False)
                outfile.write('\n')
                outfile.write("╔══════════════════════════════════════════════╗\n")
                outfile.write(f" Task Parameters\n")
                outfile.write("╚══════════════════════════════════════════════╝\n")
                outfile.write(f" - Name: {GeneralData['taskname']}\n")
                outfile.write(f" - Atmosphere Model: Atlas 9\n")
                outfile.write(f" - Parameters: \n")
                outfile.write(f"   - Metallicity: {MakeSEDData['Metallicity']}\n")
                outfile.write(f"   - Gravity: {MakeSEDData['Gravity']}\n")
                outfile.write(f"   - Energy Bins:\n")
                EBins = EBins_LamBins['Energy Bins'].to_string(index=False)
                EBins_Formatted = '\n'.join('  ' * 2 + line for line in EBins.split('\n'))
                outfile.write(EBins_Formatted)
                outfile.write('\n'*2)
                outfile.write("╔══════════════════════════════════════════════╗\n")
                outfile.write('Computed Data\n')
                outfile.write("╚══════════════════════════════════════════════╝\n")
                outfile.write(f" - Bundled Models:\n")
                Formatted_BundledModels = '\n'.join(' ' * 5 + line for line in BundledModelsPlusUnits.split('\n'))
                outfile.write(Formatted_BundledModels)
                outfile.write('\n' * 2)
                outfile.write(f" - Wavelength Bins:\n")
                LamBins = EBins_LamBins['Wavelength Bins'].to_string(index=False)
                Formatted_Lam = '\n'.join(' ' * 5 + line for line in LamBins.split('\n'))
                outfile.write(Formatted_Lam)
                outfile.write('\n' * 2)
                outfile.write(f" - Fractional Flux Across Energy Bins:\n")

                outfile.write(f" - Units: [Name], [K], [ergs/cm$^{2}$/s], The remaining columns are all in [1]\n")
                outfile.write('\n')
                FracSED = BinnedFracSED.to_string(index=False)
                Formatted_FracSED = '\n'.join(' ' * 4 + line for line in FracSED.split('\n'))
                outfile.write(Formatted_FracSED)
                outfile.write('\n' * 2)
                if MakeSEDData['Plot']:
                    # outfile.write()
                    pass
                if MakeSEDData['PIONFormat']:
                    outfile.write(PIONFormat)


        # PoWR Model %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if MakeSEDData['Model'].lower() == 'powr':
            logger.info(f'Initiating Binning Spectral Energy Distributions for PoWR')
            PoWRObject = PotsdamWolfRayet(MakeSEDData)
            BundledModels = PoWRObject.BundleUpGrids()
            BundledModelsUnits = {'GRID': 'Name', 'MODEL': 'Name', 'T_EFF': '[K]',
                                  'R_TRANS': '[R_SUN]', 'MASS': '[M_SUN]', 'LOG G': '[CGS]',
                                  'LOG L': '[L_SUN]', 'LOG MDOT': '[M_SUN/YR]', 'V_INF': '[KM/S]',
                                  'CLUMP': '[1]', 'R_STAR': '[R_SUN]'}

            BundledModelsUnits_DF = pd.DataFrame([BundledModelsUnits])
            BundledModelsPlusUnits = pd.concat([BundledModelsUnits_DF, BundledModels], axis=0, ignore_index=True)
            SED = PoWRObject.SpectralEnergyDistributions()

            EBins_LamBins = SED['EBins_LamBins']
            BinnedFracSED = SED['BinnedFracSED']

            # Plot data into plot directory
            if MakeSEDData['Plot']:
                # Get the plot path
                PlotPath = MakeSEDData['PlotPath']
                PoWRObject.PlotPoWR(PlotPath)

            # PION Format
            if MakeSEDData['PIONFormat']:
                # Get the plot path
                PIONFormatPath = MakeSEDData['PIONFormatPath']
                PIONFormat = PoWRObject.PionFormatPoWR(PIONFormatPath)

            # Writting data into output file
            logger.info(f"Writting data into {OutputFile}")
            with open(OutputFile, 'a') as outfile:
                # Converting data frame to string to write to a file
                BundledModelsPlusUnits = BundledModelsPlusUnits.to_string(index=False)
                outfile.write('\n')
                outfile.write("╔══════════════════════════════════════════════╗\n")
                outfile.write(f" Task Parameters\n")
                outfile.write("╚══════════════════════════════════════════════╝\n\n")
                outfile.write(f" - Name: {GeneralData['taskname']}\n")
                outfile.write(f" - Atmosphere Model: Potsdam Wolf-Rayet\n")
                outfile.write(f" - Parameters: \n")
                outfile.write(f"   - Metallicity: {MakeSEDData['Metallicity']}\n")
                outfile.write(f"   - Composition: {MakeSEDData['Composition']}\n")
                outfile.write(f"   - Mdot: {MakeSEDData['Mdot']}\n")
                outfile.write(f"   - Energy Bins:\n")
                EBins = EBins_LamBins['Energy Bins'].to_string(index=False)
                EBins_Formatted = '\n'.join('  ' * 2 + line for line in EBins.split('\n'))
                outfile.write(EBins_Formatted)
                outfile.write('\n'*2)
                outfile.write("╔══════════════════════════════════════════════╗\n")
                outfile.write('Computed Data\n')
                outfile.write("╚══════════════════════════════════════════════╝\n")
                outfile.write(f" - Bundled Models:\n")
                Formatted_BundledModels = '\n'.join(' ' * 5 + line for line in BundledModelsPlusUnits.split('\n'))
                outfile.write(Formatted_BundledModels)
                outfile.write('\n' * 2)
                outfile.write(f" - Wavelength Bins:\n")
                LamBins = EBins_LamBins['Wavelength Bins'].to_string(index=False)
                Formatted_Lam = '\n'.join(' ' * 5 + line for line in LamBins.split('\n'))
                outfile.write(Formatted_Lam)
                outfile.write('\n' * 2)
                outfile.write(f" - Fractional Flux Across Energy Bins:\n")
                outfile.write(f" - Units: [Name], [K], [ergs/cm$^{2}$/s], The remaining columns are all in [1]\n")
                outfile.write('\n')
                FracSED = BinnedFracSED.to_string(index=False)
                Formatted_FracSED = '\n'.join(' ' * 4 + line for line in FracSED.split('\n'))
                outfile.write(Formatted_FracSED)
                outfile.write('\n' * 2)
                if MakeSEDData['Plot']:
                    # outfile.write()
                    pass
                if MakeSEDData['PIONFormat']:
                    outfile.write(PIONFormat)


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


            # Writting data into output file
            logger.info(f"Writting data into {OutputFile}")
            with open(OutputFile, 'a') as outfile:
                outfile.write('\n')
                outfile.write("╔══════════════════════════════════════════════╗\n")
                outfile.write(f" Task Parameters\n")
                outfile.write("╚══════════════════════════════════════════════╝\n\n")
                outfile.write(f" - Name: {GeneralData['taskname']}\n")
                outfile.write(f" - Atmosphere Model: Blackbody\n")
                outfile.write(f"   - Energy Bins:\n")
                EBins = EBins_LamBins['Energy Bins'].to_string(index=False)
                EBins_Formatted = '\n'.join('  ' * 2 + line for line in EBins.split('\n'))
                outfile.write(EBins_Formatted)
                outfile.write('\n'*2)
                outfile.write("╔══════════════════════════════════════════════╗\n")
                outfile.write('Computed Data\n')
                outfile.write("╚══════════════════════════════════════════════╝\n")
                outfile.write('\n')
                outfile.write(f" - Wavelength Bins:\n")
                LamBins = EBins_LamBins['Wavelength Bins'].to_string(index=False)
                Formatted_Lam = '\n'.join(' ' * 5 + line for line in LamBins.split('\n'))
                outfile.write(Formatted_Lam)
                outfile.write('\n' * 2)
                outfile.write(f" - Fractional Flux Across Energy Bins:\n")
                outfile.write(f" - Units: [Name], [K], [ergs/cm$^{2}$/s], The remaining columns are all in [1]\n")
                outfile.write('\n')
                FracSED = BinnedFracSED.to_string(index=False)
                Formatted_FracSED = '\n'.join(' ' * 4 + line for line in FracSED.split('\n'))
                outfile.write(Formatted_FracSED)
                outfile.write('\n' * 2)

                if MakeSEDData['Q_H']:
                    outfile.write(f" - Q(H) and Luminosity of Black Body star:\n")
                    outfile.write(f" - Units: [Name], [K], [s$^{-1}$], [1], [erg/s], [1]\n")
                    outfile.write('\n')
                    QHSetData = QHSet.to_string(index=False)
                    Formatted_QHSetData = '\n'.join(' ' * 4 + line for line in QHSetData.split('\n'))
                    outfile.write(Formatted_QHSetData)
                    outfile.write('\n' * 2)

                if MakeSEDData['Plot']:
                    # outfile.write()
                    pass
                if MakeSEDData['PIONFormat']:
                    outfile.write(PIONFormat)



    MakeSED_EndTime = time.time()
    RuntimeDict['MakeSED'] = MakeSED_EndTime - MakeSED_StartTime
    # End of Task No. 1
    # **********************************************************************************************




















    # **********************************************************************************************
    # put this towars the end of main
    if TaskCounter == 0:
        logger.warn("No Actionable Tasks Found.")
        with open(OutputFile, 'a') as outfile:
            outfile.write(msg.NoTaskError)
        sys.exit("PyMicroPION Exiting ...")

    if TaskCounter != 0:
        logger.info(GeneralData['taskname'] + ' Successfully Completed')
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

    # **********************************************************************************************

if __name__ == "__main__":
    main()