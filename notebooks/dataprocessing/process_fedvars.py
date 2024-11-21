#!/nbhome/gam/miniconda3/envs/climpred_clean/bin/python
# Python file to preprocess data for a number of variables
import esm4ppe
import gfdl_utils as gu

variables = ['dfeos',
             'dep_dry_fed',
             'dep_dry_lith',
             'dep_wet_fed',
             'dep_wet_lith',
             'ffe_iceberg',
             # 'dfe',
             'MLD_003',
             'limfediat','limfepico','limfemisc','limfediaz']
frequency = 'monthly'

for variable in variables:
    print(variable)
    es = esm4ppe.esm4ppeObj(variable,frequency)
    # open the ensemble and the control, save to zarr
    es = es.add_ensemble(triggeropen=True).add_control(triggeropen=True)
    # calculate ppp and save
    es = es.verify(metric='ppp',saveskill=True,groupby='month')
    # calculate regional means and save
    es = es.regionalmean('basin',omit=['ensemble'],saveregionalmean=True)