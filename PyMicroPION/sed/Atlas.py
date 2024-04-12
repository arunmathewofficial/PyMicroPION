
import sys
import glob
import os
import re
import numpy as np
import pandas as pd
from tqdm import tqdm
from astropy.io import fits
import matplotlib.pyplot as plt
from itertools import zip_longest
from PyMicroPION.tools import setup_logger
from PyMicroPION.tools import constants as const

logger = setup_logger("Atlas", "pymicropion_activity.log")


class CastelliKuruczAtlas:
    '''
    ?????????
    '''

    #############################################################################
    def __init__(self, SEDParameter):
        self.SEDParameter = SEDParameter
    #############################################################################


    #############################################################################
    def BundleUpModels(self):
        '''
        This method will bundle up the file name for the
        specific input parameters in the ini file.
        detail ???????????????
        :return: Bundled_GridModels: Models specific for input parameters,
        Bundled_GridFiles': The corresponding model files
        '''

        # ***********************************************************************
        # SECTION: Locating the desired files with the given Metallicity
        Metallicity = self.SEDParameter['Metallicity']
        MetallicityString = Metallicity
        # Construct path to the grid directory
        MetallicityValue = float(Metallicity)
        sign = None
        if MetallicityValue < 0:
            sign = 'm'
        if MetallicityValue >= 0:
            sign = 'p'
        Metallicity = Metallicity.replace('-', '').replace('+', '').replace('.', '')
        # Data base path
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        atlas_database = package_dir + '/data/Atlas'
        # Construct path to the grid directory
        grid_dir = atlas_database + '/' + 'ck' + sign + Metallicity
        # Define the fits file pattern.
        file_pattern = 'ck' + sign + Metallicity + '_*.fits'
        # Collecting all fits files with similar names.
        FileSet = glob.glob(os.path.join(grid_dir, file_pattern))
        # ***********************************************************************

        # ***********************************************************************
        # SECTION: Get model name, parameters and file name. Sort the file
        # name array according to the effective temperature.
        # Get Gravity Value from the input parameter file.
        Gravity = self.SEDParameter['Gravity']
        GravityValue = float(Gravity)
        GravityString = str(GravityValue)
        # Model name and parameters.
        ModelName = []
        LOG_Z = []
        T_EFF = []
        LOG_G = []
        # List of tuples to sort the filenames.
        TeffFileSet = []
        # Grid name part for specific metallicity.
        GridName = ('ck' + sign + Metallicity).lower()
        self.GridName = GridName
        for file in FileSet:
            FileMatch = re.search(GridName + r'_(\d+)\.fits', file)
            T = FileMatch.group(1)
            if FileMatch:
                ModelName.append(
                    GridName + '_' + T + '_'
                    + GravityString.replace('-', '').replace('+', '').replace('.', ''))
                LOG_Z.append(MetallicityString)
                T_EFF.append(T)
                LOG_G.append(GravityString)
                TeffFileSet.append((float(T), file))
        # Sorting.
        TeffFileSet.sort(key=lambda x: x[0])
        # Sorted finalized file set.
        FileSet = [file for _, file in TeffFileSet]
        del TeffFileSet
        # ***********************************************************************

        # ***********************************************************************
        # Generating a dataframe containing pertinent information.
        ModelName_DF = pd.DataFrame({'MODEL': ModelName})
        ModelLogZ_DF = pd.DataFrame({'LOG_Z': LOG_Z})
        ModelTeff_DF = pd.DataFrame({'T_EFF': T_EFF})
        ModelLogG_DF = pd.DataFrame({'LOG_G': LOG_G})
        BundledModels_DF = pd.concat([ModelName_DF, ModelTeff_DF,
                                        ModelLogZ_DF, ModelLogG_DF], axis=1)
        del ModelName
        del LOG_Z
        del T_EFF
        del LOG_G

        # Sort the Atlas Bundled Models data frame by effective temperature.
        BundledModels_DF['T_EFF'] = pd.to_numeric(BundledModels_DF['T_EFF'],
                                                  errors='coerce')
        BundledModels_DF = BundledModels_DF.sort_values(by='T_EFF', ascending=True)
        # ***********************************************************************

        logger.info(f"Model Bundling Completed: Successfully bundled "
                    f"{len(FileSet)} models.")
        self.FileSet = FileSet
        self.BundledModels_DF = BundledModels_DF
        return BundledModels_DF
    #############################################################################


    #############################################################################
    def SpectralEnergyDistributions(self):
        '''
        This function take finalized file set from the BundleUPModels and bin the
        spectral energy distribution of each models into the input energy bins
        :return: Energy bins, Wavelength bins and SED binned data
        '''

        logger.info(f"Initiating Spectral Energy Distribution (SED) Binning")

        # ***********************************************************************
        # SECTION: Derive Lambda Bins from Energy Bins

        # Get Energy Bins from the parameter file
        EnergyBins = self.SEDParameter['EnergyBins']

        # Make energy bin data frame
        EnergyBins_DF = pd.DataFrame(EnergyBins, columns=['Bin Min (eV)',
                                                          'Bin Max (eV)'])
        EnergyBins_DF.columns = pd.MultiIndex.from_tuples(
            [('Energy Bins', col) for col in EnergyBins_DF.columns])

        # Making Lambda (Wavelenght) Bins from Energy Bins
        LambdaBins = []
        # Loop through the rows (outer loop)
        for EnergyBin in EnergyBins:
            # Loop through the columns (inner loop)
            LambdaBin = []
            for Energy in EnergyBin:
                Lambda = const.ev2Ang / Energy  # Waveleghts are given in Angstrom
                LambdaBin.append(Lambda)
            LambdaBin.reverse()
            LambdaBins.append(LambdaBin)
        LambdaBins.reverse()

        # Make wavelength bin data frame
        LambdaBins_DF = pd.DataFrame(LambdaBins, columns=['Bin Min (\u00c5)',
                                                          'Bin Max (\u00c5)'])
        LambdaBins_DF.columns = pd.MultiIndex.from_tuples(
            [('Wavelength Bins', col) for col in LambdaBins_DF.columns])

        # Save the Lambda Bins into EBinsLamBins_Dataframe
        EBins_LamBins_DF = pd.concat([EnergyBins_DF, LambdaBins_DF], axis=1)

        # Saving Lambda Bins to the Class Object
        self.EBins_LamBins_DF = EBins_LamBins_DF
        # *************************************************************************


        # ************************************************************************
        # SECTION: Binning
        # Performing flux binning for each finalized model flux in the
        # Finalized File set

        # Models Data
        TotFluxSet = []
        DataSet = []
        FinalizedFileSet = []

        # Looping through the bundled models
        for Model, T_eff, Log_G, File, i, in zip_longest(self.BundledModels_DF['MODEL'],
                                        self.BundledModels_DF['T_EFF'],
                                        self.BundledModels_DF['LOG_G'],
                                        self.FileSet,
                                        tqdm(self.FileSet, desc="Binning ...",
               ascii=False, ncols  = 100)
                                                           ):
            logger.debug(f"SED - Binning Flux for Model: {Model}, T_eff: {T_eff:.2e} K")

            # Make Column name from the input Gravity parameter
            GravityColName = 'g' + Log_G.replace('-', '').replace('+', '').replace('.', '')

            # Fits File Reading ====================================================
            # Atlas model in PyMicroPION database are in fits file format.
            # The datas are obtained form: https://www.stsci.edu/hst/instrumentation/
            # reference-data-for-calibration-and-tools/astronomical-catalogs/castelli-and-kurucz-atlas
            # Open the FITS file to read wavelength and flam
            with fits.open(File) as hdul:
                # The open function returns an object called an HDUList which is a list-like
                # collection of HDU objects. An HDU (Header Data Unit) is the highest level
                # component of the FITS file structure, consisting of a header and (typically)
                # a data array or table.

                # Files opened for reading can be verified and fixed with method
                # HDUList.verify. This method is typically invoked after opening the file but
                # before accessing any headers or data:
                hdul.verify('fix')

                # hdul[0] is the primary HDU, hdul[1] is the first extension HDU
                # The header in hdul[0] of the Atlas fits file contains comprehensive data
                # details, while the actual data is stored in hdul[1].

                # Retrieve the wavelength and FLAM from the designated FITS file.
                ModelLambda = hdul[1].data['Wavelength']
                ModelFlux = hdul[1].data[GravityColName]

                # Binning the wavelength and flux of the original model.
                # Binning lambda values and flam values according to the Lambda
                # Bins (obtained from the input energy bin).
                BinnedLambda = []
                BinnedFlux = []
                for bin in LambdaBins:
                    SubBinnedLambda = []
                    SubBinnedFlux = []
                    for lam, flux in zip(ModelLambda, ModelFlux):
                        if bin[0] <= lam <= bin[1]:
                            SubBinnedLambda.append(lam)
                            SubBinnedFlux.append(flux)
                    BinnedLambda.append(SubBinnedLambda)
                    BinnedFlux.append(SubBinnedFlux)
                    del SubBinnedLambda
                    del SubBinnedFlux

                # Perform integration across the entire wavelength domain to obtain the
                # total flux.
                TotalFlux = np.trapz(np.asarray(ModelFlux), np.asarray(ModelLambda))
                # Append the Total Flux into TotalFlux_BundledGrids
                TotFluxSet.append(TotalFlux)

                # Check if both arrays have the same dimensions (number of rows)
                if len(BinnedLambda) != len(BinnedFlux):
                    logger.error("Atlas: Binned Array size mismatch")
                    sys.exit("PyMicroPION Exiting ...")

                # Calculating flux in each bin by integrating within the bin interval
                BinFlux = []
                for i in range(len(BinnedLambda)):
                    BinFlux.append(np.trapz(np.asarray(BinnedFlux[i]), np.asarray(BinnedLambda[i])))

                # Reverse the order of the flux bins since we are interested in obtaining
                # flux in energy bins.
                BinFlux.reverse()
                # Normalized flux within each bin.
                if TotalFlux == 0.0:
                    NormBinFlux = np.zeros_like(BinFlux)
                else:
                    NormBinFlux = BinFlux / TotalFlux
                # Removing binned flux array
                del BinFlux

                # Appending the result fractional flux for each model to final set
                #BinnedFracFluxSet.append([f"{x:.4e}" for x in NormBinFlux])
                BinnedFracFluxDict = {i: value for i, value in enumerate(NormBinFlux)}
            # End of Fits File Reading ==================================================

            # Make New File Set by Ignoring Model with Zero Total Flux
            if TotalFlux != 0.0:
                FinalizedFileSet.append(File)
                # Append generated data for each model to the whole DataSet
                DataSet.append({**{'MODEL': Model, 'T_EFF': T_eff, 'TOTFLUX': TotalFlux},
                                **BinnedFracFluxDict})


        # Making the Data Frame for the whole Dataset
        DataSet_DF = pd.DataFrame(DataSet)
        self.DataSet_DF = DataSet_DF
        self.FinalizedFileSet = FinalizedFileSet

        return {'EBins_LamBins': EBins_LamBins_DF, 'BinnedFracSED': DataSet_DF}
    #############################################################################



    #############################################################################
    def PlotAtlas(self, PlotDir):
        '''

        :param PlotDir:
        :return: None
        '''

        logger.info(f"Initiating Plotting of Binned SED Data Set.")

        # Get maximum and minimum energy in the energy bins
        GetEnergyBins = self.EBins_LamBins_DF['Energy Bins']
        MinPlotEnergy = 5.0 #float(GetEnergyBins['Bin Min (eV)'][0]) - 10.0
        MaxPlotEnergy = 80.0 #float(GetEnergyBins['Bin Max (eV)'].iloc[-1])

        # Calculate bin center value and bin width for each energy bin
        BinsCenter = []
        BinsWidth = []
        for binmin_edge, binmax_edge in zip(GetEnergyBins['Bin Min (eV)'],
                                            GetEnergyBins['Bin Max (eV)']):
            BinsCenter.append((float(binmin_edge) + float(binmax_edge)) / 2)
            BinsWidth.append(float(binmax_edge) - float(binmin_edge))

        # loop over the finalized grid models
        for Model, T_eff, Log_G, Log_Z, File, TotFlux, Row, i in zip(
                self.BundledModels_DF['MODEL'],
                self.BundledModels_DF['T_EFF'],
                self.BundledModels_DF['LOG_G'],
                self.BundledModels_DF['LOG_Z'],
                self.FinalizedFileSet,
                self.DataSet_DF['TOTFLUX'],
                self.DataSet_DF.iloc[:, 3:].itertuples(index=False),
                tqdm(self.FinalizedFileSet, desc="Plotting ...", initial=1,
                     ascii=False, ncols=100)):

            # Make a data frame from panda series
            FluxRow_DF = pd.Series(Row)
            # Extract binned flux values to an array
            FluxRow = FluxRow_DF.values

            # If the total flux is zero, skip the entire plotting process.
            if TotFlux == 0.0:
                continue
                
            else:

                # **********************************************************************
                # Create a figure with subplots
                fig, axs = plt.subplots(2, 1, figsize=(12, 6))

                GravityColName = 'g' + Log_G.replace('-', '').replace('+', '').replace('.', '')

                # ======================================================================
                # Fetch the original data from the fits file: ModelFile
                with fits.open(File) as hdul:
                    hdul.verify('fix')
                    # Retrieve the wavelength and FLAM from the designated FITS file.
                    ModelLambda = hdul[1].data['Wavelength']  # Wavelengths are given in Angstrom.
                    ModelFlux = hdul[1].data[GravityColName]
                    ModelEnergy = []
                    for Lambda in ModelLambda:
                        Energy = const.ev2Ang / Lambda  # Converting wavelength to electron volt.
                        ModelEnergy.append(Energy)
                # ======================================================================

                # SubPlot 1: Plot the original Atlas9 data
                axs[0].plot(ModelEnergy, ModelFlux, label="Original ATLAS9 Data", color='black',
                            linestyle='-', linewidth=2)
                axs[0].set_xlabel("Energy, eV")
                axs[0].set_ylabel(r'$\rm log \ F_{\lambda} \  (ergs \, cm^{-2} s^{-1} \AA^{-1})$')
                axs[0].set_yscale('log')
                axs[0].set_title(f'Model: {Model},  T_eff: {T_eff} K,  Log Z: {Log_Z}, '
                                 f' Log g: {Log_G}', fontsize=12)
                axs[0].tick_params(axis="both", direction="inout", which="both",
                                   bottom=True, top=True, left=True, right=True, length=3)
                axs[0].legend(loc='upper right')
                axs[0].set_xlim(MinPlotEnergy, MaxPlotEnergy)
                axs[0].grid(True, linestyle='--', alpha=0.5)

                # SubPlot 2: Plot (bar plot) the binned data calculated by PyMicroPion
                axs[1].bar(BinsCenter, FluxRow, width=BinsWidth, align='center', color='orange',
                           alpha=0.5, label="PyMicroPION")
                axs[1].set_xlabel("Energy, eV")
                axs[1].set_ylabel("log Fractional Binned Flux")
                axs[1].set_yscale('log')
                axs[1].tick_params(axis="both", direction="inout", which="both", bottom=True, top=True,
                                   left=True, right=True, length=3)
                axs[1].legend(loc='upper right')
                axs[1].set_xlim(MinPlotEnergy, MaxPlotEnergy)
                axs[1].grid(True, linestyle='--', alpha=0.5)

                plt.tight_layout()
                imagefile = PlotDir + Model + ".png"
                # log message
                logger.debug(f"Plot - Saving image" + ' ' + imagefile)
                plt.savefig(imagefile, dpi=100)
                plt.close(fig)
                # **********************************************************************
    ####################################################################################



    ################################################################################
    def PionFormatAtlas(self, PlotFormatPathDir):

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
        ModelInfoText = f"{'atlas_' + self.GridName + '.info'} = " \
                        f"\"#COMMENT: SED - Atlas Model Atmospheres\\n\""\
                        f"\"#COMMENT: SED parameters:\\n\""\
                        f"\"#COMMENT: LOG Z = {self.SEDParameter['Metallicity']}\\n\""\
                        f"\"#COMMENT: LOG G = {self.SEDParameter['Gravity']}\\n\";"
        # **************************************************************************
        # **************************************************************************
        # Converting Binned SED Data Frame into PION cpp 2D-Vector Format
        SED = self.DataSet_DF.drop(['MODEL', 'TOTFLUX'], axis=1)
        SED = SED.values.tolist()
        SED_PIONFormatName = 'atlas_' + self.GridName + '.data'

        SED_num_rows = len(SED)
        SED_num_cols = len(SED[0]) if SED_num_rows > 0 else 0

        SED_PIONFormat = f"{SED_PIONFormatName} = {{\n"
        for row in SED:
            SED_PIONFormat += "    {"
            SED_PIONFormat += ', '.join(map(lambda x: f"{x:.6e}", row))
            SED_PIONFormat += "},\n"
        SED_PIONFormat += "};"
        # **************************************************************************

        # PIONFormat text file content
        PIONFormat = ModelInfoText + '\n\n' + EnergyBins_PIONFormat + '\n\n' + SED_PIONFormat

        #f'\n\n# PION-Formating ***\n' \
        #f'# PION-Format File: {PIONFormatFile}\n' \
        #f'# File Content: Model Configurations, Energy Bins, Binned SED\n' \
        #f'# Energy Bins - 2D Array with {EnergyBins_num_rows} bins (in unit of eV)\n' \
        #f'# Binned Spectral Energy Distribution - 2D Array with {SED_num_rows} Atlas Models\n' \
        #f'# The initial element in each model represent its effective temperature in K.\n' \
        #f'# The subsequent elements represent fractional dimensionless flux in each bin.\n'

        PIONFormatFile = PlotFormatPathDir + 'atlas_' + self.GridName + '_pionformat.txt'
        logger.info(f"Writing PION-formatted PoWR Data into: " + ' ' + PIONFormatFile)



        with open(PIONFormatFile, 'w') as outfile:
            #outfile.write()
            outfile.write(PIONFormat)

        OutputText = \
            f' - PION-Formating: \n' \
            f'   - PION-Format File: {PIONFormatFile}\n' \
            f'   - File Content: Model Configurations (info), Energy Bins (eV), Binned SED (data)\n' \
            f'   - Energy Bins Size: {EnergyBins_num_rows} \n' \
            f'   - Binned Spectral Energy Distribution Size: {SED_num_rows} \n'

        return OutputText
    ################################################################################