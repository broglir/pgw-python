import xarray as xr
import sys

"""
Can be used to add the calculated difference in all necessary variables to the initial condition (laf) file. This very fast, just run it in the console.

Input:
lafpath: Path to the original laf-file from the "base" simulation (e.g. reanalysis driven or historical simulation). The name of the laf file must be as outputted by int2lm (e.g. laf1970010100.nc ).
newyear: What year to use in the files (change it to the future to adapt CO2 levels)
outputpath: In which folder should the adapted laf file be put (probably the same as the adapted boudary or lbfd files) 
Diffspath: Where is the input located, i.e. the single files that have been previously produced by the interpolate.py routie or the regridding routines. These are the files called for example T00000.nc
"""

lafpath = '/scratch/snx3000/robro/int2lm/HadGEM/driving_historical/laf1970010100.nc'
newyear = 2070
outputpath = '/scratch/snx3000/robro/int2lm/HadGEM/PGW_TEST/2070/'
Diffspath = '/scratch/snx3000/robro/pgwtemp/interpolated/'

def lafadapt(lafpath, newyear, outputpath, Diffspath):

	laffile = xr.open_dataset(lafpath, decode_cf=False)

	def diffadd(var, laffile=laffile):
		Diff = xr.open_dataset(f'{Diffspath}/{var}00000.nc')[var]
		laffile[var].data = laffile[var].data + Diff.data.astype('float32')

	variables = ['PP','QV','QV_S', 'T', 'T_S', 'T_SO', 'U', 'V']

	for var in variables:
		diffadd(var, laffile)
	
	endtimestring = laffile.time.units[-15:]
	laffile.time.attrs['units'] = f'seconds since {newyear}{endtimestring}'

	endpartlaf = lafpath[-9:] 
	laffile.to_netcdf(f'{outputpath}/laf{newyear}{endpartlaf}')
	laffile.close()

lafadapt(lafpath, newyear, outputpath, Diffspath)
