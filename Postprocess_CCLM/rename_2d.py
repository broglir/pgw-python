import xarray as xr
import sys
"""
Script to rename variables if necessary; specific to COSMO-CLM
"""

oldpath='/scratch/snx3000/robro/regridded/regridded/'
newpath='/scratch/snx3000/robro/regridded/final_try2/'

variable=str(sys.argv[1])
newvariable=str(sys.argv[2])

for i in range(366 * 4):
	old = xr.open_dataset(f"{oldpath}/{variable}{i:05d}.nc")
	old = old.rename({variable:newvariable})
	old.to_netcdf(f"{newpath}/{newvariable}{i:05d}.nc")
