# Script to extract data from BATCH to a remote server/ personal computer
#
# Set up paths
EXTRACT_SCRIPTS_DIR=..
EXTRACT_DATA_DIR=../extracted_data
BATCH=443
# Get List of URLS
if [ ! -f ./batch_${BATCH}.txt.gz ]; then 
  wget http://upload2.cpdn.org/results/batch_${BATCH}/batch_${BATCH}.txt.gz
fi
# Extact data from the list of URLS
$EXTRACT_SCRIPTS_DIR/wah_extract_wget.py -u ./batch_${BATCH}.txt.gz \
-f "\
['ma.pc',3236,[],'all',150,400,720,'maximum',''],\
['ma.pc',3236,[],'all',150,400,720,'minimum',''],\
['ma.pc',3236,[],'all',150,400,720,'mean',''],\
['ga.pe',5216,[],'all',-0.0001,1,720,'mean',''],\
['ga.pd',5216,[],'all',-0.0001,1,24,'mean','z0'],\
"  -o $EXTRACT_DATA_DIR/batch_${BATCH} -s 1 -e 2

