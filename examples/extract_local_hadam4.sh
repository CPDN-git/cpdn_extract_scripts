# Script to extract data from BATCH to a directory on the server where the data is stored
# Example paths are given for the GPFS filesystem on cpdn-ppc01 (data for upload2 in Oxford)
# Author: Sihan Li
# Modified: 08/09/2017
#

# Set up paths
EXTRACT_SCRIPTS_DIR=..
EXTRACT_DATA_DIR=/gws/nopw/j04/docile/scratch/ssparrow/

# Current URL for uploads includes project and batch number
BATCH=d196
PROJECT=docile
DATA_DIR=/gws/nopw/j04/docile/project_results/$PROJECT
BATCH_DATA_DIR=$DATA_DIR/batch_${BATCH}/successful/
# Specify a certain year to extract, if extract all years, set to 0
YEAR=2011


# Start and end zip to extract data from:
START_ZIP=3
END_ZIP=5

# Extract data from the batch directory ['ga.pd',5216,[],'all',-0.0001,1,24,'mean','z0'],\
/home/users/ssparrow01/miniconda2/envs/pyenv/bin/python $EXTRACT_SCRIPTS_DIR/wah_extract_local_hadam4.py -i $BATCH_DATA_DIR \
-f "\
['ga.pc',15201,[],'all',-200,200,6,'mean','pressure_0'],\
"  -o $EXTRACT_DATA_DIR/batch_${BATCH} -y $YEAR -s $START_ZIP -e $END_ZIP
