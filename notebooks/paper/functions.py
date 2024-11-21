import xarray as xr
import cartopy.crs as ccrs
import numpy as np
from xhistogram.xarray import histogram
import matplotlib.pyplot as plt

plt.rcParams['text.usetex'] = True

### FIGURE SAVING
def save_fig(fig,filename):
    savedir = '.'
    fig.patch.set_facecolor('white')
    fig.savefig('/'.join([savedir,filename])+'.png',dpi=300,transparent=True,bbox_inches='tight')

### PLOTTING
def draw_globalplot(ax,da,**kw_args):
    im = ax.pcolormesh(da['lon'],da['lat'],da,transform=ccrs.PlateCarree(),**kw_args)
    return im,ax

def draw_globalplot_esm4(ax,da,static,**kw_args):
    im = ax.pcolormesh(static["geolon"],static["geolat"],da,transform=ccrs.PlateCarree(),**kw_args)
    return im,ax

def add_colorbar(fig,im,position,tick_position='top',orientation='horizontal'):
    axcb = fig.add_axes(position)
    imcb = fig.colorbar(im,orientation=orientation,cax=axcb)
    axcb.xaxis.set_ticks_position(tick_position)
    return axcb, imcb

def draw_zonalmeans(ax,da,threshold=None,**kwargs):
    im = ax.pcolormesh(da['lead'],da['geolat_bin'],da.transpose(),shading='auto',**kwargs)
    if threshold is not None:
        mask = (da<threshold)
        ax.contourf(da['lead'],da['geolat_bin'],mask.transpose(), 1, hatches=['', '///'], alpha=0)
    ax.set_xlim([-0.5,35.5])
    ax.set_xlabel('Lead time [months]')
    ax.set_ylabel('Latitude [$^\circ N$]')
    return ax,im


### PROCESSING

def _calc_maxlims(cr,static):
    """
    Calculate the maximum correlation across the growth limitation factors
    
    INPUT
    ---
    cr : xr.Dataset
        Dataset with arrays corresponding to the Pearson correlation coefficients for each of the growth
        limitation factors. Form of data arrays is 'pearson_intpp<phytotype>-<limitation><phytotype>.
    static : xr.Dataset
        Model static file
        
    RETURNS
    ---
    maxlims : xr.DataArray
        Array with number index of max limitation factor
    lims : list
        List of limitation factor names, with index corresponding to values in the maxlims array
    """
    variables = cr.data_vars
    # extract phytotype
    phytotype = list(set([v[-4:] for v in variables]))
    if len(phytotype)>1:
        raise Exception("Function _calc_maxlims is written to work on one phytoplankton type at a time."+
                        "Use calc_maxlims_allphyto to calculate for multiple types.")
    else:
        phytotype=phytotype[0] # take it out of a list
    # extract names of limitations
    limnames = [v.split('-')[1][:-4] for v in variables]
    # stack the correlations arrays for each limitaion along a new 'lims' dimension and assign the names
    limsarray = cr.to_array('lims',name=phytotype).assign_coords({'lims':limnames})
    # find the maximum correlation along the lims dimension
    maxlims = limsarray.fillna(-9999).argmax(dim='lims').where(static['wet']==1)
    return maxlims,limnames

def calc_maxlims_allphyto(cr,static):
    """
    Calculate the maximum correlation across the growth limitation factors for all phytoplankton types.
    INPUT
    ---
    cr : xr.Dataset
        Dataset with arrays corresponding to the Pearson correlation coefficients for each of the growth
        limitation factors for a suite of phytoplankton types.
        Form of data arrays is 'pearson_intpp<phytotype>-<limitation><phytotype>.
    static : xr.Dataset
        Model static file
        
    RETURNS
    ---
    maxlims : xr.DataSet
        Dataset with arrays corresponding to each phytotype present in cr.
        Each array has number index of max limitation factor
    lims : dict
        List of limitation factor names for each phytotype, with index corresponding to values in the maxlims array
    """
    
    maxlims = xr.Dataset()
    limnames = {}
    
    # extract phytotypes
    phytotypes = list(set([v[-4:] for v in cr.data_vars]))
    for phytotype in phytotypes:
        # get the names of the variables for this phytotype
        variables = [l for l in cr.data_vars if phytotype in l]
        maxlims[phytotype], limnames[phytotype] = _calc_maxlims(cr[variables],static)
    return maxlims,limnames

def calc_timehorizon(da,threshold,dim='lead',smooth=None,):
    ''' Find time at which value of [da] drops below [threshold], moving forward in time.
    If it never drops below threshold, np.max(time)+1 is returned.'''
    if smooth is not None:
        tmp = da.rolling({dim:smooth},center=True,min_periods=1).mean()
    else:
        tmp = da.copy()
    return xr.where(tmp<threshold, tmp[dim],np.max(da[dim])+1).min(dim=dim,skipna=True)

def calc_zonalmean(da,mask,weights,geolat,lat_bins):
    hs_daw = histogram(geolat.where(mask,drop=True),
                       bins=[lat_bins],
                       weights=(da*weights).fillna(0).where(mask,drop=True),
                       dim=['xh','yh'],
                       keep_coords=True)
    hs_w = histogram(geolat.where(mask,drop=True),
                     bins=[lat_bins],
                     weights=weights.fillna(0).where(mask,drop=True),
                     dim=['xh','yh'],
                     keep_coords=True)
    if 'month' in da.dims:
        coord_assign = {'month':np.array([1,4,7,10]),
                        'lead':np.arange(0,120)}
    else:
        coord_assign = {'lead':np.arange(0,120)}
        
    return ((hs_daw/hs_w).
            assign_coords(**coord_assign))

