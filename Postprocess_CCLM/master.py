import sys
import os
import numpy as np
import glob

'''
Master script to run the workflow. Similar structure to settings.py in parent directory. 

'''
difference_2d_files_path='/scratch/snx3000/jvergara/PGW/temporaly_and_horizontaly_interpolated/'
difference_files_path='/scratch/snx3000/jvergara/PGW/full_interpolation/'
lbdfs_files_path='/scratch/snx3000/jvergara/PGW/COSMO-boundaries/'
constant_variables_file='/scratch/snx3000/jvergara/PGW/lffd20001001000000c.nc'
laf_file=glob.glob(f'{lbdfs_files_path}laf*')[0]
print(laf_file)
year_laf=laf_file.split('laf')[1][:4]
print(year_laf)
output_path='/scratch/snx3000/jvergara/PGW/final_files'
os.makedirs(output_path, exist_ok=1)

st_year='2005'
end_year='2016'


sc_directory='/scratch/snx3000/jvergara/PGW/'
script_directory='/scratch/snx3000/jvergara/PGW/pgw-python/Postprocess_CCLM/'

execute_rename=0

if execute_rename:
	print('Renaming 2D fields')
	variablename_cmor = [ 'hurs', 'tas' ]
	variablename_cclm = ['RELHUM_S', 'T_S'] #tas is modifiyed to T_S instead of T_2M to adapt the sea surface temps
	for i in range(len(variablename_cclm)):
		cmd=f'python rename_variables.py {variablename_cmor[i]} {variablename_cclm[i]} {difference_2d_files_path} {difference_files_path}'
		a=os.system(cmd)


execute_adapt_laf=1

if execute_adapt_laf:
	print('Executing addition of signal to laf file')
	cmd=f'python laf_adapt.py {laf_file} {int(year_laf)+100} {output_path} {difference_files_path} {constant_variables_file}' 
	print(cmd)
	a=os.system(cmd)

execute_lbdf=0
if execute_lbdf:
	print('Executing addition of signal to lbdf files')
	cmd=f'python submit_lbfd.py {sc_directory} {script_directory} {st_year} {end_year} {lbdfs_files_path} {output_path} {difference_files_path} {constant_variables_file}'
	a=os.system(cmd)


