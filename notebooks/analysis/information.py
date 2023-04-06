import numpy as np
import re
import socket
import cftime

global ppeDict
global ppcontrol
global LMEorderK20
global ppp_threshold

ppeDict = {
    'config_id_control':'ESM4_piControl_D',
    'prod':'gfdl.ncrc4-intel18-prod-openmp',
    'startyears': np.array([123,161,185,208,230,269,300,326,359,381]),
    'startmonths': np.array([1,4,7,10]),
    'gridfile':'/GRID/ocean.static.nc',
    }

### Machine-specific items
hostname = socket.gethostname()
if re.search('della',socket.gethostname()):
    ppeDict['rootdir']='/projects/SOCCOM/datasets/ESM4_PPE/archive/Richard.Slater/xanadu_esm4_20190304_mom6_ESM4_v1.0.3_rc1'
    ppeDict['datasavedir']='/projects/SOCCOM/graemem/projects/esm4_ppe/data'
    ppeDict['figsavedir']='/home/graemem/projects/esm4_ppe/figures'
    ppeDict['pathLMEmask']='/projects/SOCCOM/datasets/LargeMarineEcos/derived_masks/LME66.ESM4.nc'
elif (re.search('an',socket.gethostname())) or (re.search('pp',socket.gethostname())):
    ppeDict['rootdir']='/archive/Richard.Slater/xanadu_esm4_20190304_mom6_ESM4_v1.0.3_rc1'
    ppeDict['datasavedir']='/work/gam/projects/esm4_ppe/data'
    ppeDict['figsavedir']='/home/gam/projects/esm4_ppe/figures'
    ppeDict['pathLMEmask']='/work/gam/LargeMarineEcos/derived_masks/LME66.ESM4.nc'
    ### TEMPORARY
    ppeDict['griddirtmp']='/work/gam/projects/esm4_ppe/data'   
    
ppeDict['rootdir_annual']=ppeDict['datasavedir']+'/raw/annualmeans'

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

def get_timeslice(startyear,startmonth):
    if startmonth in [4,7,10]:
        endyear = startyear+3
        endmonth = startmonth-1
    else:
        endyear = startyear+9
        endmonth = 12
    starttime = cftime.DatetimeNoLeap(startyear,startmonth,1)
    try:
        endtime = cftime.DatetimeNoLeap(endyear,endmonth,31)
    except:
        endtime = cftime.DatetimeNoLeap(endyear,endmonth,30)
    return slice(starttime,endtime)

### Ordering of LME systems from Krumhardt et al 2020, Figure 6
LMEorderK20 = ['California Current',
                'Gulf of California',
                'Gulf of Mexico',
                'Southeast U.S. Continental Shelf',
                'Insular Pacific-Hawaiian',
                'Pacific Central-American Coastal',
                'Caribbean Sea',
                'South Brazil Shelf',
                'East Brazil Shelf',
                'North Brazil Shelf',
                'Mediterranean Sea',
                'Canary Current',
                'Guinea Current',
                'Benguela Current',
                'Agulhas Current',
                'Somali Coastal Current',
                'Arabian Sea',
                'Bay of Bengal',
                'Gulf of Thailand',
                'South China Sea',
                'Sulu-Celebes Sea',
                'Indonesian Sea',
                'North Australian Shelf',
                'Northeast Australian Shelf',
                'East Central Australian Shelf',
                'South West Australian Shelf',
                'West Central Australian Shelf',
                'Northwest Australian Shelf',
                'East China Sea',
                'Kuroshio Current',
                'Gulf of Alaska',
                'Southeast Australian Shelf',
                'New Zealand Shelf',
                'Sea of Japan',
                'Oyashio Current',
                'Sea of Okhotsk',
                'West Bering Sea',
                'Antarctica',
                'Aleutian Islands',
                'Greenland Sea',
                'Yellow Sea',
                'Northern Bering - Chukchi Seas',
                'Beaufort Sea',
                'East Siberian Sea',
                'Laptev Sea',
                'Kara Sea',
                'Iceland Shelf and Sea',
                'Hudson Bay Complex',
                'Central Arctic',
                'Canadian High Arctic - North Greenland',
                'East Bering Sea',
                'Patagonian Shelf',
                'Norwegian Sea',
                'North Sea',
                'Celtic-Biscay Shelf',
                'Faroe Plateau',
                'Northeast U.S. Continental Shelf',
                'Scotian Shelf',
                'Labrador - Newfoundland',
                'Humboldt Current',
                'Canadian Eastern Arctic - West Greenland',
                'Barents Sea',
                'Iberian Coastal']

LMEArctic = ['Gulf of Alaska',
            'Aleutian Islands',
            'East Bering Sea',
            'West Bering Sea',
            'Northern Bering - Chukchi Seas',
            'East Siberian Sea',
            'Laptev Sea',
            'Kara Sea',
            'Barents Sea',
            'Norwegian Sea',
            'Greenland Sea',
            'Iceland Shelf and Sea',
            'Canadian Eastern Arctic - West Greenland',
            'Hudson Bay Complex',
            'Canadian High Arctic - North Greenland',
            'Beaufort Sea',
            'Central Arctic']

ppp_threshold = 0.235559205