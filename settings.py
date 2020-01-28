# -*- coding: utf-8 -*-

import subprocess

#should change in specific humidity be computed from relative humidity?
calhumidity = True

# settings for humidity routine. See documentation in humidity_difference_via_RH.py
if calhumidity == True:
	
	humidity_hist_path = '/home/broglir/polybox/pgw-python/RELHUM_CT_Part.nc'
	pressure_hist_path = '/home/broglir/polybox/pgw-python/P_CT_Part.nc'
	temperature_hist_path =  '/home/broglir/polybox/pgw-python/T_CT_Part.nc'

	humidity_future_path = '/home/broglir/polybox/pgw-python/RELHUM_SC_Part.nc'
	pressure_future_path = '/home/broglir/polybox/pgw-python/P_SC_Part.nc'
	temperature_future_path = '/home/broglir/polybox/pgw-python/T_SC_Part.nc'

	savename = '/home/broglir/polybox/pgw-python/spec_hum_diff.nc'

	humidityname='RELHUM'
	pressurename='P'
	temperaturename='T'
	savevariablename = 'QV'

	commandhum = f"python humidity_difference_via_RH.py {humidity_hist_path} {pressure_hist_path} {temperature_hist_path} {humidity_future_path} {pressure_future_path} {temperature_future_path} {savename} {humidityname} {pressurename} {temperaturename} {savevariablename} > outfile_calhum.txt &"
	subprocess.run(commandhum, shell=True)
	print(commandhum)


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
    

performinterp = False
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


