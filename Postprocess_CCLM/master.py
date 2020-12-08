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


execute_rename=1

if execute_rename:
	variablename_cmor = [ 'hurs', 'tas' ]
	variablename_cclm = ['RELHUM_S', 'T_S'] #tas is modifiyed to T_S instead of T_2M to adapt the sea surface temps
	for i in range(len(variablename_cclm)):
		cmd=f'python rename_variables.py {variablename_cmor[i]} {variablename_cclm[i]} {difference_2d_files_path} {difference_files_path}'
		a=os.system(cmd)


execute_adapt_laf=1

if execute_adapt_laf:
	cmd=f'python laf_adapt.py {laf_file} {year_laf} {output_path} {difference_files_path} {constant_variables_file}' 
	print(cmd)
	a=os.system(cmd)
