import xarray as xr
import sys
from pathlib import Path
import numpy as np
import os
"""
Can be used to add the calculated difference in all necessary variables to the initial condition (laf) file.
This very fast, just run it in the console.
It requires the difference in relative humidity to adapt the specific humidity!

Input:
	lafpath: Path to the original laf-file from the "base" simulation
	(e.g. reanalysis driven or historical simulation). The name of the laf file
	must be as outputted by int2lm (e.g. laf1970010100.nc ).

	newyear: What year to use in the files (change it to the future to adapt CO2 levels)

	laftimestep: Which timestep within the annual cycle is apropriate to adapt
	the laf file? (0 for beginning of year; otherwise dayofyear*timesteps_per_day)

	newtimestring: What timestamp should be used for the adapted laf file?
	Put the exact time of the new laf file in the format 'seconds since yyyy-mm-dd hh:mm:ss'

	outputpath: In which folder should the adapted laf file be put (
	probably the same as the adapted boudary or lbfd files). Will be created if nonexistent.

	Diffspath: Where is the input located, i.e. the single files that have been
	reviously produced by the interpolate.py routie or the regridding routines.
	These are the files called for example T00000.nc

	terrainpath: Path to a netcdf file containing the height of the terrain in
	the cosmo domain (could be a constant file such as lffd1969120100c.nc)

	recompute_pressure: Boolean to indicate whether the pressure of the boundary
	files should be recomputed based on temperature changes (not necessary if a
	difference file for PP already exists (e.g. from previous cosmo simulation).

Output:
	The adapted laf file will be written to the chosen location and should directly be usable for CCLM.
"""

lafpath = ''
newyear = 2070
newtimestring = f'seconds since {newyear}-01-01 00:00:00'
outputpath = ''
Diffspath = '/scratch/snx3000/robro/pgwtemp/interpolated/'
terrainpath='/store/c2sm/ch4/robro/surrogate_input/lffd1969120100c.nc'
laftimestep = 0
recompute_pressure = False

if len(sys.argv)>5:
	lafpath=str(sys.argv[1])
	newyear=str(sys.argv[2])
	newtimestring = str(sys.argv[6])
	outputpath=str(sys.argv[3])
	Diffspath=str(sys.argv[4])
	terrainpath=str(sys.argv[5])
	laftimestep=int(sys.argv[7])
	recompute_pressure=bool(sys.argv[8])

height_flat = xr.open_dataset(lafpath).vcoord[:-1] #no 0 level (only for staggered grid)
vcflat=xr.open_dataset(lafpath).vcoord.vcflat

#get reference pressure function
def getpref(vcflat, terrainpath, height_flat):
	smoothing = (vcflat - height_flat) / vcflat
	smoothing = np.where(smoothing > 0, smoothing, 0)

	const = xr.open_dataset(terrainpath)
	hsurf = const['HSURF'].squeeze()

	#the height at which the reference pressure needs to be computed needs to be derived form the terrain   following coordinates:
	newheights = np.zeros((len(height_flat), hsurf.shape[0], hsurf.shape[1]))

	#avoid forloop
	newheights = height_flat.values[:,None,None] + hsurf.values[None,:,:] * smoothing[:,None,None]

	#New formulation as researched by Christian Steger (untested)
	# Constants
	p0sl = height_flat.p0sl # sea-level pressure [Pa]
	t0sl = height_flat.t0sl   # sea-level temperature [K]
	# Source: COSMO description Part I, page 29
	g = 9.80665     # gravitational acceleration [m s-2]
	R_d = 287.05    # gas constant for dry air [J K-1 kg-1]
	# Source: COSMO source code, data_constants.f90

	# irefatm = 2
	delta_t = height_flat.delta_t
	h_scal = height_flat.h_scal
	# Source: COSMO description Part VII, page 66
	t00 = t0sl - delta_t

	pref = p0sl * np.exp (-g / R_d * h_scal / t00 * \
                   np.log((np.exp(newheights / h_scal) * t00 + delta_t) / \
                          (t00 + delta_t)) )
	pref_sfc = p0sl * np.exp (-g / R_d * h_scal / t00 * \
                   np.log((np.exp(hsurf.data / h_scal) * t00 + delta_t) / \
                          (t00 + delta_t)) )

	return pref, pref_sfc, newheights



def lafadapt(lafpath, newyear, outputpath, Diffspath, laftimestep, newtimestring, pref, pref_sfc, height_array, recompute_pressure):

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


	def pressure_recompute(laf_file, pref, height_array):
		#function to compute pressure field in a differen climate using the barometric
		#formula (maintaining hydrostatic balance)
		#temperature changes
		dT_sfc = xr.open_dataset(f'{Diffspath}/T_S{laftimestep:05d}.nc')['T_S']
		dT_atmos = xr.open_dataset(f'{Diffspath}/T{laftimestep:05d}.nc')['T']

		#get pressure field
		pressure_original = laffile['PP'] + pref
		pressure_new = pressure_original.copy()

		#get height difference between model levels
		dz = height_array[:-1] - height_array[1:]

		temperature = laffile['T']
		sfc_temperature = laffile['T_S']

		#define barometric height formula
		def barometric(reference_pressure, reference_temperature, dz, lapse_rate):
			R = 8.3144598 #universal gas constant
			M = 0.0289644 # molar mass of air #standard lapse rate
			g = 9.80665
			#lapse_rate = - 0.0065
			exo = - g * M / (R * lapse_rate) #exponent in barometric formula

			pressure = reference_pressure * ( (reference_temperature + (lapse_rate * dz))
			/ reference_temperature )**exo

			return pressure

		#compute surface pressure
		surface_press = barometric(pressure_original[:,-1,:,:], temperature[:,-1,:,:], -20, 0.0065)

		#get the lowest model level in warmer climate
		pressure_new[:,-1,:,:] = barometric(surface_press, sfc_temperature+dT_sfc, 20, -0.0065)
		#get the rest
		pressure_new[:,:-1,:,:] = barometric(pressure_original[:,1:,:,:],
		temperature[:,1:,:,:]+dT_atmos[1:,:,:], dz, -0.0065)

		#convert to PP
		laffile['PP'] = pressure_new - pref

		return laffile


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

	if recompute_pressure:
		laffile = pressure_recompute(laffile, pref, height_array)
		variables = ['T', 'T_S', 'U', 'V']
	else:
		variables = ['T', 'T_S', 'U', 'V', 'PP']

	#change other variables
	for var in variables:
		diffadd(var, laffile)

	laffile.time.attrs['units'] = newtimestring
	laffile['time'].data[0] = 0

	#apply moisture function
	laffile = computeQVnew(laffile, RH_old, RH_S_old)

	endpartlaf = lafpath[-9:]

	laffile.to_netcdf(f'{outputpath}/laf{newyear}{endpartlaf}', mode='w')
	laffile.close()
	print(f'saved {outputpath}/laf{newyear}{endpartlaf}')

pref, pref_sfc, height_array = getpref(vcflat, terrainpath, height_flat)
lafadapt(lafpath, newyear, outputpath, Diffspath, laftimestep, newtimestring,
pref, pref_sfc, height_array, recompute_pressure)
