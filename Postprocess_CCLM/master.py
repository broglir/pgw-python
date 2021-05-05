import sys
import os
import numpy as np
import glob
import subprocess
import xarray as xr

'''
Master script to run the workflow. Similar structure to settings.py in parent directory.
Alternatively scripts can also be seperately submitted.

'''

difference_2d_files_path='/scratch/snx3000/jvergara/PGW/temporaly_and_horizontaly_interpolated/'
difference_files_path='/scratch/snx3000/robro/pgwtemp/final2/'

constant_variables_file='/store/c2sm/ch4/robro/surrogate_input/lffd2005112000c.nc'

output_path='/scratch/snx3000/robro/PGW_atl_04/output/ifs2lm'

recompute_pressure=True

st_year=2004
end_year=2004


lbfds_files_path='/scratch/snx3000/robro/PGW_atl_04/output/org_ifs2lm'

#lafpath = f'{lbfds_files_path}/{st_year}'
lafpath = lbfds_files_path
laf_file=glob.glob(f'{lafpath}/laf*')[0]
#print(laf_file)
year_laf=laf_file.split('laf')[1][:4]
#print(year_laf)


outputtimesteps=366 * 4
starttimestep=305 * 4 #0 for 1st of january then count up depending on boundary update frequency

#how many years to add to lbfd and laf files? #for nomal calendars should be
#able to devide by 4 due to leap years (needed for adjustment of CO2 concentrations)
changeyears=88
year_laf = int(year_laf) + changeyears

#put the correct start date
laftimestring = f'seconds since {year_laf}-11-01 00:00:00'

#directory where to submit to queue (scratch)
sc_directory='/scratch/snx3000/robro/pgwtemp/'
#directory where the script is
script_directory='~/software/pgw-python/Postprocess_CCLM'





execute_rename=0

if execute_rename:
	print('Renaming 2D fields')
	variablename_cmor = [ 'hurs', 'tas' ]
	variablename_cclm = ['RELHUM_S', 'T_S'] #tas is modifiyed to T_S instead of T_2M to adapt the sea surface temps
	for i in range(len(variablename_cclm)):
		cmd=f'python rename_variables.py {variablename_cmor[i]} {variablename_cclm[i]} {difference_2d_files_path} {difference_files_path} {outputtimesteps}'
		a=os.system(cmd)


execute_adapt_laf=1

if execute_adapt_laf:
	print('Executing addition of signal to laf file')
	cmd=f'python laf_adapt.py {laf_file} {year_laf} {output_path} {difference_files_path} {constant_variables_file} "{laftimestring}" {starttimestep} {recompute_pressure}'
	print(cmd)
	a=os.system(cmd)

execute_lbfd=1

if execute_lbfd:
	print('Executing addition of signal to lbfd files')

	for yyyy in range(st_year, end_year + 1):
		newyear = yyyy + changeyears

		if end_year - st_year > 0: # if one wants to sumbit multiple jobs for different years, files should be grouped in folders for the year
			output_path = f'{output_path}/{newyear}/'
			lbfds_files_path = f'{lbfds_files_path}/{yyyy}/'

		os.makedirs(output_path, exist_ok=1)

		with open (f'{sc_directory}/submit_{yyyy}.bash', 'w') as rsh:
			rsh.write(f'''\
#!/bin/bash -l
#SBATCH --job-name="adapt_{yyyy}"
#SBATCH --time=02:00:00
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

module load daint-gpu
module load cray-netcdf-hdf5parallel

source activate pgw-python3

srun -u python lbfd_adapt.py {yyyy} {lbfds_files_path} {output_path} {difference_files_path} {constant_variables_file} {starttimestep} {outputtimesteps} {changeyears} {recompute_pressure}

exit
''')

		subprocess.run(f'cp {script_directory}/lbfd_adapt.py {sc_directory}', shell=True)
		os.chdir(sc_directory)
		print(f'sbatch submit_{yyyy}.bash')
		subprocess.run(f'sbatch submit_{yyyy}.bash', shell=True)
