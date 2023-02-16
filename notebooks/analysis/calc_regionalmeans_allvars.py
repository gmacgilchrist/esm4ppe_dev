# Script to load and save regional means for each variable at monthly resolution

import xarray as xr
import numpy as np
import gfdl_utils as gu
from dask.diagnostics import ProgressBar
from information import *
from processing import *
from variance import *
import os

frequency='monthly'
grid = xr.open_dataset(ppeDict['rootdir']+ppeDict['gridfile'])
masks = generate_masks(grid)
savedir = ppeDict['datasavedir']+'/processed/regionalmeans/'
verbose = False

# Functions for calculating means
def calc_regionalmean(da,mask,weights):
    return da.where(mask,drop=True).weighted(weights.fillna(0)).mean(['xh','yh'])

def calc_regionalmean_all(da,masks,weights,verbose=False):
    ''' Calculate regional means for [da] based on [masks].
    Return DataArray with "region" dimension corresponding to masknames.'''
    coords_out = dict(da.coords)
    coords_out.pop('xh')
    coords_out.pop('yh')
    dims_orig = list(coords_out.keys())
    coords_out['region']=list(masks.keys())
    da_out = xr.DataArray(dims=coords_out.keys(),coords=coords_out,name=da.name)
        
    for name,mask in masks.items():
        print('region: '+name)
        if verbose:
            with ProgressBar():
                da_out.loc[{'region':name}] = calc_regionalmean(da,mask,grid['areacello']).transpose(*dims_orig)
        else:
            da_out.loc[{'region':name}] = calc_regionalmean(da,mask,grid['areacello']).transpose(*dims_orig)
    return da_out

### MAIN LOOP
variables = get_allvars_ensemble(frequency)

for variable in variables:
    ### CONTROL
    print('Calculating and saving regional means for : '+variable)
    print('Control simulation:')
    timestr = 'control'
    savefilename = '.'.join([variable,frequency,timestr,'regionalmeans','nc'])

    if os.path.isfile(savedir+savefilename):
        print(savefilename+' already exists. Not recalculating.')
    else:
        control = open_control(variable,frequency)
        da = control[variable]
        da_out = calc_regionalmean_all(da,masks,grid['areacello'],verbose=verbose)
        print('Saving '+savefilename)
        da_out.to_netcdf(savedir+savefilename,mode='w')

    ### ENSEMBLES
    startmonth = 1
    for startyear in ppeDict['startyears']:
        timestr = str(startyear).zfill(4)+str(startmonth).zfill(2)
        print('Ensemble '+timestr+':')
        savefilename = '.'.join([variable,frequency,timestr,'regionalmeans','nc'])
        if os.path.isfile(savedir+savefilename):
            print(savefilename+' already exists. Not recalculating.')
        else:
            es = open_ensemble(variable,frequency,startyear=startyear,startmonth=startmonth,control=control,verbose=verbose)
            da = es[variable]
            da_out = calc_regionalmean_all(da,masks,grid['areacello'],verbose=verbose)
            print('Saving '+savefilename)
            da_out.to_netcdf(savedir+savefilename)