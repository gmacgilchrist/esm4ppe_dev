#!/bin/bash

root=/archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_piControl_D/gfdl.ncrc4-intel16-prod-openmp/pp

ppname=ocean_monthly
out=ts
local=monthly/5yr
time=0[2-4]*
var=sos

paths=${root}/${ppname}/${out}/${local}/${ppname}.${time}.${var}.nc

dmget ${paths} &