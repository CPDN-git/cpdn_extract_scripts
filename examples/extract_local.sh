# Script to extract data from BATCH to a directory on the server where the data is stored
# Example paths are given for the GPFS filesystem on cpdn-ppc01 (data for upload2 in Oxford)
# Author: Peter Uhe
# Modified: 07/03/2017
#

# Set up paths
EXTRACT_SCRIPTS_DIR=..
EXTRACT_DATA_DIR=../extracted_data

# Current URL for uploads includes project and batch number
BATCH=500
PROJECT=science
BATCH_DATA_DIR=/gpfs/projects/cpdn/storage/boinc/project_results/$PROJECT/batch_${BATCH}/successful/
# Alternate form of the BATCH_LIST_URL (for older batches):
# BATCH_DATA_DIR=/gpfs/projects/cpdn/storage/boinc/results/batch_${BATCH}/successful/
# Alternate form of the BATCH_LIST_URL including model name (for EVEN older batches):
#MODEL=hadam3p_eu
# BATCH_DATA_DIR=/gpfs/projects/cpdn/storage/boinc/results/$MODEL/batch${BATCH}/

# Start and end zip to extract data from:
START_ZIP=1
END_ZIP=2

# Extract data from the batch directory
$EXTRACT_SCRIPTS_DIR/wah_extract_local.py -i $BATCH_DATA_DIR \
-f "\
['ma.pc',3236,[],'all',150,400,720,'maximum',''],\
['ma.pc',3236,[],'min',150,400,720,'minimum',''],\
['ma.pc',3236,[],'all',150,400,720,'mean',''],\
['ga.pe',5216,[],'all',-0.0001,1,720,'mean',''],\
['ga.pd',5216,[],'all',-0.0001,1,24,'mean','z0'],\
"  -o $EXTRACT_DATA_DIR/batch_${BATCH} -s $START_ZIP -e $END_ZIP