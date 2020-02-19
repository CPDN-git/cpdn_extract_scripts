#!/usr/bin/env python2.7
#############################################################################
# Program : compress_extracted_netcdf.py
# Author  : Sarah Sparrow
# Date    : 19/02/2020
# Purpose : Apply lossless compression to already extracted netcdf files
#           in the specified directory
#############################################################################

import os, sys, shutil
import argparse
import glob

def compress_netcdf(fname):
    os.system('nccopy -d 2 -s '+fname+' '+fname+'_compressed')
    shutil.move(fname+'_compressed',fname)

def main():
    #Read in the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="The directory containing the netCDF files you want to compress")

    args = parser.parse_args()
        
    iter_files=glob.iglob(os.path.join(args.dir,"*.nc"))

    for fname in iter_files:
        print("Compressing file "+fname)
        compress_netcdf(fname)


    print('Finished!')

#Washerboard function that allows main() to run on running this file
if __name__=="__main__":
  main()


