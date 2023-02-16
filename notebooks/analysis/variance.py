import information
from processing import *

import os
import xarray as xr
from dask.diagnostics import ProgressBar

def find_variance(variable,frequency,ensemble_or_control,startyear=None,startmonth=None):
    '''
    Determine if the variance file for the given [variable] at [frequency]
    has already been calculated. If so, return the path to the zarr file. If not, 
    return None.
    '''
    ppname = get_pathDict_control(variable,frequency)['ppname']
    outdir = '/'.join([ppeDict['datasavedir'],'processed',ensemble_or_control+'variance'])
    if startyear is None:
        outfile = '.'.join([ppname,'zarr'])
    else:
        outfile = '.'.join([ppname,str(startyear).zfill(4)+str(startmonth).zfill(2),'zarr'])
        
    if os.path.isfile('/'.join([outdir,outfile,variable,'0.0.0'])):
        print('/'.join([outdir,outfile,variable])+' already saved.')
        return outdir+'/'+outfile
    else:
        return None
    
def find_ppp(variable,frequency):
    '''
    Determine is ppp has already been calculated for [variable] at [frequency].
    If so, return path; if not return None.
    '''
    
    ppname = get_pathDict_control(variable,frequency)['ppname']
    outfile = '.'.join([ppname,'zarr'])
    outdir = '/'.join([ppeDict['datasavedir'],'processed','ppp'])
    if os.path.isfile('/'.join([outdir,outfile,variable,'0.0.0'])):
        print('/'.join([outdir,outfile,variable])+' already saved.')
        return outdir+'/'+outfile
    else:
        return None
    
def calc_evar(variable,frequency,startyear,startmonth,control,save=False,verbose=False):
    ''' Open all members of ensemble and calculate variance. '''
    
    evarpath = find_variance(variable,frequency,'ensemble',
                             startyear=startyear,startmonth=startmonth)
    if evarpath is not None:
        evar = xr.open_zarr(evarpath)
    else:
        ds = open_ensemble(variable,frequency,
                           startyear=startyear,startmonth=startmonth,
                           control=control,verbose=verbose)
        evar = ((ds.std(dim='member'))**2).chunk({'time':60})
        
        if save:
            print('Saving ensemble variance for '+str(startyear).zfill(4)+str(startmonth).zfill(2))
            # Save ensemble variance
            ppname = get_pathDict_control(variable,frequency)['ppname']
            outdir = '/'.join([ppeDict['datasavedir'],'processed','ensemblevariance'])
            outfile = '.'.join([ppname,str(startyear).zfill(4)+str(startmonth).zfill(2),'zarr'])
            with ProgressBar():
                evar.compute()
                evar.to_zarr(outdir+'/'+outfile,mode='a')
    return evar

def calc_evarmean(variable,frequency,startmonth=1,save=False,saveeach=False,verbose=False):
    ''' Load or calculate variance for each ensemble, and calculate mean variance.'''
    
    evarpath = find_variance(variable,frequency,'ensemble')
    if evarpath is not None:
        evarmean = xr.open_zarr(evarpath)
    else:
        print('Calculating mean ensemble variance.')
        print('Note : Ensure you are running with enough memory if trying to save.')
        # Open the control simulation (do it just once because it can take time)
        control = open_control(variable,frequency)
        # Loop through start years, calculate variance
        dd = [*range(len(ppeDict['startyears']))]
        for i,startyear in enumerate(ppeDict['startyears']):
            if verbose:
                print('Start year '+str(startyear))
            evar = calc_evar(variable,frequency,startyear=startyear,startmonth=startmonth,control=control,save=saveeach,verbose=verbose)
            if i==0:
                timenew = np.arange(len(evar['time']))
            dd[i]=evar.assign_coords({'time':timenew})
        evars = xr.concat(dd,dim='startyear').assign_coords({'startyear':ppeDict['startyears']})
        evarmean = evars.mean(dim='startyear')

        if save:
            if saveeach==True:
                print('Consider rerunning function to load saved variances, before saving mean.')
                print('This will save considerable time and memory.')
            print('Saving mean ensemble variance')
            # Save ensemble variance
            ppname = get_pathDict_control(variable,frequency)['ppname']
            outdir = '/'.join([ppeDict['datasavedir'],'processed','ensemblevariance'])
            outfile = '.'.join([ppname,'zarr'])
            with ProgressBar():
                evarmean.compute()
                evarmean.to_zarr(outdir+'/'+outfile,mode='a')
        
    return evarmean
    
def calc_cvar(variable,frequency,save=False,verbose=False):
    ''' Load or calculate variance for control simulation'''
    
    cvarpath = find_variance(variable,frequency,'control')
    if cvarpath is not None:
        cvar = xr.open_zarr(cvarpath)
    else:
        print('Calculating control variance.')
        control = open_control(variable,frequency)
        # Calculate the control variance
        tmp = (control.groupby('time.month').std()**2)
        # Broadcast to 10 repeating years
        montharray = np.tile(tmp['month'].to_numpy(),10)
        tmp = tmp.sel(month=montharray).rename({'month':'time'})
        cvar = tmp.assign_coords({'time':np.arange(len(tmp['time']))}).chunk({'time':60})
        
        if save:
            # Save control variance
            ppname = get_pathDict_control(variable,frequency)['ppname']
            outdir = '/'.join([ppeDict['datasavedir'],'processed','controlvariance'])
            outfile = '.'.join([ppname,'zarr'])
            with ProgressBar():
                cvar.to_zarr(outdir+'/'+outfile,mode='a')
        
    return cvar

def calc_ppp(variable,frequency,save=False,saveensemble=False,savecontrol=False,verbose=False):
    ppppath = find_ppp(variable,frequency)
    if ppppath is not None:
        ppp = xr.open_zarr(ppppath)
    else:
        print('Calculating PPP for '+variable)
        evarmean = calc_evarmean(variable,frequency,verbose=verbose,saveeach=saveensemble,save=saveensemble)
        cvar = calc_cvar(variable,frequency,save=savecontrol,verbose=verbose)
        ppp = 1-(evarmean/cvar)

        if save:
            ppname = get_pathDict_control(variable,frequency)['ppname']
            outdir = '/'.join([ppeDict['datasavedir'],'processed','ppp'])
            outfile = '.'.join([ppname,'zarr'])
            with ProgressBar():
                ppp.to_zarr(outdir+'/'+outfile,mode='a')
        
    return ppp