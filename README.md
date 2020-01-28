# pgw-python

Contains utility functions to modify lateral boundary conditions of regional climate simulations 
as described e.g. here https://iopscience.iop.org/article/10.1088/1748-9326/ab4438 or also
here https://doi.org/10.1175/JCLI-D-18-0431.1


The purpose of the different scripts is as follows:

pgw_conda_env.yml -- conda environment file to install a conda environment with the necessary
python module to run the python scripts

settings.py -- an example of a kind of "master" script that can be used to provide information
and run the utiliy scripts below. Must be changed based on own system.

humidity_difference_via_RH.py -- Calculate the difference in specific humidity between two time steps using relative humidity. 
Has been shown to prevent lateral boundaries from drying unrealistically here https://doi.org/10.1007/s00382-016-3276-3

timesmoothing.py -- Smooth a noisy timeseries (mean annual cycle of a change in a specific varaible)
using a spectral filter. An example output can be seen in Figure S4 here: 
https://iopscience.iop.org/1748-9326/14/11/114017/media/ERL_14_11_114017_suppdata.pdf

interpolate.py -- interpolate a mean annual cycle with either daily or monthly resolution to the
frequency needed for the lateral boundaies (update frequency)
