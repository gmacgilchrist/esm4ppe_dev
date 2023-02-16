import xarray as xr
import numpy as np
import gfdl_utils as gu
from information import *
import os
import cftime
import re

def get_pp(getmember=False,startyear=None,startmonth=None,member=None):
    '''Get post process directory for either control run (default), or a specific member.'''
    if getmember:
        startdate = str(startyear).zfill(4)+str(startmonth).zfill(2)+'01'
        memberstr = str(member).zfill(2)
        config_id = '-'.join([ppeDict['config_id_control'],'ensemble',startdate,memberstr])
    else:
        config_id = ppeDict['config_id_control']
    return '/'.join([ppeDict['rootdir'],config_id,ppeDict['prod'],'pp'])

def get_pathDict_from_pp_variable_frequency(pp,variable,frequency,time='*',out='ts',constraint=None):
    '''
    Provided a pp path, an accurate variable name, and a specified frequency, return
    the desired entries to the pathDict dictionary for use in core.open_frompp.
    '''
    
    pathDict = {}
    # Specify pp
    pathDict['pp'] = pp
    # Specify variable
    pathDict['add'] = variable
    # Specify output type (always ts)
    pathDict['out'] = out
    # Specify time (always all times)
    pathDict['time'] = time
    
    # Find variable in ppnames
    ppnames = gu.core.find_variable(pathDict['pp'],pathDict['add'])
    if ppnames is None:
        print(variable+' not found. Returning pathDict so far.')
        return pathDict
    # Get correct ppname based on output frequency
    for ppname in gu.core.find_variable(pathDict['pp'],pathDict['add']):
        timefrequency = gu.core.get_timefrequency(pathDict['pp'],ppname)
        if constraint is None:
            # Find first with specified time frequency
            if timefrequency == frequency:
                pathDict['ppname'] = ppname
                break
        else:
            if (bool(re.search(constraint,ppname))) & (timefrequency == frequency):
                pathDict['ppname'] = ppname
                break
    if 'ppname' not in pathDict.keys():
        print(variable+' not found for a ppname that satisfies constraint and frequency. Returning pathDict so far.')
        return pathDict
    # Get local file structure
    pathDict['local'] = gu.core.get_local(pathDict['pp'],pathDict['ppname'],pathDict['out'])
    return pathDict

def get_pathDict_control(variable, frequency, constraint=None):
    '''
    Get pathDict for [variable] at [frequency] for control simulation.
    '''
    return get_pathDict_from_pp_variable_frequency(get_pp(),variable,frequency,constraint=constraint)

def get_pathDict_member(variable,frequency,startyear,startmonth,member, constraint=None):
    '''
    Get pathDict for [variable] at [frequency] for [startyear][member] simulation.
    '''
    pp=get_pp(getmember=True,startyear=startyear,startmonth=startmonth,member=member)
    return get_pathDict_from_pp_variable_frequency(pp,variable,frequency,constraint=constraint)
    
def open_control(variable,frequency):
    '''
    Open [variable] at [frequency] in the 300-year control simulation.
    '''
    pathDict = get_pathDict_control(variable, frequency)
    return gu.core.open_frompp(**pathDict)

def open_member(variable,frequency,startyear,startmonth,member):
    '''
    Open a specific ensemble member.
    '''
    pathDict = get_pathDict_member(variable,frequency,startyear,startmonth,member)
    return gu.core.open_frompp(**pathDict)

def open_ensemble(variable,frequency,startyear,startmonth,control=None,verbose=False):
    '''
    Open all members of a specific ensemble.
    '''
    # Specify number of members
    if control is None:
        nm = 9
    else:
        nm = 10
    dd = [*range(nm)]
    # Loop through members
    for member in np.arange(1,10):
        if verbose:
            print('Opening member '+str(member))
        dd[member]=open_member(variable,frequency,startyear,startmonth,member)
    # Add control
    if control is not None:
        if verbose:
            print('Adding control')
        dd[0] = control.sel(time=dd[1]['time'])
    return xr.concat(dd,dim='member').assign_coords({'member':np.arange(nm)})

def preprocess_climpred(ds,leadunits='months'):
    '''Make necessary adjustments to dataset for use with climpred package.'''
    nt = len(ds['time'])
    init = cftime.DatetimeNoLeap(ds['time.year'][0],ds['time.month'][0],1)
    
    ds = ds.rename({'time':'lead'}).assign_coords({'lead':np.arange(1,nt+1,1)})
    ds['lead'].attrs['units']=leadunits
    ds = ds.expand_dims({'init':[init]})
    ds = ds.chunk({'member':-1,'lead':-1})
    return ds

def get_allvars_ensemble(frequency):
    '''Return a list of all of the variables available for the ensembles with monthly frequency'''
    ppmember=get_pp(getmember=True,startyear=381,startmonth=1,member=1)
    vardict = gu.core.get_allvars(ppmember)
    variables = []
    for key in vardict.keys():
        timefrequency = gu.core.get_timefrequency(ppmember,key)
        if timefrequency==frequency:
            for variable in vardict[key]:
                variables.append(variable)
    return variables