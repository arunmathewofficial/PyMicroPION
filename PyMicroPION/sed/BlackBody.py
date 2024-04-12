

import sys
import math
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from itertools import zip_longest
from PyMicroPION.tools import setup_logger
from PyMicroPION.tools import constants as const
from scipy import integrate
logger = setup_logger("BlackBody", "pymicropion_activity.log")

# need to write the script to the set of files for a particular model

#there are grids with same temperature but different mdot
#one may write the script to choose the right one for different temperatures 


class BlackBody:
    '''
    ?????????
    '''

    #############################################################################
    def __init__(self, SEDParameter):
        self.SEDParameter = SEDParameter

    #############################################################################
    def BB_BinFracFunction(self, T, E):
        factor = 2.0*const.pi / pow(const.h, 3.0) / pow(const.c, 2.0) / const.stefanBoltzmann / pow(T, 4.0)
        return factor * pow(E, 3.0) / (math.exp(E / const.kB / T ) - 1.0)


    #############################################################################
    def BB_FluxLambda(self, T, lam):
        factor = 2.0*const.pi*const.h*pow(const.c, 2.0) / pow(lam*const.Ang2cm, 4.0) / lam
        return factor / (math.exp(const.h * const.c / (lam*const.Ang2cm) / const.kB / T) - 1.0)

    #############################################################################
    def QHPerUnitArea(self, T, E):
        factor = 2.0*const.pi / pow(const.h, 3.0) / pow(const.c, 2.0)
        return factor * pow(E, 2.0) / (math.exp(E / const.kB / T) - 1.0)

    #############################################################################
    def SpectralEnergyDistributions(self):

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
                Lambda = const.ev2Ang / Energy # Waveleghts are given in Angstrom
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
        # Performing flux binning for black body spectrum for different temperatures

        # Maximum energies
        Max_Energy = EnergyBins[-1][-1]
        self.MaxinumEnergy = Max_Energy

        TotFluxSet = []
        BinnedFluxSet = []
        # Looping through the bundled models
        for T_eff, i in zip_longest(
                const.BB_Temperature_Table,
                tqdm(const.BB_Temperature_Table, desc="Binning ...",
                     ascii=False, ncols=100)):

            modelname = 'bb_' + str(int(T_eff))

            NormBinFlux = []
            for EnergyBin in EnergyBins:
                result, error = integrate.quad(lambda E: self.BB_BinFracFunction(T_eff, E),
                                               EnergyBin[0]*const.ev2Erg, EnergyBin[1]*const.ev2Erg)
                NormBinFlux.append(result)
                TotalFlux = const.stefanBoltzmann * pow(T_eff, 4.0)

            TotFluxSet.append(TotalFlux)
            BinnedFracFluxDict = {i: value for i, value in enumerate(NormBinFlux)}
            BinnedFluxSet.append({**{'MODEL': modelname, 'T_EFF': T_eff, 'TOTFLUX': TotalFlux}, **BinnedFracFluxDict})

        # Making the Data Frame for the whole Dataset
        BinnedFluxSet_DF = pd.DataFrame(BinnedFluxSet)
        self.BinnedFluxSet_DF = BinnedFluxSet_DF

        return {'EBins_LamBins': EBins_LamBins_DF, 'BinnedFracSED': BinnedFluxSet_DF}

    ##############################################################################


    ##############################################################################
    def CalculateQH(self, Rstar):

        A = 4.0*const.pi*pow(Rstar*const.radiusSun, 2.0) # Stellar surface area of the star
        QHDataSet = []

        for T_eff, i in zip_longest(
                const.BB_Temperature_Table,
                tqdm(const.BB_Temperature_Table, desc="Calculating Q(H) ...",
                     ascii=False, ncols=100)):

            modelname = 'bb_' + str(int(T_eff))

            QH_perunitarea, error = integrate.quad(lambda E: self.QHPerUnitArea(T_eff, E),
                                                   const.IE_Hydrogen*const.ev2Erg, self.MaxinumEnergy*const.ev2Erg)

            LStar = A * const.stefanBoltzmann * pow(T_eff, 4.0)

            QH = A * QH_perunitarea
            QHDataSet.append({**{'MODEL': modelname, 'T_EFF': T_eff, 'QH': QH, 'Log QH': np.log10(QH), 'L': LStar, 'Log L': np.log10(LStar)}})

        # Making the Data Frame for the whole Dataset
        QHDataSet_DF = pd.DataFrame(QHDataSet)
        self.QHDataSet_DF = QHDataSet_DF

        return {'QHSet': QHDataSet_DF}





    ##############################################################################
    def PlotBB(self, PlotDir):


        # Get maximum and minimum energy in the wavelenghts
        GetWavelengthBins = self.EBins_LamBins_DF['Wavelength Bins']
        MinLambda = float(GetWavelengthBins['Bin Min (\u00c5)'][0]) - 50.0
        MaxLambda = float(GetWavelengthBins['Bin Max (\u00c5)'].iloc[-1]) + 200.0
        # Make a small lambda array
        Lambda_Array = np.linspace(MinLambda, MaxLambda, 15)
        FluxLambdaDataSet = []

        # Looping through the bundled models
        for T_eff, i in zip_longest(
                const.BB_Temperature_Table,
                tqdm(const.BB_Temperature_Table, desc="Making Flux-Lambda ...",
                     ascii=False, ncols=100)):

            Model = 'bb_' + str(int(T_eff))

            FluxLambda = []
            for Lambda in Lambda_Array:
                FluxLambda.append(self.BB_FluxLambda(T_eff, Lambda))

            FluxLambdaDict = {i: value for i, value in enumerate(FluxLambda)}
            FluxLambdaDataSet.append({**{'MODEL': Model, 'T_EFF': T_eff}, **FluxLambdaDict})

            # Making the Data Frame for the whole Dataset
        FluxLambdaDataSet_DF = pd.DataFrame(FluxLambdaDataSet)


        # **********************************************************************
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

        # ======================================================================
        # Converting wavelength array to energy array
        Energy_Array = []
        for Lambda in Lambda_Array:
            Energy = const.ev2Ang / Lambda  # Converting wavelength to eV.
            Energy_Array.append(Energy)

        # loop over the finalized grid models
        for Model, T_eff, BinnedRow, FlamRow, i in zip(
                self.BinnedFluxSet_DF['MODEL'],
                self.BinnedFluxSet_DF['T_EFF'],
                self.BinnedFluxSet_DF.iloc[:, 3:].itertuples(index=False),
                FluxLambdaDataSet_DF.iloc[:, 2:].itertuples(index=False),
                tqdm(const.BB_Temperature_Table, desc="Plotting ...", initial=1, ascii=False, ncols=100)):

            # Make a data frame from panda series
            BinnedFluxRow_DF = pd.Series(BinnedRow)
            BinnedFluxRow = BinnedFluxRow_DF.values

            FlamRow_DF = pd.Series(FlamRow)
            Flam = FlamRow_DF.values

            # **********************************************************************
            # Create a figure with subplots
            fig, axs = plt.subplots(2, 1, figsize=(12, 6))

            # SubPlot 1: Plot the original Atlas9 data
            axs[0].plot(Energy_Array, Flam, label="Blackbody Data", color='black',
                        linestyle='-', linewidth=2)
            axs[0].set_xlabel("Energy, eV")
            axs[0].set_ylabel(r'$\rm log \ F_{\lambda} \  (ergs \, cm^{-2} s^{-1} \AA^{-1})$')
            #axs[0].set_yscale('log')
            axs[0].set_title(f'Model: {Model}, T_eff: {T_eff} K', fontsize=12)
            axs[0].tick_params(axis="both", direction="inout", which="both",
                               bottom=True, top=True, left=True, right=True, length=3)
            axs[0].legend(loc='upper right')
            axs[0].set_xlim(MinPlotEnergy, MaxPlotEnergy)
            axs[0].grid(True, linestyle='--', alpha=0.5)


            # SubPlot 2: Plot (bar plot) the binned data calculated by PyMicroPion
            axs[1].bar(BinsCenter, BinnedFluxRow, width=BinsWidth, align='center',
                       color='orange', edgecolor='black', alpha=0.5, label="PyMicroPION")
            axs[1].set_xlabel("Energy, eV")
            axs[1].set_ylabel("log (Fractional Binned Flux)")
            axs[1].set_yscale('log')
            axs[1].tick_params(axis="both", direction="inout", which="both",
                               bottom=True, top=True, left=True, right=True, length=3)
            axs[1].legend(loc='upper right')
            axs[1].set_xlim(MinPlotEnergy, MaxPlotEnergy)
            axs[1].grid(True, linestyle='--', alpha=0.5)

            plt.tight_layout()
            imagefile = PlotDir + Model + ".png"
            # log message
            logger.debug(f"Saving image" + ' ' + imagefile)
            plt.savefig(imagefile, dpi=100)
            plt.close(fig)


        return {'FluxLambda': FluxLambdaDataSet_DF}
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
        ModelInfoText = f"{'blackbody.info'} = " \
                        f"\"#COMMENT: SED - Blackbody\\n\";"
        # **************************************************************************
        # **************************************************************************
        # Converting Binned SED Data Frame into PION cpp 2D-Vector Format
        SED = self.BinnedFluxSet_DF.drop(['MODEL', 'TOTFLUX'], axis=1)
        SED = SED.values.tolist()
        SED_PIONFormatName = 'blackbody.data'

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
        PIONFormatFile = PlotFormatPathDir + 'blackbody_pionformat.txt'
        logger.info(f"Writing PION-formatted Blackbody Data into: " + ' ' + PIONFormatFile)
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