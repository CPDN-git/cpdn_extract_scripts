# cpdn_extract_scripts
###Scripts for extraction of climateprediction.net data

- wah_extract_local.py is for extraction of data on machines that have direct access to the data

- wah_extract_wget.py is for extraction of data on remote machines by first downloading the zip files off the server

## Installation:

First clone the repository using git. i.e. $git clone https://github.com/CPDN-git/cpdn_extract_scripts

### Dependencies
Requires python2.7 with packages: numpy, netCDF4

### Suggested installation of dependancies using miniconda
Miniconda is a stand alone package containing python, enabling users to create environments with the packages they require on a system where they don't have control of the system python installation.

 - If miniconda is already installed on a shared system e.g. by a system administrator, create a conda environment: 
    ```
    conda create --name pyenv python=2.7
    source activate pyenv
    conda install -y numpy
    conda install -y netCDF4
    ```
    NOTE: you will have to run '$source activate pyenv' each time you create a new terminal before you run the scripts. 

 - If you don't already have miniconda:
   1. Download miniconda installer from https://conda.io/miniconda.html
   2. Install miniconda to home directory (following directions on website above)
   3. Close and reopen your terminal so your envionment is updated
   4. Install numpy and netCDF4 to your miniconda environment:
   ```
   conda install numpy netCDF4
   ```

Now you should be ready to go when you run the python scripts. 


## Command line arguments are:

wah_extract_local.py ONLY:
- -i / --in_dir: input directory containing subfolders for each task (e.g. /gpfs/projects/cpdn/storage/boinc/upload/batch_440/successful/)
Please Note: need to include the '/' as the end of the input directory name
wah_extract_wget.py ONLY:
- -u / --urls_file: File containing list of urls of zip files (in gzipped format)

BOTH SCRIPTS:
- -o / --out_dir: output directory for extracted data
- -y / --year: Specify a certain year to extract, if need to extract all, set to 0
- -s / --start_zip: First zip to extract
- -e / --end_zip: Last zip to extract
- -f / --fields: List of (comma separated) fields to extract
- --output-freq: Output frequency of model data zips [month|year], defaults to month
- --structure: Directory structure of extracted data (after output directory) Options for structure are: 
   std (default): out_dir/region[_subregion]/variable/
   startdate-dir: out_dir/region[_subregion]/variable/startdate
   Where: region is [ocean,atmos,region] (depending on the file stream), startdate is yyyymm

## Each field entry has the format:
-        [file_stream,stash_code,[subregion],process,valid_min,valid_max,time_freq,cell_method,vert_lev]'

where:
-        file_stream = ga.pd|ga.pe|ma.pc
-        stash_code  = stash_section * 1000 + stash_item
-        [subregion]    = [lon_NW,lat_NW,lon_SE,lat_SE] or []
-        process     = time post_processing: min|max|mean|sum|all
-        time_freq   = input variable data frequency in hours (e.g. 24=daily, 720=monthly)
-        cell_method = input variable time cell method: minimum,maximum,mean
-        vert_lev    = input variable name of vertical level in netcdf file or ''

## Examples can be found in the examples folder:
Note that older batches use a different directories structure, so the examples have a few different options (commented out)


