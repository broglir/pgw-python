# -*- coding: utf-8 -*-

import xarray as xr
import sys
import numpy as np
from pathlib import Path

def interpannualcycle(filepath, variablename, outputtimesteps, inputfreq, outputpath='./'):
	"""
	Interpolate temporally an annual cyle with sparse data points linearly to higher time frequencies.
	This can be used to interpolate a daily or monthly resolution annual cycle to the
	 frequency that is used to update. 
	The file has to contain the climate change signal to add it later  ex. future-present)
	the boundary conditions in a model.

	Input:
	filepath: Path to a netcdf file of the annual cycle of the signal to be interpolated.  
	variablename: The name of the variable within the given netcdf file which will be interpolated.
	outputtimesteps: Amount of thimesteps needed as output (e.g. 366 * 4 for output every 6 hours in a gregorian calendar)
	inputfreq: Either 'day' or 'month': Frequency of the input annual cycle, either daily or monthly averages.
	outputpath: path to a folder to put the output netcdf files. Defaults to the current folder, yet due to the amount of 
	output a separate folder is advisable.
		
	Output:
	Multiple netcdf files! One netcdf file per output timestep. They are numbered upwards from 0,
	starting at the beginning of the year and increasing by 1 for each time step. Format variablenameNNNNN.nc,
	where NNNNN is the number of the timestep (e.g. ta00432.nc; for timestep number 432 and a variable called ta).
	"""

	#open the inputfile and variable
	infile = xr.open_dataset(filepath)[variablename].squeeze()

	#enumerate the time steps for easyier interpolation
	timesteps = len(infile['time'])
	infile['time'] = np.arange(timesteps)

	#create the new time steps if daily inputdata is given (no special treatment necessary)
	if inputfreq == 'day':
		tnew = np.linspace(0, timesteps-1, num=outputtimesteps)

	#create new time steps with monthly data (shift the montly means to the end of the month and add a dublicate the first time step)
	if inputfreq == 'month':
		tnew = np.linspace(0, timesteps, num=outputtimesteps)

		jan = (infile[0] + infile[-1]) / 2.
		rest = (infile.data[0:-1] + infile.data[1:]) / 2.

		#fill in the appropriate data for the end of the month
		infile.data[0] = jan.data
		infile.data[1:] = rest

		#concat the january data to the end of the timeseries
		jan['time'] = infile['time'][-1] + 1
		infile = xr.concat([infile,jan], dim='time')


	#interpolate new output timesteps
	outfile = infile.interp(time=tnew, method='linear', assume_sorted=True)
	del infile

	#numerate outputtimesteps
	outfile['time'] = np.arange(outputtimesteps)

	#save each output timestep in a seperate netcdf file for easyier handling later on
	Path(outputpath).mkdir(parents=True, exist_ok=True)
	for filenum in range(outputtimesteps):
		outfile[filenum].to_netcdf(f"{outputpath}/{variablename}{filenum:05d}.nc", mode='w')       

                
if __name__ == "__main__":
	filepath = str(sys.argv[1])
	variablename = str(sys.argv[2])
	outputtimesteps = int(sys.argv[3])
	inputfreq = str(sys.argv[4])
	outputpath = str(sys.argv[5])
	interpannualcycle(filepath, variablename, outputtimesteps, inputfreq, outputpath)
