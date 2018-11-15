#!/bin/bash

# Author: Sihan Li, 24/11/2017
# example script to convert other datasets(model, observation, reanalysis) to a certain wah2 regional model grid (given as txt files under the folder 'rotated_grid_txt_files')

cdo remapcon2,rot_grid_pnw25.txt inputfile.nc outputfile.nc

