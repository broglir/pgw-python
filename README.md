# pgw-python

Contains utility functions to modify lateral boundary conditions of regional climate simulations 
as described e.g. here https://iopscience.iop.org/article/10.1088/1748-9326/ab4438 or also
here https://doi.org/10.1175/JCLI-D-18-0431.1


The purpose of the different scripts is as follows:

**pgw_conda_env.yml** -- conda environment file to install a conda environment with the necessary
python modules to run the python scripts in this repository.

**settings.py** -- an example of a kind of "master" script that can be used to provide information
and run the utiliy scripts below. Must be changed based on own system.

**timesmoothing.py** -- Smooth a noisy timeseries (mean annual cycle of a change in a specific varaible)
using a spectral filter. An example output can be seen in Figure S4 here: 
https://iopscience.iop.org/1748-9326/14/11/114017/media/ERL_14_11_114017_suppdata.pdf

**interpolate.py** -- interpolate a mean annual cycle with either daily or monthly resolution to the
frequency needed for the lateral boundaies (every timestep where a lateral boundary forcing is imposed)

**regrid_horizontal.py** -- Can be used to bring the input data to the output grid.

**cclm_vertical.py** -- interpolates pressure level data to height-based model levels. This is very specific to the regional climate model COSMO-CCLM and can only be used for inspiration for other models. This is also a very compute intensive script and should be run on a cluster.

**Typical workflows** (see also settings.py script):

**Daily mean input data**: 1) timesmoothing.py - 2) interpolate.py - 3) regrid_horizontal.py - 4) cclm_vertical.py 

**Monthly mean input data**: 1) interpolate.py - 3) regrid_horizontal.py - 4) cclm_vertical.py 

It is expected that daily input data leads keeps the updated boundary conditions closer to the input data than monthly input.

Further information can be found in each python script.
