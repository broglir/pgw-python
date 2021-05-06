# Install required python packages at CSCS

This will create a kernel with all python dependencies to be used in jupyterlab provided by CSCS. 

1. Login to CSCS in a terminal
1. wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
1. Run the shell script: bash Miniconda3-latest-Linux-x86_64.sh  ; when asked if you want to use the default install location say no and choose a location on /project or /store
1. Activate conda: eval "$(*/path-to/*miniconda3/bin/conda shell.bash hook)"
1. cd to the location where you saved this repository or clone the repository: git clone https://github.com/broglir/pgw-python.git
1. conda env create -f pgw_conda_env.yml
1. conda activate pgw-python3
1. module load daint-gpu
1. module load jupyter-utils
1. kernel-create -n pgw-python3-kernel

