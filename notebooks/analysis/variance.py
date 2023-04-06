import information
from processing import *

import os
import glob
import xarray as xr
import climpred as cp
cp.set_options(PerfectModel_persistence_from_initialized_lead_0=True)
from dask.diagnostics import ProgressBar

def find_variance(variable,frequency,ensemble_or_control,startmonth=None,startyear=None):
    '''
    Determine if the variance file for the given [variable] at [frequency]
    has already been calculated. If so, return the path to the zarr file. If not, 
    return None.
    '''
    ppname = get_pathDict_control(variable,frequency)['ppname']
    outdir = '/'.join([ppeDict['datasavedir'],'processed',ensemble_or_control+'variance'])
    if startyear is None:
        if (ensemble_or_control=='control'):
            outfile = '.'.join([ppname,'zarr'])
        if startmonth is None:
            ValueError('Returning mean ensemble variance requires that you specify a start month.')
        else:
            outfile = '.'.join([ppname,'mean'+str(startmonth).zfill(2),'zarr'])
    else:
        outfile = '.'.join([ppname,str(startyear).zfill(4)+str(startmonth).zfill(2),'zarr'])
        
    if os.path.isfile('/'.join([outdir,outfile,variable,'0.0.0'])):
        print('/'.join([outdir,outfile,variable])+' already saved.')
        return outdir+'/'+outfile
    else:
        return None
    
def find_ppp(variable,frequency,startmonth):
    '''
    Determine is ppp has already been calculated for [variable] at [frequency].
    If so, return path; if not return None.
    '''
    return find_skill(variable,frequency,startmonth)

    # ppname = get_pathDict_control(variable,frequency)['ppname']
    # outfile = '.'.join([ppname,str(startmonth).zfill(2),'zarr'])
    # outdir = '/'.join([ppeDict['datasavedir'],'processed','ppp'])
    # if os.path.isfile('/'.join([outdir,outfile,variable,'0.0.0'])):
    #     print('/'.join([outdir,outfile,variable])+' already saved.')
    #     return outdir+'/'+outfile
    # else:
    #     return None
    
def find_skill(variable,frequency,startmonth,metric='ppp',comparison='e2c'):
    '''
    Determine if [metric] has already been calculated for [variable] at [frequency].
    If so, return path; if not return None.
    '''
    
    ppname = get_pathDict_control(variable,frequency)['ppname']
    outdir = '/'.join([ppeDict['datasavedir'],'processed','skill',metric+'.'+comparison])
    outfile = '.'.join([ppname,str(startmonth).zfill(2),'zarr'])
    if len(glob.glob('/'.join([outdir,outfile,variable,'*'])))!=0:
        print('/'.join([outdir,outfile,variable])+' already saved.')
        return outdir+'/'+outfile
    else:
        return None
    
def calc_evar(variable,frequency,startyear,startmonth,control,save=False,rechunk={'time':1},verbose=False):
    ''' Open all members of ensemble and calculate variance. '''
    
    evarpath = find_variance(variable,frequency,'ensemble',
                             startyear=startyear,startmonth=startmonth)
    if evarpath is not None:
        evar = xr.open_zarr(evarpath)
    else:
        ds = open_ensemble(variable,frequency,
                           startyear=startyear,startmonth=startmonth,
                           control=control,rechunk=rechunk,verbose=verbose)
        evar = ((ds.std(dim='member'))**2)
        
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

def calc_evarmean(variable,frequency,startmonth=None,save=False,saveeach=False,rechunk={'time':1},verbose=False):
    ''' Load or calculate variance for each ensemble, and calculate mean variance.'''
    
    evarpath = find_variance(variable,frequency,'ensemble',startmonth=startmonth)
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
            evar = calc_evar(variable,
                             frequency,
                             startyear=startyear,
                             startmonth=startmonth,
                             control=control,
                             save=saveeach,
                             rechunk=rechunk,
                             verbose=verbose)
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
            outfile = '.'.join([ppname,'mean'+str(startmonth).zfill(2),'zarr'])
            with ProgressBar():
                evarmean.compute()
                evarmean.to_zarr(outdir+'/'+outfile,mode='a')
        
    return evarmean
    
