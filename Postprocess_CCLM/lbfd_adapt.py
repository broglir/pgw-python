import xarray as xr
import sys
import os
import glob
from pathlib import Path
import numpy as np

"""
Add the calculated difference in all necessary variables to the boundary condition (lbfd) files for one year.
This should be run on a cluster.

Input:
	year (comandline argument): The year for which the boundary files should be adapted.
	The year refers to the year in the original output from int2lm.

	lbfdpath: path to directory where boundary files are saved

	changeyears: amount of years to be added to timestamp of data (shift to future)

	outputpath: path to put the modifiyed bondary files

	Diffspath: Where to find the changes (climate change deltas) to add to the boundary files.
	This is the ouput of earlier scripts in this repository (i.e. T00000.nc, T00001.nc etc.).

	difftimesteps: Amount of timesteps (or boundary data fields) in one year
	(extrapolate to an entire year even if only a fraction is needed; this depends on the calendar used)

    terrainpath: Path to a netcdf file containing the height of the terrain in
	the cosmo domain (could be a constant file such as lffd1969120100c.nc)

	starttimestep: The files as produced from previous scripts start in january
	and run through the year. If your PGW simulation does not start in january,
	you have to compute the timestep of the start (dayofyear * timesteps_per_day)

	recompute_pressure: Boolean to indicate whether the pressure of the boundary
	files should be recomputed based on temperature changes (not necessary if a
	difference file for PP already exists (e.g. from previous cosmo simulation).

Output:
	For every boundary file in the inputdata, a corresponding output field will
	be written to the path specified as outputpath.
"""

year = int(sys.argv[1])

lbfdpath = f'/scratch/snx3000/robro/int2lm/HadGEM/driving_historical/{year}/'

changeyears = 88
newyear = year + changeyears
outputpath = f'/scratch/snx3000/robro/int2lm/HadGEM/PGW_TEST/{newyear}/'

Diffspath = '/scratch/snx3000/robro/pgwtemp/interpolated/'
difftimesteps = 366 * 4

starttimestep = 0

terrainpath='/store/c2sm/ch4/robro/surrogate_input/lffd1969120100c.nc'

#if submitted by master.py
if len(sys.argv)>5:
	year=int(sys.argv[1])
	lbfdpath=str(sys.argv[2])
	outputpath=str(sys.argv[3])
	Diffspath=str(sys.argv[4])
	terrainpath=str(sys.argv[5])
	starttimestep=int(sys.argv[6])
	difftimesteps=int(sys.argv[7])
	changeyears=int(sys.argv[8])
	recompute_pressure=bool(sys.argv[9])
	newyear = year + changeyears


#read height coordinate from file
os.chdir(lbfdpath)
files = glob.glob('lbfd??????????.nc')
height_flat_half = xr.open_dataset(files[0]).vcoord #these are half levels
height_flat = xr.open_dataset(files[0]).vcoord[:-1]
vcflat=xr.open_dataset(files[0]).vcoord.vcflat

#get the full level height
height_flat.data = height_flat_half.data[1:] + \
(0.5 * (height_flat_half.data[:-1] - height_flat_half.data[1:]) )

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



