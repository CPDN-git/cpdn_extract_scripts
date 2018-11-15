#!/bin/bash

# Author: Sihan Li, 24/11/2017
# example script to take extracted wah2 regional model outputs onto a regular grid.

# if regional model resolution is 50km

cdo -remapbil,r720x360 inputfile.nc outputfile.nc

# if regional model resolution is 25km

cdo -remapbil,r1440x720 inputfile.nc outputfile.nc



