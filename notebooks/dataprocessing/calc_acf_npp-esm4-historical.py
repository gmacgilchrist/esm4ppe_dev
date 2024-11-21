import xarray as xr
import esmtools
from dask.diagnostics import ProgressBar
import gfdl_utils as gu
import os

nlags = 36

# path specifics
variable = "tos"
yearstart = 1998
yearend = 2014

basedir_out = "/projects/SOCCOM/graemem/projects/esm4_ppe/data/processed/esm4historical"
yearstr = "_".join([str(yearstart),str(yearend)])
filename_prefix = ".".join(["ESM4_historical_D1",yearstr])
filename_suffix = ".".join([variable,"nc"])

# Load esm4 data
pathDict = {"pp":"/projects/SOCCOM/datasets/archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp",
           "add":v}
pathDict["ppname"] = gu.core.find_variable(pathDict["pp"],pathDict["add"])[0]
pathDict["out"]="ts"
pathDict["local"]=gu.core.get_local(pathDict["pp"],pathDict["ppname"],pathDict["out"])
pathDict["time"]="*"
path = gu.core.get_pathspp(**pathDict)
ds = xr.open_mfdataset(path).sel(time=slice(str(yearstart)+"-01-01",str(yearend)+"-12-31"))
ds = ds.chunk({'time':-1,'xh':'auto','yh':'auto'}).drop_vars(['average_DT','time_bnds']).drop_dims('nv')

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
dsat = dsat.chunk({'time':-1,'xh':'auto','yh':'auto'})

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
filename = ".".join([filename_prefix,"acf",filename_suffix])
outpath = "/".join([basedir_out,filename])
# remove if present
try:
    os.remove(outpath)
except OSError:
    pass
acf.to_netcdf(outpath,mode='w')