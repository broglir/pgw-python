# -*- coding: utf-8 -*-

import subprocess
import os

performsmooth = False
if performsmooth == True:
#settings for timesmoothing script:

	#list of the files that contain the variables to be smoothed
	samepath = '/project/pr04/robro/inputfiles_for_surrogate_hadgem/input_github/'
	annualcycleraw = [
	samepath+'Diff_HadGEM2-ES_RCP85_PP.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_QV.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_QV_S.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_T.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_T_S.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_T_SO.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_U.nc',
	samepath+'Diff_HadGEM2-ES_RCP85_V.nc'
	]
	#list of variablenames
	variablename_to_smooth = ['PP', 'QV', 'QV_S', 'T', 'T_S', 'T_SO', 'U', 'V']
	#path to put the output netcdf
	outputpath = '/scratch/snx3000/robro/pgwtemp/smoothed/'


	#enter the command to run the script:
	for num,pathi in enumerate(annualcycleraw):
		commandsmooth = f"python timesmoothing.py {pathi} {variablename_to_smooth[num]} {outputpath} > outputfile_smooth_{variablename_to_smooth[num]}.txt &"
		subprocess.run(commandsmooth, shell=True)
		print(commandsmooth)
    

performinterp = True
if performinterp == True:
	#see documentation in interpolate.py
	samepath='/scratch/snx3000/robro/pgwtemp/smoothed/'
	
	filepathint = [
	samepath+'PP_filteredcycle.nc',
	samepath+'QV_filteredcycle.nc',
	samepath+'QV_S_filteredcycle.nc',
	samepath+'T_filteredcycle.nc',
	samepath+'T_S_filteredcycle.nc',
	samepath+'T_SO_filteredcycle.nc',
	samepath+'U_filteredcycle.nc',
	samepath+'V_filteredcycle.nc',
	]
	variablename = ['PP', 'QV', 'QV_S', 'T', 'T_S', 'T_SO', 'U', 'V']
	outputtimesteps = 360 * 4
	inputfreq = 'day'
	outputpath_int = '/scratch/snx3000/robro/pgwtemp/interpolated/'
    
	for numi,pathin in enumerate(filepathint):  
		commandint = f"python interpolate.py {pathin} {variablename[numi]} {outputtimesteps} {inputfreq} {outputpath_int} > outputfile_interp.txt &"
		subprocess.run(commandint, shell=True)
		print(commandint)


regridhori = False

if regridhori == True:

	infolder = '/store/c2sm/ch4/robro/surrogate_input/GCMdata/interpolated'
	variablename = ['hus', 'huss', 'psl', 'ta', 'tas', 'ua', 'uas', 'va', 'vas']
	inputtimesteps = 4 * 366
	outputgridfile = '/scratch/snx3000/lhentge/for_pgw_atlantic/lffd2005112000c.nc'
	outputfolder = '/store/c2sm/ch4/robro/surrogate_input/GCMdata/regridded'

	for variable in variablename:
		#get the python command and write a file to submit to the piz daint machine
		comandreghor = f"python regrid_horizontal.py {infolder} {variable} {inputtimesteps} {outputgridfile} {outputfolder} > out_regrid.txt &" 

		subprocess.run(comandreghor, shell=True)



#this part is software/hardware specific for the piz daint supercomputer on CSCS
regridvert = False

if regridvert == True:

	terrainpath = '/scratch/snx3000/lhentge/for_pgw_atlantic/lffd2005112000c.nc'
	datapath = '/scratch/snx3000/robro/regridded/regridded/'
	variablename = ['hus','ta','ua','va']
	outvar = ['QV', 'T', 'U', 'V']
	outputpath = '/scratch/snx3000/robro/regridded/final_try2/'
	vcflat = 11357 #height where modellevels become flat
	inputtimesteps = 4 * 366
	steps_per_job = 150 #split the job into multiple chucks and run in paralell
	starttime = 0

	for variable, outv in zip(variablename, outvar):
		for start in range(starttime, inputtimesteps, steps_per_job):
			end_job = start + steps_per_job
			comandregver = f"srun -u python cclm_vertical.py {terrainpath} {datapath} {variable} {outv} {outputpath} {vcflat} {end_job} {start}"

			print(comandregver)
		
			#create a run script for afew timesteps and each variable. 
			with open (f'/scratch/snx3000/robro/regridded/submit_{variable}.bash', 'w') as rsh:
				rsh.write(f'''\
#!/bin/bash -l
#SBATCH --job-name="reg_{variable}_{start}"
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

{comandregver}

exit
''')
#submit the slurm batch job script from the scratch directory
			os.chdir('/scratch/snx3000/robro/regridded/')
			subprocess.run('cp /project/pr04/robro/pgw-python/cclm_vertical.py /scratch/snx3000/robro/regridded/', shell=True)
			subprocess.run(f'sbatch submit_{variable}.bash', shell=True)
