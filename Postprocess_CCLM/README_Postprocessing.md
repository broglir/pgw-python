#Modify COSMO-CLM initial and boundary conditions

This directory includes python scripts to modify the boundary conditions of the Regional climate model CCLM with output from the scripts in the top-level directory. All these scripts can be run if the conda environment given in pgw_conda_env.yml is used.

In contrast to the top level directory all input for the different functions in this folder must be given within the scripts.

#Typical workflow

**1. rename_2d.py**

This script can be useful when GCM data has been used as input in the previous functions. Using this script the names of variables can be changed to what is used in CCLM. Can be run in command line and takes the old and new variablename as input (e.g. "python rename_2d.py ta T")

**2. laf_adapt.py** 

Modify the initial condition of CCLM. See docstring for more information. Can be run in the command line.

**3. lbfd_adapt.py**

Modify the boundary conditions of one CCLM simulation year. See docstring in python file for more information on input. This takes a longer time to run and using a cluster is recommended (see next step).

**4. submit_lbfd.py**

Creates a batch job submit script that runs the lbfd_adapt.py file on the Piz Daint cluster and submits the jobs for the given years. Piz Daint uses the slrum scheduler.

**5. add_year_end.py**
Can be used to add a folder with a couple of boundary condition files at the intended end of the simulation time. Some versions of CCLM crash if no boundary files for the 2-3 timesteps after the end of the simulation are present (Normally not very important). 
