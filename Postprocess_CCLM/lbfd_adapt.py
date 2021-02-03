import xarray as xr
import sys
import os
import glob
from pathlib import Path
import numpy as np

"""
Add the calculated difference in all necessary variables to the boundary condition (lbfd) files for one year. This should be run on a cluster. This script will only work when data for all year is present!

Input:
	year (comandline argument): The year for which the boundary files should be adapted. The year refers to the year in the original output from int2lm.
	lbfdpath: path to directory where boundary files are saved
	changeyears: amount of years to be added to timestamp of data
	outputpath: path to put the adapted bondary files
	Diffspath: Where to find the changes (climate change deltas) to add to the boundary files. This is the ouput of earlier scripts in this repository (i.e. T00000.nc, T00001.nc etc.).
	difftimesteps: Amount of timesteps (or boundary data fields) in one year
    vcflat: Altitude where the vertical coordinate levels in CCLM become flat (this can be found in runscripts or YUSPECIF). We assume a Gal-Chen vertical coordinate here.is needed for the adaptation of humidity.
    terrainpath: Path to a netcdf file containing the height of the terrain in the cosmo domain (could be a constant file such as lffd1969120100c.nc)
    height_flat: Array of the geometrical altitude of all model levels in the cclm doman (can be found e.g. in YUSPECIF file). One value for each vertical level (this means there should normally be no level 0)! 


Output:
	For every boundary file in the inputdata, a corresponding output field will be written to the path specified as outputpath.
"""

year = int(sys.argv[1]) 
#The year (in original data) which should be processed should be passed as command line argument
lbfdpath = f'/scratch/snx3000/robro/int2lm/HadGEM/driving_historical/{year}/'

changeyears = 100
newyear = year + changeyears
outputpath = f'/scratch/snx3000/robro/int2lm/HadGEM/PGW_TEST/{newyear}/'

Diffspath = '/scratch/snx3000/robro/pgwtemp/interpolated/'
difftimesteps = 360 * 4

#options for adaptation of humidity
vcflat=11430. 
terrainpath='/store/c2sm/ch4/robro/surrogate_input/lffd1969120100c.nc'



height_flat=np.asanyarray([22700.0, 20800.0000, 19100.0, 17550.0, 16150.0, 14900.0, 13800.0, 12785.0, 11875.0, 11020.0, 10205.0,        9440.0, 8710.0, 8015.0, 7355.0, 6725.0, 6130.0, 5565.0, 5035.0, 4530.0, 4060.0, 3615.0, 3200.0, 2815.0, 2455.0, 2125.0, 1820.0, 1545.0, 1295.0, 1070.0, 870.0, 695.0, 542.0, 412.0, 303.0, 214.0, 143.0, 89.0, 49.0, 20.0])

if len(sys.argv)>5:
	year=int(sys.argv[1])
	lbfdpath=str(sys.argv[2])
	lbfdpath = f'{lbfdpath}/{year}/'
	changeyears = 100
	newyear = year + changeyears
	outputpath=str(sys.argv[3])
	outputpath=f'{outputpath}/{newyear}/'
	Diffspath=str(sys.argv[4])
	terrainpath=str(sys.argv[5])



if os.path.exists('heights.txt'):
	height_flat=np.genfromtxt('heights.txt',skip_header=1)[:-1,1]


#get reference pressure function
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
	
	#old but somewhat less acurate formulation
	#pref = 100000*np.exp(-(9.80665*0.0289644*newheights/(8.31447*288.15)))
	#pref_sfc = 100000*np.exp(-(9.80665*0.0289644*hsurf.data/(8.31447*288.15)))
	
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
	pref_sfc = p0sl * np.exp (-g / R_d * h_scal / t00 * \
                   np.log((np.exp(hsurf.data / h_scal) * t00 + delta_t) / \
                          (t00 + delta_t)) )
	
	return pref, pref_sfc


#function to adapt all lbfd files:
def lbfdadapt(lbfdpath, outputpath, Diffspath, difftimesteps, changeyears, pref, pref_sfc):
        
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

	#loop over all boundary fields:
	for num,lbfdnum in enumerate(files):
		#print and open boundary data
		print(num, lbfdnum)
		lbfd = xr.open_dataset(lbfdnum, decode_cf=False)

		#if there is a file for the next year in the folder use first timestep; print to check
		if num >= difftimesteps:
			num = 0
			print(f'used first delta for {lbfdnum}')
		

		#run the defined functions and change filename & time:
		RH_old, RH_S_old = comprelhums(lbfd, pref, pref_sfc)

		variables = ['T', 'T_S', 'U', 'V']

		for var in variables:
			diffadd(var, num, lbfd)
	
		#change time to future
		endtimestring = lbfd.time.units[-15:]
		old_yyyy_timestamp = int(lbfd.time.units[-19:-15])
		new_yyyy_timestamp = old_yyyy_timestamp + changeyears
		lbfd.time.attrs['units'] = f'seconds since {new_yyyy_timestamp}{endtimestring}'

		lbfd = computeQVnew(lbfd, num, RH_old, RH_S_old)
		
		endpart = lbfdnum[-9:]
		lbfdyear = int(lbfdnum[4:8])
		lbfdyear = lbfdyear + changeyears
		lbfd.to_netcdf(f'{outputpath}/lbfd{lbfdyear}{endpart}', mode='w')
		lbfd.close()

pref, pref_sfc = getpref(vcflat, terrainpath, height_flat)
lbfdadapt(lbfdpath, outputpath, Diffspath, difftimesteps, changeyears, pref, pref_sfc)
