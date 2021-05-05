# -*- coding: utf-8 -*-

import xarray as xr
import sys
import numpy as np
from pathlib import Path
import gc
import dask

def interpannualcycle(filepath, variablename, outputtimesteps, inputfreq, outputpath='./'):
	"""
	Interpolate temporally an annual cyle with sparse data points linearly to higher time frequencies.
	This can be used to interpolate a daily or monthly resolution annual cycle to the
	 frequency that is used to update the boundary conditions. 

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


	#if len(infile.shape) > 3:
		#infile = infile.chunk({'plev':1})	
	#interpolate new output timesteps
	outfile = infile.interp(time=tnew, method='linear', assume_sorted=True)#.chunk({'time':1})
	infile.close()
	del infile
	gc.collect()

	#numerate outputtimesteps
	outfile['time'] = np.arange(outputtimesteps)

	#save each output timestep in a seperate netcdf file for easyier handling later on
	Path(outputpath).mkdir(parents=True, exist_ok=True)
	for filenum in range(outputtimesteps):
		outfile[filenum].to_netcdf(f"{outputpath}/{variablename}{filenum:05d}.nc", mode='w')       

	outfile.close()
	del outfile
	gc.collect()



def interpannualcycle_dask(filepath, variablename, outputtimesteps, inputfreq, outputpath, threads_per_task):
	"""
	Dublication of function above but using dask arrays instead of numpy arrays.
	If memory problems occur with the original function, this can be used instead.
	
	An additional setting is the amount of threads per task, which will be used for paralell saving of 
	netcdf files.
	"""

	#open the inputfile and variable
	infile = xr.open_dataset(filepath, chunks={'lat':1})[variablename].squeeze()

	#enumerate the time steps for easyier interpolation
	timesteps = len(infile['time'])
	infile['time'] = np.arange(timesteps)

	#create the new time steps if daily inputdata is given (no special treatment necessary)
	if inputfreq == 'day':
		tnew = np.linspace(0, timesteps-1, num=outputtimesteps)

#create new time steps with monthly data (shift the montly means to the end of the month and add a dublicate the first time step)
	if inputfreq == 'month':
		tnew = np.linspace(0, timesteps, num=outputtimesteps)

		jan = 0.5*(infile[0] + infile[-1])
		first = infile[:-1, ...]
		second = infile[1:, ...]
		first['time'] = second['time'] #metadata must match for xarray computation. Dangerous thing...
    
		rest = 0.5*(first + second)
		end = jan.copy()
    
		jan['time'] = rest['time'][0] - 1
		end['time'] = rest['time'][-1] + 1
    
		infile = xr.concat([jan,rest,end], dim='time').transpose('time', ...).chunk({'time':13})

	outfile = infile.interp(time=tnew, method='linear', assume_sorted=True)
	infile.close()

	#numerate outputtimesteps
	outfile['time'] = np.arange(outputtimesteps)
	outfile = outfile.chunk({'time':1, 'lat':-1})
	
	#save each output timestep in a seperate netcdf file for easyier handling later on
	Path(outputpath).mkdir(parents=True, exist_ok=True)
	
	#within processes allow paralell io
	threadsteps = threads_per_task
	for large_file_num in range(0,outputtimesteps,threadsteps):
		compute_list = []
		for small_file_num in range(large_file_num,large_file_num+threadsteps,1):
			compute_list.append(outfile[small_file_num].to_netcdf(f"{outputpath}/{variablename}{small_file_num:05d}.nc", mode='w', compute=False))
		dask.compute(*compute_list, scheduler='threads')
                
if __name__ == "__main__":
	filepath = str(sys.argv[1])
	variablename = str(sys.argv[2])
	outputtimesteps = int(sys.argv[3])
	inputfreq = str(sys.argv[4])
	outputpath = str(sys.argv[5])
	interpannualcycle(filepath, variablename, outputtimesteps, inputfreq, outputpath)
