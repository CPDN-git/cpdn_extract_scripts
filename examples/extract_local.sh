# Script to extract data from BATCH to a directory on the server where the data is stored
#
# Set up paths
EXTRACT_SCRIPTS_DIR=/home/cenv0437/cpdn_extract_scripts/
EXTRACT_DATA_DIR=/gpfs/projects/cpdn/scratch/cenv0437/extracted
BATCH=442
# Extact data from the list of URLS
$EXTRACT_SCRIPTS_DIR/wah_extract_local.py -i /gpfs/projects/cpdn/storage/boinc/upload/batch_${BATCH}/successful/ \
-f "\
['ma.pc',3236,[],'all',150,400,720,'maximum',''],\
['ma.pc',3236,[],'min',150,400,720,'minimum',''],\
['ma.pc',3236,[],'all',150,400,720,'mean',''],\
['ga.pe',5216,[],'all',-0.0001,1,720,'mean',''],\
['ga.pd',5216,[],'all',-0.0001,1,24,'mean','z0'],\
"  -o $EXTRACT_DATA_DIR/batch_${BATCH} -s 1 -e 2
