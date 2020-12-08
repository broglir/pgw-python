# Repository pgw-python

Software to modify lateral boundary conditions of regional climate simulations 
as described e.g. here https://iopscience.iop.org/article/10.1088/1748-9326/ab4438 or also
here https://doi.org/10.1175/JCLI-D-18-0431.1

The structure of the repository is built as follows:

The top level directory contains the central scripts to modify lateral boundary conditions of any regional climate model using imput from a global or regional climate model. 
Two additional directories contain less generic codes that may be used if the regional climate model COSMO-CLM is used to provide the input (Preprocess_CCLM) for the boundary data modification or/and if the boundary data of COSMO-CLM itself needs to be modified (Postprocess_CCLM; documentation [here](/Postprocess_CCLM/README_Postprocessing.md)).

The scripts regrid and preprocess the so-called climate change deltas which subsequently can be added to the original RCM boundary data.

# Workflows Based on Input Data

**Any Data**

The software is written in python 3 and requires multiple python modules. The ennvironment-file **pgw_conda_env.yml** can be used to install a conda environment to run the software. More information about what conda is and how it works: https://docs.conda.io/projects/conda/en/latest/user-guide/index.html#

To install the enviroment, just execute `conda env create -f environment.yml` once conda is installed. 

**Requeriments**

Annual climate deltas from a global climate model in either daily or monthly steps.
Climate deltas refer to the difference between the fields predicted by the climate model between two different time periods (usually future and present).

**Input On Daily Timescale**

Use settings.py or a similar script to set up the workflow. Run the following scripts:
1) timesmoothing.py
2) interpolation.py 
3) End here if the input grid is the same as the output grid, if not:
4) regrid_horizontal.py
5) cclm_vertical.py (caution if an RCM different from CCLM is used this script needs to be replaced or reprogrammed according to the definition of the vertical grid. But it serves as inspiration)


**Input on Monthly Timescale**

Same procedure as for daily timescale but step 1) timesmoothing.py can be omitted and interpolation.py can be run directly.

**Input from COSMO-CLM**

Prior to running any scripts from the top-level directory the scripts in the folder [Preprocess_CCLM](/Preprocess_CCLM/) may be used produce input that is ready to be read by the top-level scripts.

**Output Intended to Run COSMO-CLM**

After running the top-level scripts the scripts in the folder [Postprocess_ CCLM](/Postprocess_CCLM/) can be used to add the climate change deltas to all boundary and initial fields that have been created by int2lm.

**Model Variables to Modify**

For a physically consistent modification of the lateral boundaries as well as a realistic representation of climate change it is recommended to modify atmospheric temperature, wind, humidity and pressure (depending on the vertical coordinate), as well as surface temperature and humidity. Soil temperature or moisture in the inital conditions may also be modified. Another recommendation is to compute the modification of humidity of the target model using the change in relative humidity (an example of how to do this can be found in [Postprocess_CCLM/laf_adapt.py](/Postprocess_CCLM/laf_adapt.py)), even though this complicates the workflow, it prevents spurious precipitation/humidity changes.

# Further Documentation

Information about the exact purpose of the single pieces of python software can be found in the docstring of the python files themselves. The purpose of the scripts in the top level directory is briefly summarized below:

  **settings.py** -- an example of a kind of "master" script that can be used to provide the necessary arguments and run scripts. Partially has to be changed based on own system.

  **timesmoothing.py** -- Smooth a noisy timeseries (mean annual cycle of a change in a specific varaible)
using a spectral filter. An example output can be seen in Figure S4 here: 
https://iopscience.iop.org/1748-9326/14/11/114017/media/ERL_14_11_114017_suppdata.pdf

  **interpolate.py** -- interpolate a mean annual cycle with either daily or monthly resolution to the
frequency needed for the lateral boundaries (every timestep where a lateral boundary forcing is imposed)

  **regrid_horizontal.py** -- Can be used to bring the input data to the output grid.

  **cclm_vertical.py** -- interpolates pressure level data to height-based model levels. This is very specific to the regional climate model COSMO-CCLM and can only be used for inspiration for other models. This is also a very compute intensive script and should be run on a cluster.
