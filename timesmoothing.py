# -*- coding: utf-8 -*-

#from settings import annualcycleraw, variablename_to_smooth, outputpath
import xarray as xr
import numpy as np
import sys
import math

def filterdata(annualcycleraw, variablename_to_smooth, outputpath):

	"""
	This function performs a temporal smoothing of an annual timeseries (typically daily resolution) using a spectral filter 
    (Bosshard et al. 2011).

	Input:
		Input 1: Path to a netcdf file of the annual cycle to be smoothed. 
        Normally this is the change in a specific variable between two simulations (e.g. warming). 
        Can be 4 or 3 dimensional, where the time is one dimension and the others are space dimensions.
		Input 2: The name of the variable within the given netcdf file
		Input 3: Path where to save the output
		
	Output:
		A netcdf file containing the smoothed annual cycle. Format: "variablename"_filteredcycle.nc
	"""	

	Diff = xr.open_dataset(annualcycleraw)[variablename_to_smooth].squeeze()
	coords = Diff.coords

	print('Dimension that is assumed to be time dimension is called: ', Diff.dims[0])
	print('shape of data: ', Diff.shape)

	Diff = Diff.data

	#create an array to store the smoothed timeseries
	#Diff_smooth=np.zeros_like(Diff, dtype=np.float32) 

	if len(Diff.shape) == 4:
		times = Diff.shape[0] 
		levels = Diff.shape[1]
		ygrids = Diff.shape[2]
		xgrids = Diff.shape[3]
	elif len(Diff.shape) == 3:
		times = Diff.shape[0]
		ygrids = Diff.shape[1]
		xgrids = Diff.shape[2]
		levels = 0
	else:
		sys.exit('Wrog dimensions of input file should be 3 or 4-D')


	if len(Diff.shape) == 4:
		for i in range(levels): #loop over levels to smooth the timeseries on every level
			for yy in range(ygrids):
				for xx in range(xgrids):	
					Diff[:,i,yy,xx] = harmonic_ac_analysis(Diff[:,i,yy,xx]) #reconstruct the smoothed timeseries using function below



	if len(Diff.shape) == 3:		
		for yy in range(ygrids):
			for xx in range(xgrids):	
				Diff[:,yy,xx] = harmonic_ac_analysis(Diff[:,yy,xx]) #dump the smoothed timeseries in the array on the original level
			

	print('Done with smoothing')

	#del Diff

	Diff = xr.DataArray(Diff, coords=coords, name=variablename_to_smooth)
	Diff.to_netcdf(outputpath+'/'+variablename_to_smooth+'_filteredcycle.nc', mode='w')

	print('saved file '+outputpath+'/'+variablename_to_smooth+'_filteredcycle.nc')


def harmonic_ac_analysis(ts):
	"""
	Estimation of the harmonics according to formula 12.19 -
	12.23 on p. 264 in Storch & Zwiers

	Is incomplete since it is only for use in surrogate smoothing --> only the part of the formulas that is needed there

	Arguments:
		ts: a 1-d numpy array of a timeseries

	Returns:
		hcts: a reconstructed smoothed timeseries (the more modes are summed the less smoothing)
		mean: the mean of the timeseries (needed for reconstruction)
	"""
	
	if np.any(np.isnan(ts) == True): #abort if there are nans
		sys.exit('There are nan values')
	
	mean = ts.mean() #calculate the mean of the timeseries (used for reconstruction)
	
	lt = len(ts) #how long is the timeseries?
	P = lt

	#initialize the output array. we will use at max 4 modes for reconstruction (for peformance reasons, it can be increased)
	hcts = np.zeros((4,lt))

	timevector=np.arange(1,lt+1,1)	#timesteps used in calculation	

	q = math.floor(P/2.) #a measure that is to check that the performed calculation is justified.
	
	for i in range(1,4): #create the reconstruction timeseries, mode by mode (starting at 1 until 5, if one wants more smoothing this number can be increased.)
		if i < q: #only if this is true the calculation is valid
			
			#these are the formulas from Storch & Zwiers
			bracket = 2.*math.pi*i/P*timevector
			a = 2./lt*(ts.dot(np.cos(bracket))) #careful with multiplications of vectors (ts and timevector)..
			b = 2./lt*(ts.dot(np.sin(bracket))) #dot product (Skalarprodukt) for scalar number output!
				
			hcts[i-1,:] = a * np.cos(bracket) + b * np.sin(bracket) #calculate the reconstruction time series
			
		else: #abort if the above condition is not fulfilled. In this case more programming is needed.
			sys.exit('Whooops that should not be the case for a yearly timeseries! i (reconstruction grade) is larger than the number of timeseries elements / 2.')

	smooths = sum(hcts[0:3,:]) + mean
	return smooths


if __name__ == "__main__":
	annualcycleraw = str(sys.argv[1])
	variablename_to_smooth = str(sys.argv[2])
	outputpath = str(sys.argv[3])
	filterdata(annualcycleraw, variablename_to_smooth, outputpath)


