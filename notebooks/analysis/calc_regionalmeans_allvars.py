# Script to load and save regional means for each variable at monthly resolution

import xarray as xr
import numpy as np
import gfdl_utils as gu
from dask.diagnostics import ProgressBar
from information import *
from processing import *
from variance import *
from averaging import *
import os


# List of variables. If None, calculates for all available variables.
variables = ['intpp','phos','chlos','o2os','tos']
frequency='monthly'
maskset = 'LME' # LME or global

grid = xr.open_dataset(ppeDict['griddirtmp']+ppeDict['gridfile'])
if maskset=='global':
    masks = generate_masks(grid)
elif maskset=='LME':
    masks = xr.open_dataset(ppeDict['pathLMEmask'])
savedir = ppeDict['datasavedir']+'/processed/regionalmeans/'
verbose = False

if variables is None:
    variables = get_allvars_ensemble(frequency)

### MAIN LOOP
for variable in variables:
    ### CONTROL
    print('Calculating and saving regional means for : '+variable)
    print('Control simulation:')
    timestr = 'control'
    savefilename = '.'.join([variable,frequency,timestr,maskset,'nc'])

    if os.path.isfile(savedir+savefilename):
        print(savefilename+' already exists. Not recalculating.')
    else:
        control = open_control(variable,frequency)
        da = control[variable]
        da_out = calc_regionalmean_all(da,masks,grid['areacello'],verbose=verbose)
        print('Saving '+savefilename)
        da_out.to_netcdf(savedir+savefilename,mode='w')

    ### ENSEMBLES
    for startyear in ppeDict['startyears']:
        for startmonth in ppeDict['startmonths']:
            timestr = str(startyear).zfill(4)+str(startmonth).zfill(2)
            print('Ensemble '+timestr+':')
            savefilename = '.'.join([variable,frequency,timestr,maskset,'nc'])
            if os.path.isfile(savedir+savefilename):
                print(savefilename+' already exists. Not recalculating.')
            else:
                control = open_control(variable,frequency)
                es = open_ensemble(variable,frequency,startyear=startyear,startmonth=startmonth,control=control,verbose=verbose)
                da = es[variable]
                da_out = calc_regionalmean_all(da,masks,grid['areacello'],verbose=verbose)
                print('Saving '+savefilename)
                da_out.to_netcdf(savedir+savefilename)