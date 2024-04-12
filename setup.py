from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='PyMicroPION',
    version='0.0.9',
    packages=find_packages(),
    license='MIT',
    description='PyMicroPION is a Python package designed to generate binned Spectral Energy Distributions (SEDs) for the MPv10 PION Module.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[],
    url='https://github.com/arunmathewofficial/PyMicroPION',
    author='Arun Mathew',
    author_email='arun@cp.dias.ie',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pymicropion = PyMicroPION.main:main',
        ],
    },

    package_data={
        'PyMicroPION': ['data/Atlas/*/*.fits', 'data/PoWR/*/*.txt'],
    },
)
