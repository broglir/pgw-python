# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr

"""
Preprocessing script to convert PP from COSMO-CLM to absolute pressure. This is only necessary if one subsequently wants to compute the mearelative Humidity from Specific humidity. 
"""

#enter paths
superpath='/project/pr04/robro/inputfiles_for_surrogate_hadgem/inputfiles/'

#enter path to pp
ppname = 'HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_PP_2070-2099_ydaymean.nc'
savename = 'HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_P_2070-2099_ydaymean.nc'

const = xr.open_dataset('/store/c2sm/ch4/robro/surrogate_input/lffd1969120100c.nc')
hsurf = const['HSURF'].squeeze()


vcflat=11430. #altitude where coordinate system becomes flat (you can find that in runscripts)

#CCLM uses a referece pressure system, to compute the actual pressure it PP needs to be added to the reference. These are the height levels for the 50km simulations!

height_flat=np.asanyarray([22700.0, 20800.0000, 19100.0, 17550.0, 16150.0, 14900.0, 13800.0, 12785.0, 11875.0, 11020.0, 10205.0, 		9440.0, 8710.0, 8015.0, 7355.0, 6725.0, 6130.0, 5565.0, 5035.0, 4530.0, 4060.0, 3615.0, 3200.0, 2815.0, 2455.0, 2125.0, 1820.0, 1545.0, 1295.0, 1070.0, 870.0, 695.0, 542.0, 412.0, 303.0, 214.0, 143.0, 89.0, 49.0, 20.0])

smoothing = (vcflat - height_flat) / vcflat
smoothing = np.where(smoothing > 0, smoothing, 0)


#the height at which the reference pressure needs to be computed needs to be derived form the terrain 	following coordinates:
newheights = np.zeros((len(height_flat), hsurf.shape[0], hsurf.shape[1]))

#add the surface height but respect the terrain following coordinates
for x in range(hsurf.shape[0]):
	for y in range(hsurf.shape[1]):
		newheights[:,x,y] =  height_flat + hsurf[x,y].values * smoothing
		
#simple old equation
#pref = 100000*np.exp(-(9.80665*0.0289644*newheights/(8.31447*288.15)))

#New formulation as researched by Christian Steger (untested)
# Constants
p0sl = 100000.0 # sea-level pressure [Pa]
t0sl = 288.15   # sea-level temperature [K]
# Source: COSMO description Part I, page 29
g = 9.80665     # gravitational acceleration [m s-2]
R_d = 287.05    # gas constant for dry air [J K-1 kg-1]
# Source: COSMO source code, data_constants.f90

# irefatm = 2
delta_t = 75.0
h_scal = 10000.0
# Source: COSMO description Part VII, page 66
t00 = t0sl - delta_t
	
pref = p0sl * np.exp (-g / R_d * h_scal / t00 * \
                   np.log((np.exp(newheights / h_scal) * t00 + delta_t) / \
                          (t00 + delta_t)) )

PP = xr.open_dataset(superpath+ppname)['PP']

p = PP + pref
	
p = p.astype('float32')
pds = p.to_dataset(name='P')
pds.to_netcdf(superpath+savename)
	
