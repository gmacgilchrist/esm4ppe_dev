# Script to load and save variances for each variable at monthly resolution

import gfdl_utils as gu

from information import *
from processing import *
from variance import *

frequency='monthly'
# List of variables. If None, calculates for all available variables.
variables = ['intpp','tos','sos','phos','chlos','chlos']

if variables is None:
    variables = get_allvars_ensemble(frequency)

for variable in variables:
    print('Calculating and saving ppp for : '+variable)
    calc_ppp(variable,'monthly',save=True, saveensemble=False, savecontrol=True, verbose=True)