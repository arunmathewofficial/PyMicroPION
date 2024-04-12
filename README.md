# PyMicroPION

PyMicroPION is a Python package designed to generate binned Spectral Energy 
Distributions (SEDs) for the MPv10 PION Module. This tool simplifies the binning SED process
 for any arbitrary energy bins for the Atlas stellar atmosphere models and the Potsdam Wolf-Rayet Models

[PION Page](https://git.dias.ie/massive-stars-software/pion)

[Atlas Page](https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/astronomical-catalogs/castelli-and-kurucz-atlas)

[Potsdam Page](https://www.astro.physik.uni-potsdam.de/~wrh/PoWR/powrgrid1.php)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Examples](#examples)
- [History](#history)
- [GitHub](#github-page)
- [License](#license)

## Installation

### Make a Project Directory 
Make the project directory and navigate to the directory where you need to create 
your virtual environment.

### Create the Virtual Environment:
To create a virtual environment, use the following command, replacing myenv with the name 
you want to give to your virtual environment:
```bash
python3 -m venv myenv
````
### Activate the Virtual Environment:
You can activate the virtual environment by running:
```bash
source myenv/bin/activate
```

### Install the Package:
The following dependencies are required to run PyMicroPION,

* [Python3](https://www.python.org/)
* [Numpy](http://www.numpy.org/)
* [Scipy](https://www.scipy.org/)
* [Matplotlib](http://matplotlib.org/)
* [Pandas](https://github.com/pandas-dev/pandas)
* [Astropy](https://www.astropy.org/)
* [tqdm](https://github.com/tqdm/tqdm)

Ensure that the package you're trying to run is installed within the virtual environment.

You can install PyMicroPION packages into the virtual environment using pip:
```bash
pip install -i https://test.pypi.org/simple/ PyMicroPION==0.0.8
```

## Usage

To use PyMicroPION, provide an input file specifying your desired parameters. For instance:

```bash
$ pymicropion input.ini 
```

## Documentation

No Documentation

## Examples

```bash
$ pymicropion atlas_m05_g40.ini 
```

The input ini file 'atlas_m05_g40.ini' has the following content. 

```ini
; PyMicroPION Input Configuration File

# General
[General]
SimulationName = SED Binning 
OutputDir = test/
OutputFileName = atlas_m05_g40.txt

#Spectral Energy Distributions Binning
[MakeSED] 
Model = ATLAS
Metallicity = -0.5
Gravity = 4.0
# example energy bins (in units of eV)
EnergyBins = [[7.64, 11.2], [11.2, 13.6], [13.6, 16.3],[16.3, 21.56], [21.56, 24.6],
 [24.6, 30.65],[30.65, 35.1], [35.1, 40.96], [40.96, 47.89], [47.89, 54.4],
 [54.4, 64.5], [64.5, 77.0]]
Plot = True
PlotPath = test/atlas_plots/
PIONFormat = True
PIONFormatPath = test/
```
Input: PyMicroPION will process the input file and generate binned SEDs based on the
specified energy bins tailored for the Atlas model, with a specific metallicity value
of -0.5 and gravity set to 4.0.

Output: You will find the generated SEDs in the output directory specified in your input file

## History 

Version 0.0.2 (release data) - Atlas-PoWR SED Binning 

## GitHub Page

[PyMicroPION GitHub Page](https://github.com/arunmathewofficial/PyMicroPION)

## License

The MIT License (MIT)

#### Developer - Arun Mathew (arun@cp.dias.ie)
