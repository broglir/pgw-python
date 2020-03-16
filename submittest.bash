#!/bin/bash -l
#SBATCH --job-name="regrid"
#SBATCH --time=23:50:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --partition=normal
#SBATCH --constraint=gpu
#SBATCH --hint=nomultithread
#SBATCH --account=pr04

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

set -ex

source activate pgw-python3

srun python cclm_vertical.py /scratch/snx3000/lhentge/for_pgw_atlantic/lffd2005112000c.nc /scratch/snx3000/robro/regridded/regridded/ va V /scratch/snx3000/robro/regridded/final/ 11357 1464

exit
