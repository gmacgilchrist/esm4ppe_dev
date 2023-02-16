import numpy as np
import re
import socket

global ppeDict
global ppcontrol

ppeDict = {
    'config_id_control':'ESM4_piControl_D',
    'prod':'gfdl.ncrc4-intel18-prod-openmp',
    'startyears': np.array([123,161,185,208,230,269,300,326,359,381]),
    'startmonths': np.array([1,4,7,10]),
    'gridfile':'/GRID/ocean.static.nc'
    }

### Machine-specific items
hostname = socket.gethostname()
if re.search('della',socket.gethostname()):
    ppeDict['rootdir']='/projects/SOCCOM/datasets/ESM4_PPE/archive/Richard.Slater/xanadu_esm4_20190304_mom6_ESM4_v1.0.3_rc1'
    ppeDict['datasavedir']='/projects/SOCCOM/graemem/projects/esm4_ppe/data'
    ppeDict['figsavedir']='/home/graemem/projects/esm4_ppe/figures'
elif re.search('an',socket.gethostname()):
    ppeDict['rootdir']='/archive/Richard.Slater/xanadu_esm4_20190304_mom6_ESM4_v1.0.3_rc1'
    ppeDict['datasavedir']='/work/gam/projects/esm4_ppe/data'
    ppeDict['figsavedir']='/home/gam/projects/esm4_ppe/figures'
    ppeDict['griddirtmp']='/work/gam/projects/esm4_ppe/data'    

ppcontrol = '/'.join([ppeDict['rootdir'],ppeDict['config_id_control'],ppeDict['prod'],'pp'])

### Specify basin masks
def generate_masks(grid):
    ''' Use grid basin and geolon and geolat to generate mask booleans for a range of ocean regions.'''
    masks = {}
    flag_values = grid['basin'].attrs['flag_values'].split(' ')
    flag_meanings = grid['basin'].attrs['flag_meanings'].split(' ')
    latbounds = np.array([-60, -45, -20, 20, 45, 60])
    latnames = ['SoP', 'SoSubP', 'SoSubT','T','NoSubT','NoSubP','NoP']
    lonbounds = np.array([-214,-68,20])
    lonnames = ['pacific','atlantic','indian']
    lonbounds_arctic = np.array([-220 , -50])
    lonnames_arctic = ['pacific','atlantic']

    for b in flag_values:
        bi = int(b)
        name = flag_meanings[bi].split('_')[0]
        masks[name]=(grid['basin']==bi)
        # Reverse boolean for land mask
        if name=='global':
            masks[name]=~masks[name]
        # Split up by latitudes
        for li,latname in enumerate(latnames):
            if (li == 0):
                newcond = (grid['geolat'] <= latbounds[li])
            elif (li == len(latnames)-1):
                newcond = (grid['geolat'] > latbounds[li-1])
            else:
                newcond = (grid['geolat'] > latbounds[li-1])  & (grid['geolat'] <= latbounds[li])
            masks[name+'_'+latname] = (masks[name]) & (newcond)
        # Split up Southern Ocean by longitude
        if name=='southern':
            for li,lonname in enumerate(lonnames):
                if li==len(lonnames)-1: # Wrap
                    newcond = (grid['geolon']>lonbounds[li]) | (grid['geolon']<lonbounds[0])
                else:
                    newcond = (grid['geolon']>lonbounds[li]) & (grid['geolon']<=lonbounds[li+1])
                masks[name+'_'+lonname] = (masks[name]) & (newcond) 
        # Split up Arctic Ocean by longitude
        if name=='arctic':
            for li,lonname in enumerate(lonnames_arctic):
                if li==len(lonnames_arctic)-1: # Wrap
                    newcond = (grid['geolon']>lonbounds_arctic[li]) | (grid['geolon']<lonbounds_arctic[0])
                else:
                    newcond = (grid['geolon']>lonbounds_arctic[li]) & (grid['geolon']<=lonbounds_arctic[li+1])
                masks[name+'_'+lonname] = (masks[name]) & (newcond)

    # Now build global basin masks
    for name in ['pacific','atlantic','indian']:
        masks[name+'_global']=masks[name].copy()
        r = re.compile(".*"+name)
        bs = list(filter(r.match, list(masks.keys())))
        for b in bs:
            masks[name+'_global']+=masks[b].copy()
            
    # Now remove any empty masks
    masksnow = masks.copy()
    for name, mask in masks.items():
        if ~mask.any():
            masksnow.pop(name)
            
    return masksnow

def get_masknames(masks):
    '''
    Subset mask names for only those masks that exist.
    For example, the red sea mask has no SoSubP mask.
    '''
    names = []
    for name, mask in masks.items():
        if mask.any():
            names.append(name)
    return names
    