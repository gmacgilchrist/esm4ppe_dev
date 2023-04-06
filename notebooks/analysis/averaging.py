import xarray as xr
from processing import *
from dask.diagnostics import ProgressBar

# Functions for calculating means
def calc_regionalmean(da,mask,weights):
    dims = get_dimensionslesstime(da)
    return da.where(mask,drop=True).weighted(weights.fillna(0)).mean(dims)

def calc_regionalmean_all(da,masks,weights,verbose=False):
    ''' Calculate regional means for [da] based on [masks].
    Return DataArray with "region" dimension corresponding to masknames.'''
    coords_out = dict(da.coords)
    dims = get_dimensionslesstime(da)
    coords_out.pop(dims[0])
    coords_out.pop(dims[1])
    dims_orig = list(coords_out.keys())
    coords_out['region']=list(masks.keys())
    da_out = xr.DataArray(dims=coords_out.keys(),coords=coords_out,name=da.name)
        
    for name,mask in masks.items():
        print('region: '+name)
        if verbose:
            with ProgressBar():
                da_out.loc[{'region':name}] = calc_regionalmean(da,mask,weights).transpose(*dims_orig)
        else:
            da_out.loc[{'region':name}] = calc_regionalmean(da,mask,weights).transpose(*dims_orig)
    return da_out