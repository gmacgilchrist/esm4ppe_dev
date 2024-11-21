#!/home/graemem/.conda/envs/climpred/bin/python
# Python file to preprocess growth limitation variables
import esm4ppe

control = True
ensemble = False
verify = False
regionalmean = False

phytotypes = ['diat','diaz','misc','pico']
limitations = ['limfe','limirr','limn','limp']
frequency = 'monthly'

for phytotype,limitation in zip(phytotypes,limitations):
    variable = limitation+phytotype
    print(variable)
    es = esm4ppe.esm4ppeObj(variable,frequency)
    if control:
        es = es.add_control(triggeropen=True)
    if ensemble:
        es = es.add_ensemble(triggeropen=True)
    if verify:
        es = es.verify('ppp',saveskill=True,groupby='month')