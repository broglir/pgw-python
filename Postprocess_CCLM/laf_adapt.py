import xarray as xr
import sys
import os

"""
Can be used to add the calculated difference in all necessary variables to the initial condition (laf) file. This very fast, just run it in the console.

Input:
	lafpath: Path to the original laf-file from the "base" simulation (e.g. reanalysis driven or historical simulation). The name of the laf file must be as outputted by int2lm (e.g. laf1970010100.nc ).
	newyear: What year to use in the files (change it to the future to adapt CO2 levels)
	laftimestep: Which timestep within the annual cycle is apropriate to adapt the laf file? (0 for beginning of year)
	newtimestring: What timestamp should be used for the adapted laf file? Put the exact time of the new laf file in the format 'seconds since yyyy-mm-dd hh:mm:ss'
	outputpath: In which folder should the adapted laf file be put (probably the same as the adapted boudary or lbfd files) 
	Diffspath: Where is the input located, i.e. the single files that have been previously produced by the interpolate.py routie or the regridding routines. These are the files called for example T00000.nc

Output:
	The adapted laf file will be written to the chosen location and should directly be usable for CCLM.
"""

lafpath = '/scratch/snx3000/robro/int2lm/HadGEM/driving_historical/laf1970010100.nc'
newyear = 2070
laftimestep = 0
newtimestring = 'seconds since 2070-01-01 00:00:00'
outputpath = '/scratch/snx3000/robro/int2lm/HadGEM/PGW_TEST/2070/'
Diffspath = '/scratch/snx3000/robro/pgwtemp/interpolated/'

def lafadapt(lafpath, newyear, outputpath, Diffspath, laftimestep, newtimestring):

	laffile = xr.open_dataset(lafpath, decode_cf=False)

	#if output directory doesn't exist create it
	if os.path.isdir(outputpath) == False:
		os.makedirs(outputpath)

	def diffadd(var, laffile=laffile):
		Diff = xr.open_dataset(f'{Diffspath}/{var}{laftimestep:05d}.nc')[var]
		laffile[var].data = laffile[var].data + Diff.data.astype('float32')

	variables = ['PP','QV','QV_S', 'T', 'T_S', 'T_SO', 'U', 'V']

	for var in variables:
		diffadd(var, laffile)
	
	laffile.time.attrs['units'] = newtimestring
	laffile['time'].data[0] = 0 

	endpartlaf = lafpath[-9:] 
	
	laffile.to_netcdf(f'{outputpath}/laf{newyear}{endpartlaf}')
	laffile.close()

lafadapt(lafpath, newyear, outputpath, Diffspath, laftimestep, newtimestring)