#function to adapt all lbfd files:
def lbfdadapt(lbfdpath, outputpath, Diffspath, difftimesteps, changeyears, pref, pref_sfc, dz, recompute_pressure):

	#function to add all variables but humidity to the boundary field (use given timestep)
	def diffadd(var, num, lbfd):
		Diff = xr.open_dataset(f'{Diffspath}/{var}{num:05d}.nc')[var]
		lbfd[var].data = lbfd[var].data + Diff.data.astype('float32')

	#function to calculate relative humidity
	def comprelhums(lbfd, pref, pref_sfc):
		p = lbfd['PP'] + pref
		QV = lbfd['QV']
		T = lbfd['T']

		p_sfc = lbfd['PP'][:,-1,:,:] + pref_sfc
		QV_S = lbfd['QV_S']
		T_S = lbfd['T_S']

		RH = 0.263 * p * QV *(np.exp(17.67*(T - 273.15)/(T-29.65)))**(-1)
		RH_S = 0.263 * p_sfc * QV_S *(np.exp(17.67*(T_S - 273.15)/(T_S-29.65)))**(-1)

		return RH, RH_S


	def pressure_recompute(lbfd, num, pref, dz, height_flat):
		#function to compute pressure field in a differen climate using the barometric
		#formula (maintaining hydrostatic balance)
		#temperature changes
		dT_sfc = xr.open_dataset(f'{Diffspath}/T_S{num:05d}.nc')['T_S']
		dT_atmos = xr.open_dataset(f'{Diffspath}/T{num:05d}.nc')['T']

		#get pressure field
		pressure_original = lbfd['PP'] + pref
		pressure_new = pressure_original.copy()

		temperature = lbfd['T']
		sfc_temperature = lbfd['T_S']

		#define barometric height formula
		def barometric(reference_pressure, reference_temperature, dz, lapse_rate):
			R = 8.3144598 #universal gas constant
			M = 0.0289644 # molar mass of air
			g = 9.80665
			#lapse_rate = - 0.0065
			exo = - g * M / (R * lapse_rate) #exponent in barometric formula

			pressure = reference_pressure * ( (reference_temperature + (lapse_rate * dz))
			/ reference_temperature )**exo

			return pressure

		#compute surface pressure
		surface_press = barometric(pressure_original[:,-1,:,:], temperature[:,-1,:,:], -height_flat[-1], 0.0065)

		#get the lowest model level in warmer climate
		pressure_new[:,-1,:,:] = barometric(surface_press, sfc_temperature+dT_sfc, height_flat[-1], -0.0065)
		#get the rest (loop from ground up)
		for level in range(len(dz)-1, -1, -1):
			pressure_new[:,level,:,:] = barometric(pressure_new[:,level+1,:,:], \
			temperature[:,level+1,:,:]+dT_atmos[level+1,:,:], dz[level,:,:], -0.0065)

		new_pp = pressure_new.data - pref
		#convert to PP
		lbfd['PP'].data = new_pp.astype('float32')

		return lbfd


	#compute new humidity funcion once temperature and pressure were changed
	def computeQVnew(lbfd, num, RH_old, RH_S_old):
		Diffrh = xr.open_dataset(f'{Diffspath}/RELHUM{num:05d}.nc')['RELHUM']
		Diffrh_s = xr.open_dataset(f'{Diffspath}/RELHUM_S{num:05d}.nc')['RELHUM_S']

		newRH = RH_old.data + Diffrh.data.astype('float32')
		newRH_S = RH_S_old.data + Diffrh_s.data.astype('float32')

		p = lbfd['PP'] + pref
		T = lbfd['T']
		p_sfc = lbfd['PP'][:,-1,:,:] + pref_sfc
		T_S = lbfd['T_S']

		newQV = (newRH.data  * np.exp(17.67*(T.data  - 273.15)/(T.data -29.65))) / ( 0.263 * p.data)
		newQV_S = (newRH_S.data  * np.exp(17.67*(T_S.data  - 273.15)/(T_S.data -29.65))) / ( 0.263 * p_sfc.data)

		lbfd['QV'].data = newQV.astype('float32')
		lbfd['QV_S'].data = newQV_S.astype('float32')

		return lbfd



	# calculation part
	#get a list of all lbfd files:
	os.chdir(lbfdpath)
	files = glob.glob('lbfd??????????.nc')
	files.sort()

	#if output directory doesn't exist create it
	Path(outputpath).mkdir(parents=True, exist_ok=True)
	num = starttimestep #set timestep where to start

	#loop over all boundary fields:
	for lbfdnum in files:
		#print and open boundary data
		print(num, lbfdnum)
		lbfd = xr.open_dataset(lbfdnum, decode_cf=False)

		#at the end of year reset the timestep counter
		if num >= difftimesteps - 1:
			num = 0

		#run the defined functions and change filename & time:
		RH_old, RH_S_old = comprelhums(lbfd, pref, pref_sfc)

		if recompute_pressure == True:
			lbfd = pressure_recompute(lbfd, num, pref, dz, height_flat)
			variables = ['T', 'T_S', 'U', 'V']
		else:
			variables = ['T', 'T_S', 'U', 'V', 'PP']

		for var in variables:
			diffadd(var, num, lbfd)

		#change time to future
		endtimestring = lbfd.time.units[-15:]
		old_yyyy_timestamp = int(lbfd.time.units[-19:-15])
		new_yyyy_timestamp = old_yyyy_timestamp + changeyears
		lbfd.time.attrs['units'] = f'seconds since {new_yyyy_timestamp}{endtimestring}'

		lbfd = computeQVnew(lbfd, num, RH_old, RH_S_old)

		endpart = lbfdnum[8:]
		lbfdyear = int(lbfdnum[4:8])
		lbfdyear = lbfdyear + changeyears
		lbfd.to_netcdf(f'{outputpath}/lbfd{lbfdyear}{endpart}', mode='w')
		lbfd.close()
		num = num + 1

pref, pref_sfc, height_array = getpref(vcflat, terrainpath, height_flat)
dz = height_array[:-1] - height_array[1:] #get height difference between model levels
lbfdadapt(lbfdpath, outputpath, Diffspath, difftimesteps, changeyears, pref,
pref_sfc, dz, recompute_pressure)
