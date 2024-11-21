#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[2]:


import esm4ppe
import gfdl_utils as gu


# In[3]:


# list possible variables
gu.core.get_allvars(esm4ppe.get_pp())['ocean_cobalt_omip_daily']


# In[4]:


variables = ['intpp']#'dfeos','chlos','zoocos','co3os','co3sataragos','co3satcalcos','phos','phycos','sios'] # must be in a list, even if only one variable
frequency = 'monthly'


# In[7]:


# This is suite of calculations/data processing that can be done
# Some selections are incompatible with one another, but this should be flagged below
# Further details for each step can be specified below
add_ensemble = True # load and add ensemble data
add_control = True # load and add control data
verify = False # calculate a skill metric
climatology = False # calculate seasonal climatology from control
regionalmean = True # calculate regional means of loaded or calculated datasets
# specify position where regional mean should be calculated
# if both are false then the regional mean is calculated at the end
regionalmeanbeforeverify = False # calculate regional means prior to verify
regionalmeanbeforeclimatology = False # calculate a regional means before climatology

### details ###
# add_ensemble details
writeensemble = False
checkwriteensemble = True

# add_control details
writecontrol = False
checkwritecontrol = True

# regionalmean details
masksname = 'basin'
omit= [] #['ensemble','control']
saveregionalmean=True
verbose=True
# checks on regionalmean logic
if (regionalmeanbeforeverify & (verify==False)) or (regionalmeanbeforeclimatology & (climatology==False)):
    raise Exception("Requesting regional mean prior to calculation that is not selected.")
if (regionalmean+regionalmeanbeforeverify+regionalmeanbeforeclimatology)>1:
    raise Exception("Only one of regionalmean, regionalmeanbeforeverify, and regionalmeanbeforeclimatology can be True.")
if (regionalmean or regionalmeanbeforeclimatology) & climatology & ('control' in omit):
    raise Exception("Calculating regionalmean for climatology while omitting the control simulation will come back empty")
    
# verify details
metric = 'ppp'
verify_kw = {'dim':'member'}
saveskill = True

# climatology details
if climatology & (add_control==False):
    raise Exception("Can't calculate the climatology without the control. Set add_control=True")


# In[8]:


print("Performing the following operations in order, for variables {"+', '.join(variables)+"} at frequency {"+frequency+"}: ")
if add_ensemble:
    print("- adding ensemble data to object")
if add_control:
    print("- adding control data to object")
if regionalmeanbeforeverify:
    print("- calculating means in regions {"+masksname+"} of all datasets present in object except {"+' and '.join(omit)+"}")
if verify:
    print("- calculating skill based on {"+metric+"}")
if regionalmeanbeforeclimatology:
    print("- calculating means in regions {"+masksname+"} of all datasets present in object except {"+' and '.join(omit)+"}")
if climatology:
    print("- calculating seasonal climatology of control")   
if regionalmean:
    print("- calculating means in regions {"+masksname+"} of all datasets present in object except {"+' and '.join(omit)+"}")


# In[ ]:


for variable in variables:
    print(variable)
    es = esm4ppe.esm4ppeObj(variable,frequency)
    if add_ensemble:
        es = es.add_ensemble(write=writeensemble,check=checkwriteensemble)
    if add_control:
        es = es.add_control(write=writecontrol,check=checkwritecontrol)
    if regionalmeanbeforeverify:
        es = es.regionalmean(masksname,omit,verbose=verbose,saveregionalmean=saveregionalmean)
    if verify:
        es = es.verify(metric,**verify_kw,saveskill=saveskill)
    if regionalmeanbeforeclimatology:
        es = es.regionalmean(masksname,omit,verbose=verbose,saveregionalmean=saveregionalmean)
    if climatology:
        es.climatology()
    if regionalmean:
        es = es.regionalmean(masksname,omit,verbose=verbose,saveregionalmean=saveregionalmean)


# In[ ]:




