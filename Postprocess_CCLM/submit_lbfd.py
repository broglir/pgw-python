"""
Short script to submit the lbfd_adapt.py script to the slurm queue on piz daint.
"""
import subprocess
import os
import sys
startyear = 1970
endyear = 2000 #The last year where boundary data is present

#directory to put submitscripts and output
submitdirectory='/scratch/snx3000/robro/pgwtemp' 

#directory where lbfd_adapt.py is located
scriptdir='/project/pr94/robro/pgw-python/Postprocess_CCLM'
lbdf_dir=''
output_dir=''
diffs_path=''
terrain_path=''


if len(sys.argv)>8:
	submitdirectory=sys.argv[1]
	scriptdir=sys.argv[2]
	startyear = int(sys.argv[3])
	endyear = int(sys.argv[4]) #The last year where boundary data is present
	lbdf_dir=sys.argv[5]
	output_dir=sys.argv[6]
	diffs_path=sys.argv[7]
	terrain_path=sys.argv[8]


for yyyy in range(startyear, endyear + 1):
	with open (f'{submitdirectory}/submit_{yyyy}.bash', 'w') as rsh:
		rsh.write(f'''\
#!/bin/bash -l
#SBATCH --job-name="adapt_{yyyy}"
#SBATCH --time=01:00:00
#SBATCH --partition=normal
#SBATCH --constraint=gpu
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --hint=nomultithread
#SBATCH --account=pr94
#SBATCH --output=output_{yyyy}
#SBATCH --error=error_{yyyy}

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

set -ex

source activate pgw-python3

srun -u python lbfd_adapt.py {yyyy} {lbdf_dir} {output_dir} {diffs_path} {terrain_path}

exit
''')
	
	subprocess.run(f'cp {scriptdir}/lbfd_adapt.py {submitdirectory}', shell=True)
	subprocess.run(f'cp {scriptdir}/heights.txt {submitdirectory}', shell=True)
	os.chdir(submitdirectory)
	subprocess.run(f'sbatch submit_{yyyy}.bash', shell=True)
