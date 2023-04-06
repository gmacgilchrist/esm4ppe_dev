# Definition of class for working with ESM4 PPE data
rootdir = {'archive':'/archive/Richard.Slater/',
           'work':'/work/gam/projects/esm4_ppe/'
          'home':'/home/gam/projects/esm4_ppe/'}
directories = {
    'ensembles':{
        'monthly':rootdir['archive'],
        'annual':rootdir['work']+'/data/raw'
    },
    'skill':rootdir['work']+'/data/processed/skill'
}
configid_control = 'ESM4_piControl_D'

root

class esm4ppe(variables,frequency):
    def __init__():
        
        dirs = {ensembles,
                skills,
               }
        
        get_config_id(startyear=None,startmonth=None,member=None)
        get_rootdir(frequency)
        get_ensembleid(startyear,startmonth)
        
        # Initialize 
        ppdirs={startyear}
        
        pm = cp.PerfectModelEnsemble(ensembles).add_control(control)
        
def get_ensembleid(startyear,startmonth):
    return str(startyear).zfill(4)+str(startmonth).zfill(2)+'01'

def get_memberid(startyear,startmonth,member):
    return '-'.join([get_ensembleid(startyear,startmonth),str(member).zfill(2)])

def get_configid(startyear=None,startmonth=None,member=None):
    if [startyear,startmonth,member].all():
        return configid_control
    else:
        return '-'.join([configid_control,'ensemble',get_memberid(startyear,startmonth,member)])
    
def get_pp(variable,frequency,configid):
    
        