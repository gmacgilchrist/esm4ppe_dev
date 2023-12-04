# Script to load and save variances for each variable at monthly resolution

import gfdl_utils as gu

from information import *
from processing import *
from variance import *

frequency='monthly'
# List of variables. If None, calculates for all available variables.
variables = ['intpp','phos','chlos','o2os','tos','sos','MLD_003']

if variables is None:
    variables = get_allvars_ensemble(frequency)

for variable in variables:
    print('Calculating and saving variance for : '+variable)
    for startmonth in ppeDict['startmonths']:
        # Running command twice - first to save individual ensemble variances,
        # and second to save mean variance - actually saves I/O time.
        calc_evarmean(variable,frequency,startmonth=startmonth,saveeach=True,save=False,verbose=True)
        calc_evarmean(variable,frequency,startmonth=startmonth,save=True)