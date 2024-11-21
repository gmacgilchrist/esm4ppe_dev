#!/home/graemem/.conda/envs/climpred/bin/python
# Python file to preprocess data for a number of variables
import esm4ppe

variables = ['intpp']
frequency = 'monthly'

for variable in variables:
    print(variable)
    es = esm4ppe.esm4ppeObj(variable,frequency)
    # open the ensemble and the control, save to zarr
    print("Adding control...")
    es = es.add_control(triggeropen=True)
    print("Adding ensemble...")
    es = es.add_ensemble(triggeropen=True)
    print("Calculating skill...")
    kw = {'comparison':'m2m','dim':["init", "member"],'groupby':'month'}
    es = es.verify(metric="acc",saveskill=True,**kw)
