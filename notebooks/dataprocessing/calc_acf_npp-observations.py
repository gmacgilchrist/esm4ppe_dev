import xarray as xr
import esmtools
from dask.diagnostics import ProgressBar
import os

nlags = 36
yearstart = 1998
yearend = 2014

basedir_out = "/projects/SOCCOM/graemem/projects/esm4_ppe/data/processed/observations/"
localdir_obs = "NPP-RyanKeogh/NPP_MLD-EN4.2.2-0.03/"

# Load observational data
basedir_obs = "/projects/SOCCOM/datasets/"
products = ["CAFE","CbPM1","CbPM2","EPPLEY","VGPM"]
suffix_obs = "_NPP_8D_25KM_1998_2022.nc"
ds = xr.Dataset()
for product in products:
    filename = product+suffix_obs
    ds[product] = xr.open_dataarray(basedir_obs+localdir_obs+filename,
                                    chunks = {'time':'auto','lat':'auto','lon':'auto'})

# subset time
ds = ds.sel(time=slice(str(yearstart)+"-01-01",str(yearend)+"-12-31"))

# deseasonalize
gb = ds.groupby("time.month")
dsa = gb - gb.mean(dim='time')
# detrend
p = (dsa-dsa.mean('time')).polyfit(dim='time',deg=1)
fit = xr.polyval(dsa.time,p)
for name in fit.data_vars:
    fit = fit.rename({name:name.split('_')[0]})
dsat = dsa-fit
# rechunk time
dsat = dsat.chunk({'time':-1,'lat':'auto','lon':'auto'})

# autocorrelation function
acf = esmtools.stats.autocorr(dsat,dim='time',
                              nlags=nlags,
                              xs_kwargs={"skipna":True})
acf = acf.assign_coords({'lead':range(nlags)})

# compute
import warnings
with ProgressBar():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        acf = acf.compute()

# save
filename = "AllProducts_8D_25KM_"+str(yearstart)+"_"+str(yearend)+"_acf.nc"
path = basedir_out+localdir_obs+filename
# remove if present
try:
    os.remove(path)
except OSError:
    pass
acf.to_netcdf(path,mode='w')