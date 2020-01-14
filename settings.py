# -*- coding: utf-8 -*-

import subprocess

performsmooth = False
if performsmooth == True:
#settings for timesmoothing script:

	#list of the files that contain the variables to be smoothed
	annualcycleraw = '/home/broglir/polybox/python_pgw/diff_ydaymean_T_2M.nc'
	#list of variablenames
	variablename_to_smooth = 'T_2M'
	#path to put the output netcdf
	outputpath = '/home/broglir/polybox/python_pgw/'


	#enter the command to run the script:
	commandsmooth = f"python timesmoothing.py {annualcycleraw} {variablename_to_smooth} {outputpath} > outputfile_smooth.txt &"
	subprocess.run(commandsmooth, shell=True)
	print(commandsmooth)
    

performinterp = True
if performinterp == True:
	#see documentation in interpolate.py
	filepathint = '/Users/roman/polybox/python_pgw/T_2M_flteredcycle.nc'
	variablename = 'T_2M'
	outputtimesteps = 360 * 4
	inputfreq = 'day'
	outputpath_int = '/lhome/broglir/netcdf/to_delete'
    
    
	commandint = f"python interpolate.py {filepathint} {variablename} {outputtimesteps} {inputfreq} {outputpath_int} > outputfile_interp.txt &"
	subprocess.run(commandint, shell=True)
	print(commandint)


