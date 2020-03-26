import xarray as xr

variablenames = ['PP', 'T', 'T_S', 'T_SO', 'U', 'V']

path_start = '/project/pr04/robro/inputfiles_for_surrogate_hadgem/inputfiles/HadGEM2-ES_Hist_RCP85_cosmo4-8_17_new_'

pathend_hist = '_1971-2000_ydaymean.nc'
pathend_fut  = '_2070-2099_ydaymean.nc'

savepath = '/project/pr04/robro/inputfiles_for_surrogate_hadgem/input_github/'

#the part of the output-filename before the variablename: 
outputname = 'Diff_HadGEM2-ES_RCP85_'

for variable in variablenames:
	hist = xr.open_dataset(f'{path_start}{variable}{pathend_hist}', decode_cf=False)[variable]
	fut = xr.open_dataset(f'{path_start}{variable}{pathend_fut}', decode_cf=False)[variable]

	hist.data = fut.data - hist.data

	hist.to_netcdf(f'{savepath}{outputname}{variable}.nc')

	print(f'saved {outputname}{variable}.nc')
