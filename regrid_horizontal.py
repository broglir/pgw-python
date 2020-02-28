# -*- coding: utf-8 -*-

import xarray as xr
import xesmf as xe
import sys

def regridhorizontal(infolder, variablename, inputtimesteps, outputgridfile, outputfolder):

	targetgrid = xr.open_dataset(outputgridfile)

	infile = xr.open_dataset(f"{infolder}/{variablename}00000.nc")

	regridder = xe.Regridder(infile, targetgrid, 'bilinear', reuse_weights=True)

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
