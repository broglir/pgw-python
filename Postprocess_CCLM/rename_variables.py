import xarray as xr
import sys
"""
Script to rename variables if necessary; specific to COSMO-CLM
"""


outputtimesteps = 4 * 366
oldpath='/scratch/snx3000/jvergara/PGW/full_interpolation/'
newpath='/scratch/snx3000/robro/regridded/final_try2/'

variable=str(sys.argv[1])
newvariable=str(sys.argv[2])

if len(sys.argv[:])>4:
	#Reading paths from command line
	oldpath=str(sys.argv[3])
	newpath=str(sys.argv[4])
	outputtimesteps=int(sys.argv[5])

for i in range(outputtimesteps):
	old = xr.open_dataset(f"{oldpath}/{variable}{i:05d}.nc")
	old = old.rename({variable:newvariable})
	old.to_netcdf(f"{newpath}/{newvariable}{i:05d}.nc")
