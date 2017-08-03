#!/usr/bin/env python2.7

###############################################################################
# Program : wah_extract_local.py
# Author  : Peter Uhe, based on original scripts by Neil Massey
# Date	  : 09/09/16
# Purpose : Script to specify the urls of w@h zip files, then download and extract 
#           the data of requested fields into separate netCDF files
###############################################################################

import sys, os
import ast
import tempfile, shutil
import glob
import argparse
import traceback

from wah_extract_functions import extract_url,process_netcdf,read_urls,check_files_exist,get_filename

###############################################################################

if __name__ == "__main__":
	urls_file = ""
	fields = ""
	output_dir = ""
	
	parser=argparse.ArgumentParser('Batch Extract Script:')
	urls_help='File containing list of urls of zip files (in gzipped format)'
	parser.add_argument('-u','--urls_file',required=True,help=urls_help)
	out_dir_help='Base of output directory for extracted files'
	parser.add_argument('-o','--out_dir',default='extract',help=out_dir_help)
	
	fields_help='List of fields to extract: fields has the format:'
	fields_help+='\n      : [file_stream,stash_code,[region],process,valid_min,valid_max,time_freq,cell_method,vert_lev]'
	fields_help+='\n      : where file_stream = ga.pd|ga.pe|ma.pc'
	fields_help+='\n      :       stash_code = stash_section*1000 + stash_item'
	fields_help+='\n      :       [region] = [lon_NW,lat_NW,lon_SW,lat_SW]'
	fields_help+='\n      :        process = time post_processing: min|max|mean|sum|all'
	fields_help+='\n      :        time_freq = input variable data frequency in hours (e.g. 24=daily, 720=monthly)'
	fields_help+='\n      :        cell_method = input variable time cell method: minimum,maximum,mean'
	fields_help+='\n      :        vert_lev = (optional) input variable name of vertical level in netcdf file'
	parser.add_argument('-f','--fields',required=True,help=fields_help)

	parser.add_argument('-s','--start_zip',type=int,default=1,help='First zip to extract')
	parser.add_argument('-e','--end_zip',type=int,default=12,help='Last zip to extract')
	
	parser.add_argument('--structure',default='std',help='Directory structure (after field) [std|startdate-dir]')
	parser.add_argument('--output-freq',default='month',help='Output frequency of model zip/data files [monthly|yearly]')

	# Get arguments
	args = parser.parse_args()
	fields=args.fields
	output_dir=args.out_dir
	urls_file=args.urls_file
	start_zip=args.start_zip
	end_zip=args.end_zip
		
	# split the field list up
	field_list = ast.literal_eval(fields)
	for field in field_list:
		if len(field) != 9:
			print "Error! Fields argument not formatted correctly"
			print field
			print fields_help
			exit()
			
	if args.structure!='std' and args.structure!='startdate-dir':
		raise Exception('Error, --structure argument must be either std or startdate-dir')
	
	# Get list of urls of zips to extract
	urls = read_urls(urls_file)
	# Strip away the zip name, leaving the path of the task
	taskurls= set(map(os.path.dirname,urls))

	print 'fields',field_list
	print 'Number of tasks:',len(taskurls)
	
	# create a temporary directory - do we have permission?
        #temp_dir = tempfile.mkdtemp(dir=os.environ['HOME'])
<<<<<<< HEAD
    tmp_dir = os.path.join(output_dir+'/tmp')
	if not os.path.exists(output_dir): 
		os.makedirs(output_dir) 
    	if not os.path.exists(tmp_dir):
    		os.makedirs(tmp_dir)
    	print 'created temporary dir: ',os.path.basename(tmp_dir)
    	temp_dir = tempfile.mkdtemp(dir=tmp_dir)
    	temp_nc = os.path.join(temp_dir,'tmp.nc')
=======
        tmp_dir = os.path.join(output_dir+'/tmp')
	if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                os.makedirs(tmp_dir)
	temp_dir = tempfile.mkdtemp(dir=tmp_dir)
	temp_nc = os.path.join(temp_dir,'tmp.nc')
>>>>>>> 6b95dc104c611e6747c806691f0f13845c63b238
	try:
		# Loop over tasks
		for u in list(taskurls):
			if u.strip()=='':
				# blank line, skip
				continue
			print u
			
			# Check if files already exist and skip if the are
			if check_files_exist(u, field_list,output_dir,start_zip,end_zip,args.structure,args.output_freq):
				print 'Files exist, skipping'
				continue
			
			# Extract zip files into temporary directory
			all_netcdfs=extract_url(u, field_list, output_dir, temp_dir,start_zip,end_zip)
			if not all_netcdfs:
				print 'Extract failed for task: ',os.path.basename(u)
				continue
		
			# Process fields into single netcdf files
			for field in field_list:
				out_file=get_filename(u, field,output_dir,start_zip,end_zip,structure=args.structure,zip_freq=args.output_freq)
				print out_file
				netcdfs=all_netcdfs[field[0]] # List of netcdf files for stream in field (e.g. 'ga.pe')
				if not netcdfs:
						print 'Error, no files for requested file stream:',field[0]
						continue
				for i,nc_in_file in enumerate(netcdfs):
					if i==0:	append=False
					else: 		append=True
					out_netcdf=process_netcdf(nc_in_file,temp_nc,field,append,zip_freq=args.output_freq)
					if not out_netcdf:
						break
				# Successfully created file:
				if out_netcdf:
					# First make the directory 
					out_dir=os.path.dirname(out_file)
					if not os.path.exists(out_dir):
						os.makedirs(out_dir)
					# Rename temp file to out_netcdf
					shutil.move(temp_nc,out_file)
					print os.path.basename(out_file)
				
			# Remove netcdf files to stop temp directory getting too big
			for nc_list in all_netcdfs.itervalues():
				for fname in nc_list:
					os.remove(fname)
	except Exception,e:
		print 'Error extracting netcdf files',e
		traceback.print_exc()
	finally:
		# remove the temporary directory
		shutil.rmtree(temp_dir,ignore_errors=True)
		shutil.rmtree(tmp_dir,ignore_errors=True)