def calc_cvar(variable,frequency,save=False,rechunk={'time':1},verbose=False):
    ''' Load or calculate variance for control simulation'''
    
    cvarpath = find_variance(variable,frequency,'control')
    if cvarpath is not None:
        cvar = xr.open_zarr(cvarpath)
    else:
        print('Calculating control variance.')
        control = open_control(variable,frequency,rechunk=rechunk)
        # Calculate the control variance
        if frequency=='monthly':
            tmp = (control.groupby('time.month').std()**2)
            # Broadcast to 10 repeating years
            montharray = np.tile(tmp['month'].to_numpy(),10)
            tmp = tmp.sel(month=montharray).rename({'month':'time'})
            cvar = tmp.assign_coords({'time':np.arange(len(tmp['time']))}).chunk(**rechunk)
        elif frequency=='annual':
            tmp = (control.std('time')**2).expand_dims({'time':1})
            tmp = tmp.isel(time=[0]*10)
            cvar = tmp.assign_coords({'time':np.arange(len(tmp['time']))}).chunk(**rechunk)
        
        if save:
            # Save control variance
            ppname = get_pathDict_control(variable,frequency)['ppname']
            outdir = '/'.join([ppeDict['datasavedir'],'processed','controlvariance'])
            outfile = '.'.join([ppname,'zarr'])
            with ProgressBar():
                cvar.to_zarr(outdir+'/'+outfile,mode='a')
        
    return cvar

def calc_ppp(variable,frequency,startmonth,save=False,saveeachensemble=False,saveensemblemean=False,savecontrol=False,rechunk={'time':1},verbose=False):
    ppppath = find_skill(variable,frequency,startmonth)
    if ppppath is not None:
        ppp = xr.open_zarr(ppppath)
    else:
        print('Calculating PPP for '+variable)
        evarmean = calc_evarmean(variable,
                                 frequency,
                                 startmonth=startmonth,
                                 verbose=verbose,
                                 saveeach=saveeachensemble,
                                 save=saveensemblemean,
                                rechunk=rechunk)
        cvar = calc_cvar(variable,frequency,save=savecontrol,rechunk=rechunk,verbose=verbose)
        cvar = cvar.shift(time=-1*(startmonth-1))
        ppp = 1-(evarmean/cvar)

        if save:
            ppname = get_pathDict_control(variable,frequency)['ppname']
            outdir = '/'.join([ppeDict['datasavedir'],'processed','skill','ppp.e2c'])
            outfile = '.'.join([ppname,str(startmonth).zfill(2),'zarr'])
            with ProgressBar():
                ppp.to_zarr(outdir+'/'+outfile,mode='a')
        
    return ppp

def calc_skill(variable,frequency,startmonth,metric='ppp',comparison='e2c',reference=None,save=False,verbose=False):
    '''
    Calculate skill using climpred package
    '''
    skillpath = find_skill(variable,frequency,startmonth,metric,comparison)
    if skillpath is not None:
        skill = xr.open_zarr(skillpath)
    else:
        print('Calculating '+metric+' for '+variable)
        control = open_control(variable,frequency)
        ensembles = open_ensembles_climpred(variable,
                                            frequency,
                                            startyears=ppeDict['startyears'],
                                            startmonth=startmonth,
                                            control=control,
                                            verbose=verbose).chunk({'init':-1})
        if 'time_bnds' in ensembles.data_vars:
            ensembles = ensembles.drop_vars('time_bnds')
        if 'nv' in ensembles.dims:
            ensembles = ensembles.drop_dims('nv')
        pm = cp.PerfectModelEnsemble(ensembles)

        skill = pm.verify(
            metric=metric, 
            comparison=comparison, 
            dim=["init", "member"],
            reference=reference)
        
        if save:
            ppname = get_pathDict_control(variable,frequency)['ppname']
            outdir = '/'.join([ppeDict['datasavedir'],'processed','skill',metric+'.'+comparison])
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            outfile = '.'.join([ppname,str(startmonth).zfill(2),'zarr'])
            with ProgressBar():
                skill.to_zarr(outdir+'/'+outfile,mode='a')
    return skill