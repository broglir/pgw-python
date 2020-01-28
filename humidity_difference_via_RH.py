# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import sys


def cal_humiditydiff(humidity_hist_path, pressure_hist_path, temperature_hist_path, humidity_future_path, pressure_future_path, temperature_future_path, savename, humidityname, pressurename, temperaturename, savevariablename):
	"""
	Difference in specific humidity from the difference in relative humidity. This potentially avoids aritificial drying of fields in used in for boundary conditions. Unfortunately, a lot of input is needed for this routine.

	Input:
	Positional arguments:
	humidity_hist_path: path to historical relative humidity netcdf (typically mean annual cycle; can be defined between 0-100 or 0-1)
	pressure_hist_path: path to historical pressure netcdf of same shape as humidity in Pa
	temperature_hist_path: path to historical temperature netcdf of same shape as humidity in K
	humidity_future_path: path to future relative humidity netcdf (0-100 or 0-1)
	pressure_future_path: path to future pressure netcdf (Pa)
	temerature_future_path: path to future temperature netcdf (K)
	savename: Name of the output specific humidity difference netcdf with path if necessary.
	humidityname: name of the humidity variable in the netcdf file
	pressurename: name of pressure variable
	temperaturename: name of temperature variable
	savevariablename: name of the variable to be saved in output
		
	Output:
	One netcdf file of the same shape as input containing the difference in specific humidity between the periods of the input. Unit is kg/kg. Can be further processed using other files in this repository (e.g. smoothing or interpolation)
	"""

	hum_hist = xr.open_dataset(humidity_hist_path)[humidityname]
	p_hist = xr.open_dataset(pressure_hist_path)[pressurename]
	T_hist  = xr.open_dataset(temperature_hist_path)[temperaturename]

	hum_fut = xr.open_dataset(humidity_future_path)[humidityname]
	p_fut = xr.open_dataset(pressure_future_path)[pressurename]
	T_fut = xr.open_dataset(temperature_future_path)[temperaturename]

	#convert relative humidity to right values for use in formula if rh is defined between 0-1
	if hum_hist.max() < 4:
		hum_hist = hum_hist * 100.
		hum_fut = hum_fut * 100.

	spec_hum_hist = (hum_hist.data * np.exp(17.67*(T_hist.data - 273.15)/(T_hist.data-29.65))) / ( 0.263 * p_hist.data)
	spec_hum_fut  = (hum_fut.data  * np.exp(17.67*(T_fut.data  - 273.15)/(T_fut.data -29.65))) / ( 0.263 * p_fut.data)

	spec_hum_diff = spec_hum_fut - spec_hum_hist
	spec_hum_diff = xr.DataArray(data=spec_hum_diff, dims=hum_hist.dims, coords=hum_hist.coords, name=savevariablename)   

	spec_hum_diff = spec_hum_diff.astype('float32')
	spec_hum_diff = spec_hum_diff.to_dataset(name=savevariablename)
	spec_hum_diff.to_netcdf(savename)

	print(f'saved {savename}')


if __name__ == "__main__":
	humidity_hist_path = str(sys.argv[1])
	pressure_hist_path = str(sys.argv[2])
	temperature_hist_path = str(sys.argv[3])
	humidity_future_path = str(sys.argv[4])
	pressure_future_path = str(sys.argv[5])
	temperature_future_path = str(sys.argv[6])
	savename = str(sys.argv[7])
	humidityname = str(sys.argv[8])
	pressurename = str(sys.argv[9])
	temperaturename = str(sys.argv[10])
	savevariablename = str(sys.argv[11])
	cal_humiditydiff(humidity_hist_path, pressure_hist_path, temperature_hist_path, humidity_future_path, pressure_future_path, temperature_future_path, savename, humidityname, pressurename, temperaturename, savevariablename)
