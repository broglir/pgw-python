# -*- coding: utf-8 -*-

import subprocess
import os

performsmooth = False
if performsmooth == True:
#settings for timesmoothing script:

	#list of the files that contain the variables to be smoothed
	samepath = '/project/pr94/robro/inputfiles_for_surrogate_hadgem/input_github/'
	annualcycleraw = [
	samepath+'Diff_HadGEM2-ES_RCP85_PP.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_QV.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_QV_S.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_T.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_T_S.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_T_SO.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_U.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_V.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_RELHUM.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_RELHUM_S.nc'
	]
	#list of variablenames
	variablename_to_smooth = ['PP', 'QV', 'QV_S', 'T', 'T_S', 'T_SO', 'U', 'V','RELHUM','RELHUM_S']
	#path to put the output netcdf
	outputpath = '/scratch/snx3000/robro/pgwtemp/smoothed/'


	#enter the command to run the script:
	for num,pathi in enumerate(annualcycleraw):
		commandsmooth = f"python timesmoothing.py {pathi} {variablename_to_smooth[num]} {outputpath} > outputfile_smooth.txt &"
		subprocess.run(commandsmooth, shell=True)
		print(commandsmooth)
    

performinterp = False
if performinterp == True:
	#see documentation in interpolate.py
	samepath='/scratch/snx3000/robro/pgwtemp/'
	
	filepathint = [
	samepath+'diff_hur.nc',
	samepath+'diff_hurs.nc',
	samepath+'diff_ta.nc',
	samepath+'diff_tas.nc',
	samepath+'diff_ua.nc',
	samepath+'diff_va.nc',
	]
	variablename = ['hur', 'hurs', 'ta', 'tas', 'ua', 'va']
	
	outputtimesteps = 366 * 4
	inputfreq = 'month'
	outputpath_int = '/scratch/snx3000/robro/pgwtemp/interpolated/'
    
	for numi,pathin in enumerate(filepathint):  
		commandint = f"python interpolate.py {pathin} {variablename[numi]} {outputtimesteps} {inputfreq} {outputpath_int}"
		print(commandint)
		subprocess.run(commandint, shell=True)


regridhori = False

if regridhori == True:

	infolder = '/scratch/snx3000/robro/pgwtemp/interpolated/'
	variablename = ['hur', 'hurs', 'ta', 'tas', 'ua', 'va']
	inputtimesteps = 4 * 366
	outputgridfile = '/store/c2sm/ch4/robro/surrogate_input/lffd2005112000c.nc'
	outputfolder = '/scratch/snx3000/robro/pgwtemp/regridded/'
    
	#option to run directly
	for variable in variablename:
		#get the python command and write a file to submit to the piz daint machine
		comandreghor = f"python regrid_horizontal.py {infolder} {variable} {inputtimesteps} {outputgridfile} {outputfolder} > out_regrid.txt &" 
		subprocess.run(comandreghor, shell=True)
		
	
	## for efficient parallelization one can run this function also in jupyterlab at cscs if a kernel with all pyton modules is available
	## first in the console run seperately
	## from dask.distributed import Client
	## client = Client(n_workers=6) #one worker per variable
	
	##uncomment the following and run settings.py after the client is initialized
	#from regrid_horizontal import regridhorizontal
	#from distributed.diagnostics.plugin import UploadFile
	#from dask import delayed
	#import os
	#import dask
	#tasks=[]
	#wordir=os.getcwd()
	
	#for variable in variablename:
		#temp = delayed(regridhorizontal)(infolder, variable, inputtimesteps, outputgridfile, outputfolder)
		#tasks.append(temp)
	
	##run this in console after settings.py
	#client.register_worker_plugin(UploadFile(wordir+"/regrid_horizontal.py")) 
	#err = dask.compute(*tasks) #this will distribute the computation to the workers



#this part is software/hardware specific for the piz daint supercomputer on CSCS
regridvert = False

if regridvert == True:

	#note that it it advised to create a height.txt (see example in repository)
	terrainpath = '/store/c2sm/ch4/robro/surrogate_input/lffd2005112000c.nc'
	datapath = '/scratch/snx3000/robro/pgwtemp/regridded/'
	variablename = ['hur','ta','ua','va']
	outvar = ['RELHUM', 'T', 'U', 'V']
	outputpath = '/scratch/snx3000/robro/pgwtemp/final2/'
	vcflat = 11357 #height where modellevels become flat
	inputtimesteps = 4 * 366
	steps_per_job = 1000 #split the job into multiple chucks and run in paralell
	starttime = 0

	for variable, outv in zip(variablename, outvar):
		for start in range(starttime, inputtimesteps, steps_per_job):
			end_job = start + steps_per_job
			comandregver = f"srun -u python cclm_vertical.py {terrainpath} {datapath} {variable} {outv} {outputpath} {vcflat} {end_job} {start}"

			print(comandregver)
		
			#create a run script for afew timesteps and each variable. 
			with open (f'/scratch/snx3000/robro/pgwtemp/pgw-python/submit_{variable}.bash', 'w') as rsh:
				rsh.write(f'''\
#!/bin/bash -l
#SBATCH --job-name="reg_{variable}_{start}"
#SBATCH --time=05:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --partition=normal
#SBATCH --constraint=gpu
#SBATCH --hint=nomultithread
#SBATCH --account=pr94

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

set -ex

module load daint-gpu
module load cray-netcdf-hdf5parallel

source activate pgw-python3

{comandregver}

exit
''')
#submit the slurm batch job script from the scratch directory (change directory if needed)
			#os.chdir('/scratch/snx3000/robro/pgwtemp/regridded/')
			#subprocess.run('cp /project/pr04/robro/pgw-python/cclm_vertical.py /scratch/snx3000/robro/regridded/', shell=True)
			subprocess.run(f'sbatch submit_{variable}.bash', shell=True)
