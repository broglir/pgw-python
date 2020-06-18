"""
To prevent CCLM from crashing it can be necessary to have boundary data for the day after the simulation ends. This script can be used as a dirty fix for that. This must be the last step in postprocessing.
"""

import xarray as xr
import subprocess
from pathlib import Path

#the last file that has been created by the lbfd_adapt.py script
lastfilepath = '/scratch/snx3000/robro/int2lm/HadGEM/PGW_TEST/2100/lbfd2101010100.nc'

newyearpath = '/scratch/snx3000/robro/int2lm/HadGEM/PGW_TEST/2101'
newfiles = ['lbfd2101010100.nc', 'lbfd2101010106.nc', 'lbfd2101010112.nc']

Path(newyearpath).mkdir(parents=True, exist_ok=True)

for nc in newfiles:
	subprocess.run(f'cp {lastfilepath} {newyearpath}/{nc}_temp', shell=True)

	newfile = xr.open_dataset(f'{newyearpath}/{nc}_temp', decode_cf=False)
	year = nc[4:8]
	month = nc[8:10]
	day = nc[10:12]
	hour = nc[12:14]

	string = f'seconds since {year}-{month}-{day} {hour}:00:00'

	newfile.time.attrs['units'] = string
	newfile['time'].data[0] = 0
	newfile['time_bnds'].data[0][0] = 0
	newfile['time_bnds'].data[0][1] = 0

	newfile.to_netcdf(f'{newyearpath}/{nc}')
	print(f'saved {nc}')

	subprocess.run(f'rm {newyearpath}/{nc}_temp', shell=True)
