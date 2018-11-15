# Script to extract data from BATCH to a remote server/ personal computer, to extract only Windows Returns
# Author: Sihan Li
# Modified: 22/11/2017
# Set up paths
EXTRACT_SCRIPTS_DIR=..
EXTRACT_DATA_DIR=../extracted_data

# Current URL for uploads includes project and batch number
BATCH=608
PROJECT=happi
BATCH_LIST_URL=http://upload2.cpdn.org/project_results/$PROJECT/batch_${BATCH}/batch_${BATCH}.txt.gz
# Alternate form of the BATCH_LIST_URL (for older batches):
#BATCH_LIST_URL=http://upload2.cpdn.org/results/batch_${BATCH}/batch_${BATCH}.txt.gz
# Alternate form of the BATCH_LIST_URL including model name (for EVEN older batches):
#MODEL=hadam3p_eu
#BATCH_LIST_URL=http://upload2.cpdn.org/results/$MODEL/batch${BATCH}/batch${BATCH}.txt.gz

# Specify a certain year to extract, if extract all years, set to 0
YEAR=2015

# Start and end zip to extract data from:
START_ZIP=2
END_ZIP=2

# Get List of URLS
if [ ! -f ./batch_${BATCH}.txt.gz ]; then 
  wget -O batch_${BATCH}.txt.gz $BATCH_LIST_URL
fi

rm ../batch_${BATCH}_successful_wus_os.csv
wget https://www.cpdn.org/batch/batch_${BATCH}_successful_wus_os.csv
mv batch_${BATCH}_successful_wus_os.csv ../

# Extact data from the list of URLS
$EXTRACT_SCRIPTS_DIR/wah_extract_wget_Windows.py -u ./batch_${BATCH}.txt.gz \
-f "\
['ga.pe',5216,[],'all',-0.0001,1,720,'mean',''],\
"  -o $EXTRACT_DATA_DIR/batch_${BATCH} -b $BATCH -y $YEAR -s $START_ZIP -e $END_ZIP
