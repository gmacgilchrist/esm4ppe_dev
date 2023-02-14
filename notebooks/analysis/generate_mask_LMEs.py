import geopandas as gpd
from information import *
import xarray as xr
from shapely.geometry import Point
import numpy as np

rootdir = '/projects/SOCCOM/datasets/LargeMarineEcos/LME66/'
filename = 'LMEs66.shp'
df = gpd.read_file(rootdir+filename)
grid = xr.open_dataset(ppeDict['rootdir']+ppeDict['gridfile'])
# Reorganize geolon coordinate
grid['geolon'] = grid['geolon'].where(grid['geolon']>-180,grid['geolon']+360)

ds = xr.Dataset(coords=grid['geolon'].coords)
gridx,gridy = grid['geolon'].values,grid['geolat'].values
xy_arr = np.vstack((gridx.ravel(), gridy.ravel())).T
# Set up numpy dictionary
inside_dict = {}
for index,row in df.iterrows():
    name = row['LME_NAME']
    inside_dict[name]=np.zeros(shape = len(xy_arr))
# Populate np arrays with boolean based on whether point in polygon
for i,xy in enumerate(xy_arr):
    if i%100==0:
        print(str(i)+' of '+str(len(xy_arr)))
    for name,inside in inside_dict.items():
        poly = df[df['LME_NAME']==name]['geometry'].iloc[0]
        inside[i]=poly.contains(Point(xy))
# Reshape boolean and store in Dataset
for name,inside in inside_dict.items():
    da=xr.DataArray(inside.reshape(gridx.shape).T,dims=ds.dims,coords=ds.coords)
    ds[name]=da
    
ds.to_netcdf(ppeDict['datasavedir']+'raw/LME66.ESM4.nc')