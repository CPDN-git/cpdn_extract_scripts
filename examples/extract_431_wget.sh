# global model
/home/cenv0437/cpdn_analysis/extract_scripts/wah_extract_wget.py -u /gpfs/projects/cpdn/storage/boinc/upload/batch_431/batch_431.txt.gz \
-f "\
['ma.pc',3236,[],'all',200,400,720,'maximum',''],\
['ma.pc',3236,[],'all',200,400,720,'minimum',''],\
['ma.pc',3236,[],'all',200,400,720,'mean',''],\
['ga.pe',5216,[],'all',-0.01,10,720,'mean',''],\
['ga.pd',5216,[],'all',-0.01,10,24,'mean','z0'],\
"  -o /gpfs/projects/cpdn/scratch/cenv0437/extracted/batch_431 -s 1 -e 4

