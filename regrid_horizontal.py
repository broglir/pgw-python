# -*- coding: utf-8 -*-

import xarray as xr
import xesmf as xe
import sys
from pathlib import Path

def regridhorizontal(infolder, variablename, inputtimesteps, outputgridfile, outputfolder):
	"""
	Regrid the output of the interpolate function for one variable to a different domain. Regridding will be performed using xesmf.

	Input:
	infolder: folder where the data of the target variable is located (the output of the interpolate.py)
	variablename: name of the variable to be regridded
	inputtimesteps: how many timesteps need to be regridded (corresponds to the number of files)?
	outputgridfile: a netcdf file that is in the target grid --> all input will be regridded to the grid defined in this netcdf file.
	outputfolder: path to a folder to write output. Overwriting files seems to cause problems, so it is recommended to use a new folder.

	Output: One netcdf file per timestep for the selected variable regirdded to the defined target grid.
	"""

	targetgrid = xr.open_dataset(outputgridfile)

	infile = xr.open_dataset(f"{infolder}/{variablename}00000.nc")

	regridder = xe.Regridder(infile, targetgrid, 'bilinear', reuse_weights=True)

	Path(outputfolder).mkdir(parents=True, exist_ok=True)

	for stepnum in range(inputtimesteps):
		infile = xr.open_dataset(f"{infolder}/{variablename}{stepnum:05d}.nc")
	
		outfile = regridder(infile)
		infile.close()

		outfile.to_netcdf(f"{outputfolder}/{variablename}{stepnum:05d}.nc")
		outfile.close()



if __name__ == "__main__":
	infolder=str(sys.argv[1])
	variablename=str(sys.argv[2])
	inputtimesteps=int(sys.argv[3])
	outputgridfile=str(sys.argv[4])
	outputfolder=str(sys.argv[5])
	regridhorizontal(infolder, variablename, inputtimesteps, outputgridfile, outputfolder)
