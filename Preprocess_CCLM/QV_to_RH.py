# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:06:30 2019

Script to compute the mean annual cycle in relative humidity from the mean annual cycle in specific humidity. Needs the mean annual cycle in pressure and temperature as input.
"""


import numpy as np
import xarray as xr


#create surface values and/or upper atmospheric?
surface = False
atmos = True

#enter paths (only necessary for the levels chosen above)
superpath='/store/c2sm/ch4/robro/surrogate_input/GCMdata/'

qvname = 'hus_MPI-ESM1-2-HR_2070-2099_ydaymean.nc'
pname = 'p_MPI-ESM1-2-HR_abs_ydaymean.nc'
Tname= 'ta_MPI-ESM1-2-HR_2070-2099_ydaymean.nc'

qvsname='huss_MPI-ESM1-2-HR_1971-2000_ydaymean.nc'
Tsname='tas_MPI-ESM1-2-HR_1971-2000_ydaymean.nc'
pslname='psl_MPI-ESM1-2-HR_1971-2000_ydaymean.nc'

savenameupper='RELHUM_MPI-ESM1-2-HR_2070-2099_ydaymean.nc'

savenamesfc='RELHUM_S_MPI-ESM1-2-HR_2070-2099_ydaymean.nc'



if atmos == True:
	print('procedure for 3-D humidity!')

	QV = xr.open_dataset(superpath+qvname)['hus']
	p = xr.open_dataset(superpath+pname)['p']
	T  = xr.open_dataset(superpath+Tname)['ta']

	p['time'] = T['time']
	RH = 0.263 * p * QV *(np.exp(17.67*(T - 273.15)/(T-29.65)))**(-1)
	
	RH = RH.astype('float32')
	RHds = RH.to_dataset(name='RELHUM')
	RHds.to_netcdf(superpath+savenameupper)

	print('sucess upper atmosphere')

	

if surface == True:
	print('procedure for surface humidity!')
	
	p_sfc = xr.open_dataset(superpath+pslname)['psl']
	
	QV_S = xr.open_dataset(superpath+qvsname)['huss']
	T_S = xr.open_dataset(superpath+Tsname)['tas']

	RH_S = 0.263 * p_sfc * QV_S *(np.exp(17.67*(T_S - 273.15)/(T_S-29.65)))**(-1)
	RH_S = RH_S.astype('float32')
	RH_Sds = RH_S.to_dataset(name='RELHUM_S')
	RH_Sds.to_netcdf(superpath+savenamesfc)
	
	print('sucess surface value')
