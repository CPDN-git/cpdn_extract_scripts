# Script to extract data from BATCH to a directory on the server where the data is stored
# Example paths are given for the GPFS filesystem on cpdn-ppc01 (data for upload2 in Oxford)
# Author: Sihan Li
# Modified: 08/09/2017
#

# Set up paths
EXTRACT_SCRIPTS_DIR=..
EXTRACT_DATA_DIR=/gpfs/projects/cpdn/scratch/cenv0628/extracted_hist/

# Current URL for uploads includes project and batch number
BATCH=619
PROJECT=tnc
DATA_DIR=/gpfs/projects/cpdn/storage/boinc/project_results/$PROJECT
BATCH_DATA_DIR=$DATA_DIR/batch_${BATCH}/successful/
# Specify a certain year to extract, if extract all years, set to 0
YEAR=2015

# Start and end zip to extract data from:
START_ZIP=2
END_ZIP=16

# Extract data from the batch directory ['ga.pd',5216,[],'all',-0.0001,1,24,'mean','z0'],\
$EXTRACT_SCRIPTS_DIR/wah_extract_local.py -i $BATCH_DATA_DIR \
-f "\
['ga.pe',15201,[],'all',-100,100,720,'mean','z7'],\
['ga.pe',15202,[],'all',-100,100,720,'mean','z7'],\
['ga.pe',16203,[],'all',150,400,720,'mean','z7'],\
['ga.pe',16202,[],'all',1000,15000,720,'mean','z7'],\
"  -o $EXTRACT_DATA_DIR/batch_${BATCH} -y $YEAR -s $START_ZIP -e $END_ZIP
