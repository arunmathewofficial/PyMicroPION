"""
Reading functions for the input file
"""
import configparser
import sys
from PyMicroPION.tools import setup_logger
import os
from PyMicroPION.tools import messages as msg


# Create a logger named "my_app_logger" that logs to "app.log" file
logger = setup_logger("write", "pymicropion_activity.log")

class MakeSEDWriter:

    def __init__(self, file):
        self.output_file_path = file


    # Atlas Model %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def MakeSED_Atlas_Writer(self, MakeSEDData, BundledModelsPlusUnits, EBins_LamBins,
                             BinnedFracSED):
        logger.info(f"Writting data into {self.output_file_path}")
        with open(self.output_file_path, 'a') as outfile:
            outfile.write("Task: Atlas Spectral Energy Distributions Binning \n")
            # Converting data frame to string to write to a file
            BundledModelsPlusUnits = BundledModelsPlusUnits.to_string(index=False)
            outfile.write('\n')
            outfile.write(f" <<Task Parameters>>\n")
            outfile.write(f" - Atmosphere Model: Atlas 9\n")
            outfile.write(f" - Parameters: \n")
            outfile.write(f"   - Metallicity: {MakeSEDData['Metallicity']}\n")
            outfile.write(f"   - Gravity: {MakeSEDData['Gravity']}\n")
            outfile.write(f"   - Energy Bins:\n")
            EBins = EBins_LamBins['Energy Bins'].to_string(index=False)
            EBins_Formatted = '\n'.join('  ' * 2 + line for line in EBins.split('\n'))
            outfile.write(EBins_Formatted)
            outfile.write('\n')
            outfile.write('<<Computed Data>>\n')
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

            outfile.write(f" - Units: [Name], [K], [ergs/cm$^{2}$/s], The remaining columns are dimensionless\n")
            outfile.write('\n')
            FracSED = BinnedFracSED.to_string(index=False)
            Formatted_FracSED = '\n'.join(' ' * 4 + line for line in FracSED.split('\n'))
            outfile.write(Formatted_FracSED)
            outfile.write('\n' * 2)
            if MakeSEDData['Plot']:
                # outfile.write()
                pass
            if MakeSEDData['PIONFormat']:
                pass
                #self.outfile.write(PIONFormat)




    # PoWR Model %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def MakeSED_PoWR_Writer(self, MakeSEDData, BundledModelsPlusUnits, EBins_LamBins,
                             BinnedFracSED):

        # Writting data into output file
        logger.info(f"Writting data into {self.output_file_path}")
        with open(self.output_file_path, 'a') as outfile:
            # Converting data frame to string to write to a file
            BundledModelsPlusUnits = BundledModelsPlusUnits.to_string(index=False)
            outfile.write('\n')
            outfile.write(f"<<Task Parameters>>\n")
            outfile.write(f" - Atmosphere Model: Potsdam Wolf-Rayet\n")
            outfile.write(f" - Parameters: \n")
            outfile.write(f"   - Metallicity: {MakeSEDData['Metallicity']}\n")
            outfile.write(f"   - Composition: {MakeSEDData['Composition']}\n")
            outfile.write(f"   - Mdot: {MakeSEDData['Mdot']}\n")
            outfile.write(f"   - Energy Bins:\n")
            EBins = EBins_LamBins['Energy Bins'].to_string(index=False)
            EBins_Formatted = '\n'.join('  ' * 2 + line for line in EBins.split('\n'))
            outfile.write(EBins_Formatted)
            outfile.write('\n' * 2)
            outfile.write('<<Computed Data>>\n')
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
            outfile.write(f" - Units: [Name], [K], [ergs/cm$^{2}$/s], The remaining columns are dimensionless\n")
            outfile.write('\n')
            FracSED = BinnedFracSED.to_string(index=False)
            Formatted_FracSED = '\n'.join(' ' * 4 + line for line in FracSED.split('\n'))
            outfile.write(Formatted_FracSED)
            outfile.write('\n' * 2)
            if MakeSEDData['Plot']:
                # outfile.write()
                pass
            if MakeSEDData['PIONFormat']:
                pass
                #outfile.write(PIONFormat)




    # BlackBody Model %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def MakeSED_BB_Writer(self, MakeSEDData, EBins_LamBins, BinnedFracSED, QHSet):
        logger.info(f"Writting data into {self.output_file_path}")
        with open(self.output_file_path, 'a') as outfile:
            outfile.write('\n')
            outfile.write(f"<<Task Parameters>>\n")
            outfile.write(f" - Atmosphere Model: Blackbody\n")
            outfile.write(f"   - Energy Bins:\n")
            EBins = EBins_LamBins['Energy Bins'].to_string(index=False)
            EBins_Formatted = '\n'.join('  ' * 2 + line for line in EBins.split('\n'))
            outfile.write(EBins_Formatted)
            outfile.write('\n' * 2)
            outfile.write('<<Computed Data>>\n')
            outfile.write(f" - Wavelength Bins:\n")
            LamBins = EBins_LamBins['Wavelength Bins'].to_string(index=False)
            Formatted_Lam = '\n'.join(' ' * 5 + line for line in LamBins.split('\n'))
            outfile.write(Formatted_Lam)
            outfile.write('\n')
            outfile.write(f" - Fractional Flux Across Energy Bins:\n")
            outfile.write(f" - Units: [Name], [K], [ergs/cm$^{2}$/s], The remaining columns are dimensionless\n")
            outfile.write('\n')
            FracSED = BinnedFracSED.to_string(index=False)
            Formatted_FracSED = '\n'.join(' ' * 4 + line for line in FracSED.split('\n'))
            outfile.write(Formatted_FracSED)
            outfile.write('\n' * 2)

            if not QHSet.empty:
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
                pass
                #outfile.write(PIONFormat)
