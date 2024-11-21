# A collection of functions for data processing
import xarray as xr

def calc_pearson(da1,da2,bymonth=False,deseasonalize=False,detrend=False):
    var1 = da1.name
    var2 = da2.name    
    ds = xr.merge([da1,da2])
    # bymonth
    if (bymonth):
        if ((deseasonalize) or (detrend)):
            raise Exception("Cannot apply deasoning or detrending while evaluating correlation by month")
        cr = ds.groupby('time.month').apply(_calc_pearson)
    else:
        # deseasonalize
        if deseasonalize:
            gb = ds.groupby('time.month')
            clim = gb.mean('time')
            ds = (gb - clim).chunk({'time':-1,'xh':'auto','yh':'auto'})
        # detrend
        if detrend:
            p = (ds-ds.mean('time')).polyfit(dim='time',deg=1)
            fit = xr.polyval(ds.time,p).rename({var1+'_polyfit_coefficients':var1,
                                                var2+'_polyfit_coefficients':var2})
            ds = ds-fit
        # correlation
        cr = _calc_pearson(ds)
    cr.name = '_'.join(['pearson','-'.join([var1,var2])])
    return cr

def _calc_pearson(ds):
    [var1,var2]=list(ds.data_vars)
    # correlation
    cr = xr.corr(ds[var1],ds[var2],dim='time')
    return cr

