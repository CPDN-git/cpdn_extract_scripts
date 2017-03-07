# cpdn_extract_scripts
###Scripts for extraction of climateprediction.net data

- wah_extract_local.py is for extraction of data on machines that have direct access to the data

- wah_extract_wget.py is for extraction of data on remote machines by first downloading the zip files off the server

## Installation:

First clone the repository using git. i.e. $git clone https://github.com/pfuhe1/cpdn_extract_scripts.git

### Dependencies
Requires python2.7 with packages: numpy, netCDF4

### Suggested installation of dependancies using miniconda
Miniconda is a stand alone package containing python, enabling users to create environments with the packages they require on a system where they don't have control of the system python installation.

 1. Download miniconda installer from https://conda.io/miniconda.html
 1. Install miniconda to home directory (following directions on website above)
 1. Close and reopen your terminal so your envionment is updated
 1. Install numpy and netCDF4 to your miniconda environment: run $conda install numpy netCDF4

Now you should be ready to go when you run the python scripts. 


## Command line arguments are:

wah_extract_local.py ONLY:
- -i / --in_dir: input directory containing subfolders for each task (e.g. /gpfs/projects/cpdn/storage/boinc/upload/batch_440/successful/)

wah_extract_wget.py ONLY:
- -u / --urls_file: File containing list of urls of zip files (in gzipped format)

BOTH SCRIPTS:
- -o / --out_dir: output directory for extracted data
- -s / --start_zip: First zip to extract
- -e / --end_zip: Last zip to extract
- -f / --fields: List of (comma separated) fields to extract

# Each field entry has the format:
-        [file_stream,stash_code,[region],process,valid_min,valid_max,time_freq,cell_method,vert_lev]'

where:
-        file_stream = ga.pd|ga.pe|ma.pc
-        stash_code  = stash_section * 1000 + stash_item
-        [region]    = [lon_NW,lat_NW,lon_SW,lat_SW] or []
-        process     = time post_processing: min|max|mean|sum|all
-        time_freq   = input variable data frequency in hours (e.g. 24=daily, 720=monthly)
-        cell_method = input variable time cell method: minimum,maximum,mean
-        vert_lev    = input variable name of vertical level in netcdf file or ''

# Examples can be found in the examples folder:
Note that older batches use a different directories structure, so the examples have a few different options (commented out)


