# Script to load and save variances for each variable at monthly resolution

import gfdl_utils as gu

from information import *
from processing import *
from variance import *

# Use directory for first ensemble to get names of variables
ppmember=get_pp(getmember=True,startyear=123,startmonth=1,member=1)

frequency='monthly'
vardict = gu.core.get_allvars(ppmember)
for key in vardict:
    timefrequency = gu.core.get_timefrequency(ppcontrol,key)
    if timefrequency==frequency:
        for variable in vardict[key]:
            print('Calculating and saving variance for : '+variable)
            calc_evarmean(variable,'monthly',saveeach=True,verbose=True)
            calc_evarmean(variable,'monthly',save=True)