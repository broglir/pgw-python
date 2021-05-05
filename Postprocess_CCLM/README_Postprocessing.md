# Modify COSMO-CLM initial and boundary conditions

This directory includes python scripts to modify the boundary conditions of the Regional climate model CCLM with output from the scripts in the top-level directory. All these scripts can be run if the conda environment given in [pgw_conda_env.yml](/pgw_conda_env.yml) is used.

If desired, the scripts can be run from the directory's master file [master.py](/Postprocess_CCLM/master.py).

If CSCS users use the [master_notebook.ipynb](/master_notebook.ipynb) jupyter notebook, this workflow is already integrated.

# Typical workflow

**1. rename_variables.py**

This script can be useful when data from another model than CCLM has been used as input in the previous functions. Using this script the names of variables can be changed to what is used in CCLM. Can be run in command line and takes the old and new variablename as input (e.g. "python rename_variables.py ta T").
Usually it has to be used to rename the 2d variables that were not renamed by the previous scripts, but its use can be extended. 

**2. laf_adapt.py** 

Modify the initial conditions of CCLM. See docstring for more information. Can be run in the command line.

**3. lbfd_adapt.py**

Modify the boundary conditions of one CCLM simulation year. See docstring in python file for more information on input. This takes a longer time to run and using a cluster is recommended. [master.py](/Postprocess_CCLM/master.py) can be used to create a batch job submission script for the slrum system.

**4. add_year_end.py**
Can be used to add a folder with a couple of boundary condition files at the intended end of the simulation time. Some versions of CCLM crash if no boundary files for the 2-3 timesteps after the end of the simulation are present (normally not very important). 
