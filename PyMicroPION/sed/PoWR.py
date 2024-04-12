

import sys
import math
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from itertools import zip_longest
from PyMicroPION.tools import setup_logger
from PyMicroPION.tools import constants as const

logger = setup_logger("PoWR", "pymicropion_activity.log")

# need to write the script to the set of files for a particular model

#there are grids with same temperature but different mdot
#one may write the script to choose the right one for different temperatures 


class PotsdamWolfRayet:
    '''
    ?????????
    '''

    #############################################################################
    def __init__(self, SEDParameter):
        self.SEDParameter = SEDParameter


    #############################################################################
    def BundleUpGrids(self):
        '''
        This method will bundle up the file name for the
        specific input parameters in the ini file.
        detail ???????????????
        :return: Bundled_GridModels: Models specific for input parameters,
        Bundled_ModelFiles': The corresponding model files
        '''

        logger.info(f"Initiating Grid Model Bundling Process for Parameters:")

        # ******************************************************************
        # SECTION: Locating the desired model-parameter files for the given
        # metallicity and composition.
        Metallicity = self.SEDParameter['Metallicity']
        Metallicity = Metallicity.replace(".", "")
        logger.info(f"  Metallicity: {Metallicity}")
        Composition = self.SEDParameter['Composition']
        logger.info(f"  Composition: {Composition}")
        # Data base path
        PoWRDatabase = 'PyMicroPION/data/PoWR/'
        # Grid Name
        GridName = Metallicity.lower() + '-' + Composition.lower()
        # Construct path to the grid directory
        GridDir = PoWRDatabase + GridName + '-sed'
        # Get model parameter file path
        modelparameters_file = GridDir + '/modelparameters.txt'
        #*******************************************************************

        # ******************************************************************
        # SECTION: Parse through the 'modelparameters.txt' file, remove
        # extraneous lines.
        data = []
        with open(modelparameters_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                # Skip lines that don't start with space
                if not line.startswith(" "):
                    continue
                # Skip lines that start with 'MODEL'
                if line.startswith(f"{' ' * 3}MODEL"):
                    continue
                # Save and Skip lines that start with 'NAME'
                if line.startswith(f"{' ' * 3}NAME"):
                    columns_units = line.strip().split()
                    columns_units = [col.strip() for col in columns_units]
                    continue
                # save the data from rest of the lines
                elif line.strip() != "":
                    # Split the line into data values
                    data_values = line.split()
                    data.append(data_values)


        # Create a DataFrame using pandas
        column_names = ['MODEL', 'T_EFF', 'R_TRANS', 'MASS', 'LOG G',
                            'LOG L', 'LOG MDOT', 'V_INF']
        Bundled_DF = pd.DataFrame(data, columns=column_names)
        # Removing original read in data
        del data

        # Add clumping factor to the data frame
        # Get clumping factor for the specific grid
        Clump = const.ClumpFactor[GridName]
        Bundled_DF['CLUMP'] = Clump
        # Adding the grid name as the first column
        Bundled_DF.insert(0, 'GRID', GridName)
        # Save the same to the class object
        self.GridName = GridName
        # ******************************************************************

        # ******************************************************************
        # Calculating stellar radius for each models
        R_star = []
        for index, row in Bundled_DF.iterrows():
            velocity = float(row['V_INF']) / 2500.0
            massloss = 10**float(row['LOG MDOT']) * math.sqrt(row['CLUMP']) * 10**4
            radius = float(row['R_TRANS'])  / (velocity / massloss)**(2/3)
            R_star.append(radius)
        # Adding calculated stellar radius to the Data Frame
        Bundled_DF['R_STAR'] = R_star
        # ******************************************************************

        # ******************************************************************
        # SECTION: Grouping the data frame into sub data frame for same
        # effective temperatures.
        grouped = Bundled_DF.groupby('T_EFF')
        # Create sub-DataFrames for each group
        Bundled_SubDF = [group for _, group in grouped]
        # After grouping, removing the original data frame
        del Bundled_DF
        # ******************************************************************

        # ******************************************************************
        # SECTION: Filtering out all lines and retaining only the
        # line with an Mdot value closest to the given value of 'Mdot' in the
        # input parameter file.
        # First, get 'Mdot' value
        Mdot = float(self.SEDParameter['Mdot'])
        logger.info(f"  Mdot: {Mdot}")
        filtered_dataframe = []
        for sub_dataframe in enumerate(Bundled_SubDF):
            '''
            Each sub-dataframe is represented as a tuple, with the first
            index indicating the tuple index and the second index 
            pointing to the respective data frame.
            '''
            min_index = None
            min_difference = float('inf')  # Initialize with positive infinity

            for index, row in sub_dataframe[1].iterrows():
                diff = np.abs(float(row['LOG MDOT']) - Mdot)
                if diff < min_difference:
                    min_difference = diff
                    min_index = index

            filtered_dataframe.append(sub_dataframe[1].loc[[min_index]])

        # Concatenate the final sub-dataframes into a single dataframe
        BundledModelSet_DF = pd.concat(filtered_dataframe, ignore_index=False)
        # ******************************************************************

        # ******************************************************************
        # Sort the Atlas Bundled Models data frame by effective temperature.
        BundledModelSet_DF['T_EFF'] = pd.to_numeric(BundledModelSet_DF['T_EFF'], errors='coerce')
        BundledModelSet_DF = BundledModelSet_DF.sort_values(by='T_EFF', ascending=True)
        # ******************************************************************

        # ******************************************************************
        # SECTION: Make file paths for all the corresponding final data frame
        FinalizedFileSet = []
        for model in BundledModelSet_DF['MODEL']:
            file = GridDir + '/' + GridName + '_' + model + '_sed.txt'
            FinalizedFileSet.append(file)
        # ******************************************************************

        self.FinalizedFileSet = FinalizedFileSet
        self.BundledModelSet_DF = BundledModelSet_DF
        return BundledModelSet_DF
    #############################################################################





    #############################################################################
    def SpectralEnergyDistributions(self):
        '''
        The objective of this method is to compute the Normalized Flux within
        specified Energy bins for Bundled Grid Models.
        :param Bundled_Grids:
        :return:
        '''

        logger.info(f"Initiating Spectral Energy Distribution Binning")

        # ******************************************************************
        # SECTION: Deriving Lambda Bins from Energy Bins

        # Get Energy Bins from the parameter file
        EnergyBins = self.SEDParameter['EnergyBins']

        # Make energy bin data frame
        EnergyBins_Dataframe = pd.DataFrame(EnergyBins,
                                            columns=['Bin Min (eV)', 'Bin Max (eV)'])
        EnergyBins_Dataframe.columns = \
            pd.MultiIndex.from_tuples([('Energy Bins', col) for
                                       col in EnergyBins_Dataframe.columns])

        # Making Lambda (Wavelenght) Bins from Energy Bins
        LambdaBins = []
        # Loop through the rows (outer loop)
        for EnergyBin in EnergyBins:
            # Loop through the columns (inner loop)
            LambdaBin = []
            for Energy in EnergyBin:
                Lambda = const.ev2Ang/Energy # Waveleghts are given in Angstrom
                LambdaBin.append(Lambda)
            LambdaBin.reverse()
            LambdaBins.append(LambdaBin)
        LambdaBins.reverse()
        # Since the data is in log10, converting LambdaBins to log10 basis.
        LogLambdaBins = np.log10(LambdaBins)

        # Make wavelength bin data frame
        LambdaBins_Dataframe \
            = pd.DataFrame(LambdaBins, columns=['Bin Min (\u00c5)', 'Bin Max (\u00c5)'])
        LambdaBins_Dataframe.columns \
            = pd.MultiIndex.from_tuples([('Wavelength Bins', col)
                                         for col in LambdaBins_Dataframe.columns])

        # Save the Energy Bins and Lambda Bins into EBins_LamBins Data Frame
        EBins_LamBins_DF = pd.concat([EnergyBins_Dataframe, LambdaBins_Dataframe], axis=1)

        # Saving Lambda Bins to the Class Object
        self.EBins_LamBins_DF = EBins_LamBins_DF
        #*************************************************************************


        # ************************************************************************
        # SECTION: Binning
        # Performing flux binning for each finalized model's flux.

        # Models Data
        TotFluxSet = []
        DataSet = []

        # Looping through the bundled models
        for Model, T_eff, R_Star, File, i, in zip_longest(
                self.BundledModelSet_DF['MODEL'],
                self.BundledModelSet_DF['T_EFF'],
                self.BundledModelSet_DF['R_STAR'],
                self.FinalizedFileSet,
                tqdm(self.FinalizedFileSet, desc="Binning ...",
                     ascii=False, ncols=100)):

            logger.debug(f"Binning Flux for Model: {Model}, T_eff: {T_eff:.2e} K")

            # Binning both model wavelength and flux from the original data
            # Initialize x-axis log wavelength and y-axis log flux lambda
            LogModelLambda = []  # Stores the original x-axis data
            LogModelFlux = []  # Stores the original y-axis data
            # Reading Model Txt File =============================================
            with open(File, 'r') as file:
                # Read the file and get log wavelength and log flux lambda
                for line in file:
                    # Strip leading and trailing whitespace from the line
                    line = line.strip()
                    # Check if the line is not empty
                    if line:
                        # Split the line into two parts using whitespace as the
                        # separator
                        columns = line.split()
                        # Convert the parts to float and append them to the
                        # respective arrays
                        LogModelLambda.append(float(columns[0]))
                        LogModelFlux.append(float(columns[1]))

                # Binning lambda values and flam values according to the input
                # Lambda Bins
                LogBinnedLambda = []
                LogBinnedFlux = []
                for bin in LogLambdaBins:
                    LogSubBinnedLambda = []
                    LogSubBinnedFlux = []
                    for loglam, logflam in zip(LogModelLambda, LogModelFlux):
                        if bin[0] <= loglam <= bin[1]:
                            LogSubBinnedLambda.append(loglam)
                            LogSubBinnedFlux.append(logflam)
                    LogBinnedLambda.append(LogSubBinnedLambda)
                    LogBinnedFlux.append(LogSubBinnedFlux)
                # Get the original form of binned wavelength and flux arrays
                BinnedLambda = [[10 ** lam for lam in row] for row in LogBinnedLambda]
                BinnedFlux = [[10 ** flam for flam in row] for row in LogBinnedFlux]
                del LogBinnedLambda
                del LogBinnedFlux

                # Get the original form of binned wavelength and flux from the
                # original model data
                ModelLambda = [10 ** l for l in LogModelLambda]
                ModelFlux = [10 ** flam for flam in LogModelFlux]
                del LogModelLambda
                del LogModelFlux

                # Perform integration across the entire wavelength domain to obtain the
                # total flux.
                TotalFlux10pc = np.trapz(np.asarray(ModelFlux), np.asarray(ModelLambda))
                # However this is the total flux at 10 pc. The total flux at the stellar
                # surface is
                TotalFluxRstar = TotalFlux10pc * \
                                 10**2.0 / (R_Star * const.radiusSun / const.parsec)**2.0
                # Append the Total Flux into TotFluxSe
                TotFluxSet.append(TotalFluxRstar)

                # Check if both arrays have the same dimensions (number of rows)
                if len(BinnedLambda) != len(BinnedFlux):
                    logger.error("PoWR: Binned Array size mismatch")
                    sys.exit("PyMicroPION Exiting ...")

                # Calculating flux in each bin by integrating within the bin interval
                BinFlux = []
                for i in range(len(BinnedLambda)):
                    BinFlux.append(np.trapz(np.asarray(BinnedFlux[i]),
                                            np.asarray(BinnedLambda[i])))

                # Reverse the order of the flux bins since we are interested
                # in obtaining flux in energy bins.
                BinFlux.reverse()

                # Determining the normalized flux within each bin.
                NormBinFlux = BinFlux / TotalFlux10pc
                del BinFlux

                # Appending the result fractional flux for each model to final set
                # BinnedFracFluxSet.append([f"{x:.4e}" for x in NormBinFlux])
                BinnedFracFluxDict = {i: value for i, value in enumerate(NormBinFlux)}
            # End of Reading Model Txt File ======================================

            # Append generated data for each model to the whole DataSet
            DataSet.append({**{'MODEL': Model, 'T_EFF': T_eff, 'TOTFLUX':
                TotalFluxRstar}, **BinnedFracFluxDict})

        # Making the Data Frame for the whole Dataset
        DataSet_DF = pd.DataFrame(DataSet)
        self.DataSet_DF = DataSet_DF

        return {'EBins_LamBins': EBins_LamBins_DF, 'BinnedFracSED': DataSet_DF}
    ##############################################################################




    ##############################################################################
    def PlotPoWR(self, PlotDir):
        '''

        :param PlotDir:
        :return: None
        '''

        # Get maximum and minimum energy in the energy bins
        GetEnergyBins = self.EBins_LamBins_DF['Energy Bins']
        MinPlotEnergy = float(GetEnergyBins['Bin Min (eV)'][0]) - 10.0
        MaxPlotEnergy = float(GetEnergyBins['Bin Max (eV)'].iloc[-1])

        # Calculate bin center value and bin width for each energy bin
        BinsCenter = []
        BinsWidth = []
        for binmin_edge, binmax_edge in zip(GetEnergyBins['Bin Min (eV)'],
                                            GetEnergyBins['Bin Max (eV)']):
            BinsCenter.append((float(binmin_edge) + float(binmax_edge)) / 2)
            BinsWidth.append(float(binmax_edge) - float(binmin_edge))

        # loop over the finalized grid models
        for Grid, Model, T_eff, Mdot, File, Row, i in zip(
                self.BundledModelSet_DF['GRID'],
                self.BundledModelSet_DF['MODEL'],
                self.BundledModelSet_DF['T_EFF'],
                self.BundledModelSet_DF['LOG MDOT'],
                self.FinalizedFileSet,
                self.DataSet_DF.iloc[:, 3:].itertuples(index=False),
                tqdm(self.FinalizedFileSet, desc="Plotting ...", initial=1,
                     ascii=False, ncols=100)):

            # Make a data frame from panda series
            FluxRow_DF = pd.Series(Row)
            # Extract binned flux values to an array
            FluxRow = FluxRow_DF.values


            # **********************************************************************
            # Create a figure with subplots
            fig, axs = plt.subplots(2, 1, figsize=(12, 6))

            # ======================================================================
            # Fetch the original data from the file:
            LogModelLambda = []  # Stores the original x-axis data
            LogModelFlux = []  # Stores the original y-axis data
            # Reading Model Txt File
            with open(File, 'r') as file:
                # Read the file and get log wavelength and log flux lambda
                for line in file:
                    # Strip leading and trailing whitespace from the line
                    line = line.strip()
                    # Check if the line is not empty
                    if line:
                        # Split the line into two parts using whitespace as the
                        # separator
                        columns = line.split()
                        # Convert the parts to float and append them to the
                        # respective arrays
                        LogModelLambda.append(float(columns[0]))
                        LogModelFlux.append(float(columns[1]))

                # Get the original form of binned wavelength and flux from the
                # original model data
                ModelLambda = [10 ** l for l in LogModelLambda]
                ModelFlux = [10 ** flam for flam in LogModelFlux]
                del LogModelLambda
                del LogModelFlux
                # Converting wavelength to energy.
                ModelEnergy = []
                for Lambda in ModelLambda:
                    Energy = const.ev2Ang / Lambda  # Converting wavelength to eV.
                    ModelEnergy.append(Energy)
            # ======================================================================

            # SubPlot 1: Plot the original Atlas9 data
            axs[0].plot(ModelEnergy, ModelFlux, label="Original PoWR Data", color='black',
                                linestyle='-', linewidth=2)
            axs[0].set_xlabel("Energy, eV")
            axs[0].set_ylabel(r'$\rm \ F_{\lambda} \  (ergs \, cm^{-2} s^{-1} \AA^{-1})$ at 10 pc')
            axs[0].set_yscale('log')
            axs[0].set_title(f'Grid: {Grid.upper()}, Model: {Model}, T_eff:'
                             f' {T_eff} K, log Mdot: {Mdot}', fontsize=12)
            axs[0].tick_params(axis="both", direction="inout", which="both",
                               bottom=True, top=True, left=True, right=True, length=3)
            axs[0].legend(loc='upper right')
            axs[0].set_xlim(MinPlotEnergy, MaxPlotEnergy)
            axs[0].grid(True, linestyle='--', alpha=0.5)

            # SubPlot 2: Plot (bar plot) the binned data calculated by PyMicroPion
            axs[1].bar(BinsCenter, FluxRow, width=BinsWidth, align='center',
                       color='orange', alpha=0.5, label="PyMicroPION")
            axs[1].set_xlabel("Energy, eV")
            axs[1].set_ylabel("log (Fractional Binned Flux)")
            axs[1].set_yscale('log')
            axs[1].tick_params(axis="both", direction="inout", which="both",
                               bottom=True, top=True, left=True, right=True, length=3)
            axs[1].legend(loc='upper right')
            axs[1].set_xlim(MinPlotEnergy, MaxPlotEnergy)
            axs[1].grid(True, linestyle='--', alpha=0.5)

            plt.tight_layout()
            imagefile = PlotDir + Grid + '_' + Model + ".png"
            # log message
            logger.debug(f"Saving image" + ' ' + imagefile)
            plt.savefig(imagefile, dpi=100)
            plt.close(fig)
            # **********************************************************************
    ################################################################################




    ################################################################################
    def PionFormatPoWR(self, PlotFormatPathDir):

        # **************************************************************************
        # Converting Input Energy Bins PION cpp 2D-Vector Format
        EnergyBins = self.SEDParameter['EnergyBins']
        #EnergyBins = EnergyBins.values.tolist()
        EnergyBins_PIONFormatName = 'energy_bins'

        EnergyBins_num_rows = len(EnergyBins)
        EnergyBins_num_cols = len(EnergyBins[0]) if EnergyBins_num_rows > 0 else 0

        # Convert the Python 2D list to a C++ 2D array string representation
        EnergyBins_PIONFormat = f"{EnergyBins_PIONFormatName}= {{\n"
        for row in EnergyBins:
            EnergyBins_PIONFormat += "    {"
            EnergyBins_PIONFormat += ', '.join(map(lambda x: f"{x:.6e}", row))
            EnergyBins_PIONFormat += "},\n"
        EnergyBins_PIONFormat += "};"
        # **************************************************************************
        # **************************************************************************
        # Gather SED Model info
        ModelInfoText = f"{'powr_' + self.GridName + '.info'} = " \
                        f"\"#COMMENT: SED - PoWR Model Atmospheres\\n\""\
                        f"\"#COMMENT: SED parameters:\\n\""\
                        f"\"#COMMENT: Metallicity = {self.SEDParameter['Metallicity']}\\n\""\
                        f"\"#COMMENT: Composition = {self.SEDParameter['Composition']}\\n\""\
                        f"\"#COMMENT: Mdot = {self.SEDParameter['Mdot']}\\n\";"
        # **************************************************************************
        # **************************************************************************
        # Converting Binned SED Data Frame into PION cpp 2D-Vector Format
        SED = self.DataSet_DF.drop(['MODEL', 'TOTFLUX'], axis=1)
        SED = SED.values.tolist()
        SED_PIONFormatName = 'powr_' + self.GridName + '.data'

        SED_num_rows = len(SED)
        SED_num_cols = len(SED[0]) if SED_num_rows > 0 else 0

        SED_PIONFormat = f"{SED_PIONFormatName} = {{\n"
        for row in SED:
            SED_PIONFormat += "    {"
            SED_PIONFormat += ', '.join(map(lambda x: f"{x:.6e}", row))
            SED_PIONFormat += "},\n"
        SED_PIONFormat += "};"
        # **************************************************************************

        # PION text formating
        PIONText = ModelInfoText + '\n\n' + EnergyBins_PIONFormat + '\n\n' + SED_PIONFormat
        PIONFormatFile = PlotFormatPathDir + 'powr_' + self.GridName + '_pionformat.txt'
        logger.info(f"Writing PION-formatted PoWR Data into: " + ' ' + PIONFormatFile)
        with open(PIONFormatFile, 'w') as outfile:
            outfile.write(PIONText)


        OutputText = \
            f' - PION-Formating:\n' \
            f'   - PION-Format File: {PIONFormatFile}\n' \
            f'   - File Content: Model configurations (info), Energy bins, Binned SED (data)\n' \
            f'   - Energy Bins Size: {EnergyBins_num_rows} \n' \
            f'   - Binned Spectral Energy Distribution Size: {SED_num_rows} \n' \

        return OutputText
    ################################################################################