# Author: Sihan Li
# Modified: 22/11/2017
# Example script to extract ONLY Windows returns

# Set up paths
EXTRACT_SCRIPTS_DIR=..
EXTRACT_DATA_DIR=/gpfs/projects/cpdn/scratch/cenv0628/extracted_hist/

# Current URL for uploads includes project and batch number
BATCH=608
BATCH_DATA_DIR=/gpfs/projects/cpdn/storage/boinc/project_results/happi/batch_${BATCH}/successful/
# grab the csv file (which contains the list of break down by os systems)
rm ../batch_${BATCH}_successful_wus_os.csv
wget https://www.cpdn.org/batch/batch_${BATCH}_successful_wus_os.csv
mv batch_${BATCH}_successful_wus_os.csv ../

# Start and end zip to extract data from:
START_ZIP=2
END_ZIP=2
Year=2015
$EXTRACT_SCRIPTS_DIR/wah_extract_local_Windows.py -i $BATCH_DATA_DIR \
-f "\
['ga.pe',5216,[],'all',-0.0001,1,720,'mean',''],\
"  -o $EXTRACT_DATA_DIR/batch_${BATCH} -b $BATCH -y $Year -s $START_ZIP -e $END_ZIP
