# PyMicroPION comments and error messages
import pkg_resources

distribution = pkg_resources.get_distribution('PyMicroPION')
package_version = distribution.version
package = "PyMicroPIONv" + package_version
metadata = distribution.get_metadata(distribution.PKG_INFO)



dashes = '-' * 30


About = ' About\n'

NoTaskError = 'No Task Found'

# Define the content
content = """# AVS field file        !
#                       !
ndim   =  3             ! dimension of data
dim1   = 53             ! no. of grid points in x direction
dim2   = 53             ! no. of grid points in y direction
dim3   = 70             ! no. of grid points in z direction
nspace =  3             ! dimension of data
veclen =  1             ! length of data vector (1 means scalar quantity)
data   = float          ! data type   integer / float / double  (integer precision / single-precision real number / double-precision real number)
field  = rectilinear    ! rectilinear coordinate system
label  = material_grid  ! name of data files to be proceeded
"""

ExitMsg = package + " Exiting ..."
TaskList = ["makesed"]



#####################################################################################
# ATLAS LOG AND ERROR

AtlasModelsUnits = {'MODEL': 'Name', 'T_EFF': '[K]', 'LOG_Z': '[M/H]', 'LOG_G': '[CGS]'}
def AtlasInputINFO(MakeSEDData):
    return f"Initiating Binning Spectral Energy Distributions for Atlas\n"\
           f"Initiating Atlas Model Bundling from Grids for Parameters:\n"\
           f"  Metallicity: {MakeSEDData['Metallicity']}\n"\
           f"  Gravity: {MakeSEDData['Gravity']}"


# Metallicity Errors
AtlasMetallicityInvalidKeyError = '''\n
# Atlas Metallicity Invalid Key Error:
#
# The Atlas model provides spectral energy distributions for a predefined set of 
# metallicities. Therefore, it is crucial to provide accurate and valid metallicity 
# values when utilizing PyMicroPION. The acceptable metallicity values are as 
# follows: -0.5, -1.5, -2.0, -2.5, 0.0, 0.2, and 0.5. If you enter a value or format 
# different from these allowed options, the package will terminate with an error. 
# Double-check your input and ensure it aligns with one of these permissible values.
'''
AtlasMetallicityNoKeyError = '''\n
# No Metallicity Key Found Error:
#
# When using the ATLAS MODEL in PyMicroPION, ensure you specify the metallicity key 
# with one of these acceptable values: -0.5, -1.5, -2.0, -2.5, 0.0, 0.2, or 0.5.
# For example:
# 
# [MakeSED]
# Metallicity = -0.5
'''
AtlasMetallicityEmptyKeyError = '''\n
# Empty Metallicity Key Error:
#
# When using the ATLAS MODEL in PyMicroPION, ensure you specify the metallicity key 
# with one of these acceptable values: -0.5, -1.5, -2.0, -2.5, 0.0, 0.2, or 0.5.
'''

# Gravity Errors
AtlasGravityInvalidKeyError = '''\n
# Atlas Gravity Invalid Key Error:
#
# The PyMicroPION model relies on the correct value of gravity to bin the spectral energy
# distribution for the Atlas model. It is essential to input valid gravity values within 
# the accepted range. The acceptable gravity values are as follows: 0.0, 0.5, 1.0, 1.5, 
# 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, and 5.0. If you provide a gravity value that is not in 
# the above list or use a different format, PyMicroPION will terminate with an error.
# Double-check your input and ensure it corresponds to one of these permissible gravity 
# values.
'''
AtlasGravityNoKeyError = '''\n
# No Gravity Key Found Error:
#
# When using the ATLAS MODEL in PyMicroPION, ensure you specify the gravity key with one 
# of these acceptable values: 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, or 5.0.
# For example:
#
# [MakeSED]
# Gravity = 4.0 
'''
AtlasGravityEmptyKeyError = '''\n
# Empty Gravity Key Error:
#
# When using the ATLAS MODEL in PyMicroPION, ensure you specify the gravity key with one 
# of these acceptable values: 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, or 5.0.
'''

# Energy Bin Errors
AtlasEnergyBinInvalidKeyError = '''\n
# Atlas Energy Bin Invalid Key Error:
#
# The PyMicroPION binning of the spectral energy distribution model in Atlas requires specifying 
# energy bins within a valid energy range. An acceptable PyMicroPION format for the energy bins is
# a two-dimensional array, with the outer array specifying each energy bin and the inner array 
# containing the bin edge values of the corresponding bins.
'''
AtlasEnergyBinNoKeyError = '''\n
# Energy Bin Key Not Found Error:
#
# When using MakeSED to bin the spectral energy distribution with PyMicroPION, make sure to 
# specify the Energy bin key. An acceptable format is a two-dimensional array, with the outer 
# array specifying each energy bin and the inner array containing the bin edge values of the 
# corresponding bins.
# The acceptable format is as follows:
#
# [MakeSED]
# EnergyBins = [[0.1, 1.1], [1.1, 3.6], [3.6, 5.7], [5.7, 7.64], [7.64, 11.2], [11.2, 13.6], 
# [13.6, 16.3], [16.3, 21.56], [21.56, 24.6], [24.6, 30.65], [30.65, 35.1], [35.1, 40.96], 
# [40.96, 47.89], [47.89, 54.4], [54.4, 64.5], [64.5, 77.0]]
'''
AtlasEnergyBinEmptyKeyError = '''\n
# Empty Energy Bin Key Error:
#
# When using MakeSED to bin the spectral energy distribution with PyMicroPION, make sure to 
# specify the Energy bin key.
'''


#####################################################################################
# PoWR LOG AND ERROR

PoWRModelsUnits = {'GRID': 'Name', 'MODEL': 'Name', 'T_EFF': '[K]',
                   'R_TRANS': '[R_SUN]', 'MASS': '[M_SUN]', 'LOG G': '[CGS]',
                   'LOG L': '[L_SUN]', 'LOG MDOT': '[M_SUN/YR]', 'V_INF': '[KM/S]',
                   'CLUMP': '[1]', 'R_STAR': '[R_SUN]'}
