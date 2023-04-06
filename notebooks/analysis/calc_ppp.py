# Script to load and save variances for each variable at monthly resolution

import gfdl_utils as gu

from information import *
from processing import *
from variance import *

frequency='monthly'
# List of variables. If None, calculates for all available variables.
variables = ['siconc']
rechunk = {'time':-1}
startmonths = ppeDict['startmonths']

if variables is None:
    variables = get_allvars_ensemble(frequency)

for variable in variables:
    print('Calculating and saving ppp for : '+variable)
    for startmonth in startmonths:
        calc_evarmean(variable,
                      frequency,
                      startmonth=startmonth,
                      saveeach=True,
                      save=False,
                      rechunk=rechunk,
                      verbose=True)
        calc_ppp(variable,
                 frequency,
                 startmonth=startmonth,
                 save=True,
                 saveeachensemble=False,
                 saveensemblemean=True,
                 savecontrol=True,
                 rechunk=rechunk,
                 verbose=True)