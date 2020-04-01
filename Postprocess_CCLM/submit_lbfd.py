"""
Short script to submit the lbfd_adapt.py script to the slurm queue on piz daint.
"""
import subprocess
import os

startyear = 1970
endyear = 2000 #The last year where boundary data is present

#directory to put submitscripts and output
submitdirectory='/scratch/snx3000/robro/pgwtemp' 

#directory where lbfd_adapt.py is located
scriptdir='/project/pr04/robro/pgw-python/Postprocess_CCLM'

for yyyy in range(startyear, endyear + 1):
	with open (f'{submitdirectory}/submit_{yyyy}.bash', 'w') as rsh:
		rsh.write(f'''\
#!/bin/bash -l
#SBATCH --job-name="adapt_{yyyy}"
#SBATCH --time=00:30:00
#SBATCH --partition=prepost
#SBATCH --constraint=mc
#SBATCH --hint=nomultithread
#SBATCH --account=pr94

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

set -ex

source activate pgw-python3

srun -u python lbfd_adapt.py {yyyy}

exit
''')
	
	subprocess.run(f'cp {scriptdir}/lbfd_adapt.py {submitdirectory}', shell=True)
	os.chdir(submitdirectory)
	subprocess.run(f'sbatch submit_{yyyy}.bash', shell=True)
