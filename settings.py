# -*- coding: utf-8 -*-

import subprocess


performsmooth = False
if performsmooth == True:
#settings for timesmoothing script:

	#list of the files that contain the variables to be smoothed
	samepath = '/store/c2sm/ch4/robro/surrogate_input/GCMdata/'
	annualcycleraw = [
	samepath+'hus_MPI-ESM1-2-HR_diff_ydaymean.nc',
	samepath+'huss_MPI-ESM1-2-HR_diff_ydaymean.nc',
	samepath+'psl_MPI-ESM1-2-HR_diff_ydaymean.nc',
	samepath+'ta_MPI-ESM1-2-HR_diff_ydaymean.nc',
	samepath+'tas_MPI-ESM1-2-HR_diff_ydaymean.nc',
	samepath+'ua_MPI-ESM1-2-HR_diff_ydaymean.nc',
	samepath+'uas_MPI-ESM1-2-HR_diff_ydaymean.nc',
	samepath+'va_MPI-ESM1-2-HR_diff_ydaymean.nc',
	samepath+'vas_MPI-ESM1-2-HR_diff_ydaymean.nc'
	]
	#list of variablenames
	variablename_to_smooth = ['hus', 'huss', 'psl', 'ta', 'tas', 'ua', 'uas', 'va', 'vas']
	#path to put the output netcdf
	outputpath = '/store/c2sm/ch4/robro/surrogate_input/GCMdata/smoothed/'


	#enter the command to run the script:
	for num,pathi in enumerate(annualcycleraw):
		commandsmooth = f"python timesmoothing.py {pathi} {variablename_to_smooth[num]} {outputpath} > outputfile_smooth_{variablename_to_smooth[num]}.txt &"
		subprocess.run(commandsmooth, shell=True)
		print(commandsmooth)
    

performinterp = False
if performinterp == True:
	#see documentation in interpolate.py
	samepath='/store/c2sm/ch4/robro/surrogate_input/GCMdata/smoothed/'
	
	filepathint = [
	samepath+'hus_filteredcycle.nc',
	samepath+'huss_filteredcycle.nc',
	samepath+'psl_filteredcycle.nc',
	samepath+'ta_filteredcycle.nc',
	samepath+'tas_filteredcycle.nc',
	samepath+'ua_filteredcycle.nc',
	samepath+'uas_filteredcycle.nc',
	samepath+'va_filteredcycle.nc',
	samepath+'vas_filteredcycle.nc'
	]
	variablename = ['hus', 'huss', 'psl', 'ta', 'tas', 'ua', 'uas', 'va', 'vas']
	outputtimesteps = 366 * 4
	inputfreq = 'day'
	outputpath_int = '/store/c2sm/ch4/robro/surrogate_input/GCMdata/interpolated'
    
	for numi,pathin in enumerate(filepathint):  
		commandint = f"python interpolate.py {pathin} {variablename[numi]} {outputtimesteps} {inputfreq} {outputpath_int} > outputfile_interp.txt &"
		subprocess.run(commandint, shell=True)
		print(commandint)


regridhori = True

if regridhori == True:

	infolder = '/store/c2sm/ch4/robro/surrogate_input/GCMdata/interpolated'
	variablename = 'vas'
	inputtimesteps = 4
	outputgridfile = '/scratch/snx3000/lhentge/for_pgw_atlantic/lffd2005112000c.nc'
	outputfolder = '/store/c2sm/ch4/robro/surrogate_input/GCMdata/regridded'

	comandreghor = f"python regrid_horizontal.py {infolder} {variablename} {inputtimesteps} {outputgridfile} {outputfolder}"

	print(comandreghor)
	subprocess.run(comandreghor, shell=True)

