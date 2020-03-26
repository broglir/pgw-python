# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import sys

"""
	Difference in specific humidity from the difference in relative humidity. This potentially avoids aritificial drying of fields in used in for boundary conditions. Unfortunately, a lot of input is needed for this routine, which is fixcoded for simplicity...
	
	Input:
	humidity_hist_path: path to historical relative humidity netcdf (3D field) (typically mean annual cycle; can be defined between 0-100 or 0-1)
	pressure_hist_path: path to historical pressure netcdf of same shape as humidity in Pa (3D)
	temperature_hist_path: path to historical temperature netcdf of same shape as humidity in K (3D)
	humidity_future_path: path to future relative humidity netcdf (0-100 or 0-1; 3D) 
	pressure_future_path: path to future pressure netcdf (Pa; 3D)
	temerature_future_path: path to future temperature netcdf (K; 3D)
	savename: Name of the output atmospheric (3D) specific humidity difference netcdf with path if necessary.
	humidityname: name of the atmospheric humidity variable in the netcdf file
	pressurename: name of atmospheric pressure variable
	temperaturename: name of atmospheric temperature variable
	savevariablename: name of the 3-d specific humidity variable to be saved in output
	sfc_humidity_hist_path: path to historical surface relative humidity
	sfc_humidity_future_path: path to future surface relative humidity
	T_S_hist_path: path to historical surface temperature
	T_S_future_path: path to future surface temperature
	sfc_savename: path to save the surface humidity difference fiels
	sfc_humidityname: name of the surface humidity in the input netcdf files
	sfc_tempname: name of the surface temperature in given netcdf
	sfc_savevariablename: name of the surface specific humidity variable to be saved in output
		
	Output:
	2 netcdf file of the same shape as the given 3D and 2D inputs containing the difference in specific humidity between the periods of the input. Unit is kg/kg. Can be further processed using other files in this repository (e.g. smoothing or interpolation)
"""



toppath = '/project/pr04/robro/inputfiles_for_surrogate_hadgem/inputfiles/'
humidity_hist_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_RELHUM_1971-2000_ydaymean.nc'
temperature_hist_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_T_1971-2000_ydaymean.nc'
pressure_hist_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_P_1971-2000_ydaymean.nc'
humidity_future_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_RELHUM_2070-2099_ydaymean.nc'
pressure_future_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_P_2070-2099_ydaymean.nc'
temperature_future_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_T_2070-2099_ydaymean.nc'
sfc_humidity_hist_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_RELHUM_S_1971-2000_ydaymean.nc'
sfc_humidity_future_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_RELHUM_S_2070-2099_ydaymean.nc'
T_S_hist_path = f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_T_S_1971-2000_ydaymean.nc'
T_S_future_path= f'{toppath}HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_T_S_2070-2099_ydaymean.nc'

savename='/project/pr04/robro/inputfiles_for_surrogate_hadgem/input_github/Diff_HadGEM2-ES_RCP85_QV.nc'
sfc_savename='/project/pr04/robro/inputfiles_for_surrogate_hadgem/input_github/Diff_HadGEM2-ES_RCP85_QV_S.nc'

humidityname='RELHUM'
pressurename='P'
temperaturename='T'
savevariablename='QV'
sfc_humidityname='RELHUM_S'
sfc_tempname='T_S'
sfc_savevariablename='QV_S'

hum_hist = xr.open_dataset(humidity_hist_path)[humidityname]
p_hist = xr.open_dataset(pressure_hist_path)[pressurename]
T_hist  = xr.open_dataset(temperature_hist_path)[temperaturename]

hum_fut = xr.open_dataset(humidity_future_path)[humidityname]
p_fut = xr.open_dataset(pressure_future_path)[pressurename]
T_fut = xr.open_dataset(temperature_future_path)[temperaturename]

sfc_hum_hist = xr.open_dataset(sfc_humidity_hist_path)[sfc_humidityname]
sfc_hum_fut = xr.open_dataset(sfc_humidity_future_path)[sfc_humidityname]
T_S_hist = xr.open_dataset(T_S_hist_path)[sfc_tempname]
T_S_fut = xr.open_dataset(T_S_future_path)[sfc_tempname]

#convert relative humidity to right values for use in formula if rh is defined between 0-1
if hum_hist.max() < 4:
	hum_hist = hum_hist * 100.
	hum_fut = hum_fut * 100.
	sfc_hum_hist = sfc_hum_hist * 100.
	sfc_hum_fut =sfc_hum_fut * 100.

spec_hum_hist = (hum_hist.data * np.exp(17.67*(T_hist.data - 273.15)/(T_hist.data-29.65))) / ( 0.263 * p_hist.data)
spec_hum_fut  = (hum_fut.data  * np.exp(17.67*(T_fut.data  - 273.15)/(T_fut.data -29.65))) / ( 0.263 * p_fut.data)

spec_hum_diff = spec_hum_fut - spec_hum_hist
spec_hum_diff = xr.DataArray(data=spec_hum_diff, dims=T_hist.dims, coords=T_hist.coords, name=savevariablename)   

spec_hum_diff = spec_hum_diff.astype('float32')
spec_hum_diff = spec_hum_diff.to_dataset(name=savevariablename)
spec_hum_diff.to_netcdf(savename)

print(f'saved {savename}')

sfc_spec_hum_hist = (sfc_hum_hist.data * np.exp(17.67*(T_S_hist.data - 273.15)/(T_S_hist.data-29.65))) / ( 0.263 * p_hist[:,-1,:,:].data)
sfc_spec_hum_fut = (sfc_hum_fut.data * np.exp(17.67*(T_S_fut.data - 273.15)/(T_S_fut.data-29.65))) / ( 0.263 * p_fut[:,-1,:,:].data)

sfc_spec_hum_diff = sfc_spec_hum_fut - sfc_spec_hum_hist
sfc_spec_hum_diff = xr.DataArray(data=sfc_spec_hum_diff, dims=T_S_hist.dims, coords=T_S_hist.coords, name=sfc_savevariablename)
sfc_spec_hum_diff = sfc_spec_hum_diff.astype('float32')
sfc_spec_hum_diff = sfc_spec_hum_diff.to_dataset(name=sfc_savevariablename)
sfc_spec_hum_diff.to_netcdf(sfc_savename)

print(f'saved {sfc_savename}')

