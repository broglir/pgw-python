import xarray as xr
import sys
from pathlib import Path
import numpy as np
import os
"""
Can be used to add the calculated difference in all necessary variables to the initial condition (laf) file. This very fast, just run it in the console.
It requires the difference in relative humidity to adapt the specific humidity!

Input:
	lafpath: Path to the original laf-file from the "base" simulation (e.g. reanalysis driven or historical simulation). The name of the laf file must be as outputted by int2lm (e.g. laf1970010100.nc ).
	newyear: What year to use in the files (change it to the future to adapt CO2 levels)
	laftimestep: Which timestep within the annual cycle is apropriate to adapt the laf file? (0 for beginning of year)
	newtimestring: What timestamp should be used for the adapted laf file? Put the exact time of the new laf file in the format 'seconds since yyyy-mm-dd hh:mm:ss'
	outputpath: In which folder should the adapted laf file be put (probably the same as the adapted boudary or lbfd files). Will be created if nonexistent. 
	Diffspath: Where is the input located, i.e. the single files that have been previously produced by the interpolate.py routie or the regridding routines. These are the files called for example T00000.nc
	vcflat: Altitude where the vertical coordinate levels in CCLM become flat (this can be found in runscripts or YUSPECIF). We assume a Gal-Chen vertical coordinate here.
	terrainpath: Path to a netcdf file containing the height of the terrain in the cosmo domain (could be a constant file such as lffd1969120100c.nc)
	height_flat: Array of the geometrical altitude of all model levels in the cclm doman (can be found e.g. in YUSPECIF file). One value for each vertical level (this means there should normally be no level 0)! 

Output:
	The adapted laf file will be written to the chosen location and should directly be usable for CCLM.
"""

lafpath = '/scratch/snx3000/robro/int2lm/HadGEM/driving_historical/laf1970010100.nc'
newyear = 2070
newtimestring = f'seconds since {newyear}-01-01 00:00:00'
outputpath = '/scratch/snx3000/robro/int2lm/HadGEM/PGW_TEST/2070/'
Diffspath = '/scratch/snx3000/robro/pgwtemp/interpolated/'
vcflat=11430. 
terrainpath='/store/c2sm/ch4/robro/surrogate_input/lffd1969120100c.nc'
height_flat=np.asanyarray([22700.0, 20800.0000, 19100.0, 17550.0, 16150.0, 14900.0, 13800.0, 12785.0, 11875.0, 11020.0, 10205.0,        9440.0, 8710.0, 8015.0, 7355.0, 6725.0, 6130.0, 5565.0, 5035.0, 4530.0, 4060.0, 3615.0, 3200.0, 2815.0, 2455.0, 2125.0, 1820.0, 1545.0, 1295.0, 1070.0, 870.0, 695.0, 542.0, 412.0, 303.0, 214.0, 143.0, 89.0, 49.0, 20.0])
laftimestep = 0

if len(sys.argv)>5:
	lafpath=str(sys.argv[1])
	new_year=str(sys.argv[2])
	newtimestring = f'seconds since {newyear}-01-01 00:00:00'
	outputpath=str(sys.argv[3])
	Diffspath=str(sys.argv[4])
	terrainpath=str(sys.argv[5])

if os.path.exists('heights.txt'):
	height_flat=np.genfromtxt('heights.txt',skip_header=1)[:-1,1]




def getpref(vcflat, terrainpath, height_flat):
	smoothing = (vcflat - height_flat) / vcflat
	smoothing = np.where(smoothing > 0, smoothing, 0)	

	const = xr.open_dataset(terrainpath)
	hsurf = const['HSURF'].squeeze()

	#the height at which the reference pressure needs to be computed needs to be derived form the terrain   following coordinates:
	newheights = np.zeros((len(height_flat), hsurf.shape[0], hsurf.shape[1]))

	#add the surface height but respect the terrain following coordinates
	for x in range(hsurf.shape[0]):
		for y in range(hsurf.shape[1]):
			newheights[:,x,y] =  height_flat + hsurf[x,y].values * smoothing

	pref = 100000*np.exp(-(9.80665*0.0289644*newheights/(8.31447*288.15)))
	pref_sfc = 100000*np.exp(-(9.80665*0.0289644*hsurf.data/(8.31447*288.15)))

	return pref, pref_sfc



def lafadapt(lafpath, newyear, outputpath, Diffspath, laftimestep, newtimestring, pref, pref_sfc):

	laffile = xr.open_dataset(lafpath, decode_cf=False)

	#if output directory doesn't exist create it
	Path(outputpath).mkdir(parents=True, exist_ok=True)
	
	def comprelhums(laffile, pref, pref_sfc):
		p = laffile['PP'] + pref
		QV = laffile['QV']
		T = laffile['T']

		p_sfc = laffile['PP'][:,-1,:,:] + pref_sfc
		QV_S = laffile['QV_S']
		T_S = laffile['T_S']

		RH = 0.263 * p * QV *(np.exp(17.67*(T - 273.15)/(T-29.65)))**(-1)
		RH_S = 0.263 * p_sfc * QV_S *(np.exp(17.67*(T_S - 273.15)/(T_S-29.65)))**(-1)

		return RH, RH_S



	def diffadd(var, laffile=laffile):
		Diff = xr.open_dataset(f'{Diffspath}/{var}{laftimestep:05d}.nc')[var]
		laffile[var].data = laffile[var].data + Diff.data.astype('float32')


    #compute new humidity funcion once temperature and pressure were changed
	def computeQVnew(laffile, RH_old, RH_S_old):
		Diffrh = xr.open_dataset(f'{Diffspath}/RELHUM{laftimestep:05d}.nc')['RELHUM']
		Diffrh_s = xr.open_dataset(f'{Diffspath}/RELHUM_S{laftimestep:05d}.nc')['RELHUM_S']

		newRH = RH_old.data + Diffrh.data.astype('float32')
		newRH_S = RH_S_old.data + Diffrh_s.data.astype('float32')

		p = laffile['PP'] + pref
		T = laffile['T']
		p_sfc = np.squeeze(laffile['PP'][:,-1,:,:]) + pref_sfc
		T_S = laffile['T_S']

		newQV = (newRH.data  * np.exp(17.67*(T.data  - 273.15)/(T.data -29.65))) / ( 0.263 * p.data)
		newQV_S = (newRH_S.data  * np.exp(17.67*(T_S.data  - 273.15)/(T_S.data -29.65))) / ( 0.263 * p_sfc.data)

		laffile['QV'].data = newQV.astype('float32')
		laffile['QV_S'].data = newQV_S.astype('float32')

		return laffile


	#get relative humidity in old laf
	RH_old, RH_S_old = comprelhums(laffile, pref, pref_sfc)

	#change other variables
	variables = ['T', 'T_S', 'U', 'V']
	for var in variables:
		diffadd(var, laffile)
	
	laffile.time.attrs['units'] = newtimestring
	laffile['time'].data[0] = 0 

	#apply moisture function
	laffile = computeQVnew(laffile, RH_old, RH_S_old)

	endpartlaf = lafpath[-9:] 
	
	laffile.to_netcdf(f'{outputpath}/laf{newyear}{endpartlaf}', mode='w')
	laffile.close()

pref, pref_sfc = getpref(vcflat, terrainpath, height_flat)
lafadapt(lafpath, newyear, outputpath, Diffspath, laftimestep, newtimestring, pref, pref_sfc)
