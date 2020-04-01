import xarray as xr
import sys
import os
import glob

"""
Add the calculated difference in all necessary variables to the boundary condition (lbfd) files for one year. This should be run on a cluster. This script will only work when data for all year is present!

Input:
	year (comandline argument): The year for which the boundary files should be adapted. The year refers to the year in the original output from int2lm.
	lbfdpath: path to directory where boundary files are saved
	changeyears: amount of years to be added to timestamp of data
	outputpath: path to put the adapted bondary files
	Diffspath: Where to find the changes (climate change deltas) to add to the boundary files. This is the ouput of earlier scripts in this repository (i.e. T00000.nc, T00001.nc etc.).
	difftimesteps: Amount of timesteps (or boundary data fields) in one year

Output:
	For every boundary file in the inputdata, a corresponding output field will be written to the path specified as outputpath.
"""

year = int(sys.argv[1]) 
#The year (in original data) which should be processed should be passed as command line argument
lbfdpath = f'/scratch/snx3000/robro/int2lm/HadGEM/driving_historical/{year}/'

changeyears = 100
newyear = year + changeyears
outputpath = f'/scratch/snx3000/robro/int2lm/HadGEM/PGW_TEST/{newyear}/'

Diffspath = '/scratch/snx3000/robro/pgwtemp/interpolated/'
difftimesteps = 360 * 4

def lbfdadapt(lbfdpath, outputpath, Diffspath, difftimesteps, changeyears):
	
	#get a list of all lbfd files:
	os.chdir(lbfdpath)
	files = glob.glob('lbfd??????????.nc')
	files.sort()

	#if output directory doesn't exist create it
	if os.path.isdir(outputpath) == False:
		os.makedirs(outputpath)

	#loop over all boundary fields:
	for num,lbfdnum in enumerate(files):
		#print and open boundary data
		print(num, lbfdnum)
		lbfd = xr.open_dataset(lbfdnum, decode_cf=False)

		#if there is a file for the next year in the folder use first timestep; print to check
		if num >= difftimesteps:
			num = 0
			print(f'used first delta for {lbfdnum}')

		#add all variables to the boundary field (use given timestep)
		def diffadd(var, lbfd=lbfd):
			Diff = xr.open_dataset(f'{Diffspath}/{var}{num:05d}.nc')[var]
			lbfd[var].data = lbfd[var].data + Diff.data.astype('float32')

		variables = ['PP','QV','QV_S', 'T', 'T_S', 'U', 'V']

		for var in variables:
			diffadd(var, lbfd)
	
		#change time to future
		endtimestring = lbfd.time.units[-15:]
		old_yyyy_timestamp = int(lbfd.time.units[-19:-15])
		new_yyyy_timestamp = old_yyyy_timestamp + changeyears
		lbfd.time.attrs['units'] = f'seconds since {new_yyyy_timestamp}{endtimestring}'

		endpart = lbfdnum[-9:]
		lbfdyear = int(lbfdnum[4:8])
		lbfdyear = lbfdyear + changeyears
		lbfd.to_netcdf(f'{outputpath}/lbfd{lbfdyear}{endpart}')
		lbfd.close()

lbfdadapt(lbfdpath, outputpath, Diffspath, difftimesteps, changeyears)
