###############################################################################
# Program : wah_extract_functions.py
# Sihan Li: Modified to include vertical integrated variables & snapshots
# Author  : Peter Uhe, based on original scripts by Neil Massey
# Date	  : 09/09/16
# Purpose : Functions to extract w@h zip files and extract the 
#           requested fields into separate netCDF files

###############################################################################

import sys, os, ast
import urllib, tempfile, zipfile, shutil
import numpy, numpy.ma
import math
import gzip
import glob
#from netcdf_file import netcdf_file # Note netcdf_file.py doesn't allow appending
#from scipy.io.netcdf import netcdf_file # Note Append option requires at least scipy-0.15.0
from netCDF4 import Dataset as netcdf_file  # Note Can use netCDF4 for append option instead 

from conv_rot_grid import rot2glob, glob2rot
import string
from datetime import datetime,timedelta
import numpy as np


#############################################################################
	
def um_datecode(syear,smon,zip_num):
	months=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
	month_str=months[(smon+zip_num-1)%12]
	year=syear+(smon+zip_num-1)/12
	decade=(year-1800)/10
	year_code=str(year%10)
	if decade<10:   dec_code=str(decade) #decade is 0 to 9
	else:           dec_code=chr(decade-10+ord('a')) #decade needs to be converted to char
	return dec_code+year_code+month_str
	
##############################################################################

#function to timesamp given um timestamp
# assumes code e.g. l5apr -> 2015-04
def um_to_timestamp(um_datecode):
	mon_map={'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
	dec_code=um_datecode[0]
	try:dec=int(dec_code) #decade is 0 to 9
	except: dec=ord(dec_code)-ord('a')+10 #decade is a-z
	year=int(um_datecode[1])
	try:
		mon=mon_map[um_datecode[2:]]
	except:
		# Assume a datecode ending in '10' is a yearly file
		if um_datecode[3:]=='10':
			mon='yr'
	return str(1800+dec*10+year)+'-'+str(mon).zfill(2)


###############################################################################

def get_coord_string(coord_list):
	coord_string = ""
	for p in range(0,4):
		V = str(coord_list[p])
		if (p == 1 or p == 3):
			if V[0] == "-":
				coord_string += "S" + V[1:] + "_"
			else:
				coord_string += "N" + V[0:] + "_"
		else:
			if V[0] == "-":
				coord_string += "W" + V[1:] + "_"
			else:
				coord_string += "E" + V[0:] + "_"
	return coord_string[:-1]

# Take time freq of data in hrs and output human readable
def time_freq_friendly(time_freq):
	if int(time_freq)==24:
		return 'daily'
	elif int(time_freq) == 720:
		return 'monthly'
	else:
		return str(time_freq)+'hrly'

###############################################################################

def get_output_field_name(field):
	fname = field[1]
	if field[2] != []:
		coord_string = get_coord_string(field[2])
		fname += "_" + coord_string
	if field[3] != 'all':
		fname += "_" + field[3]
	return fname
	
def get_output_field_name2(field):
	time_freq=time_freq_friendly(field[6])
	cell_method=field[7]
	fname = 'item'+str(field[1])
	fname += '_'+time_freq
#	if cell_method !='mean':
	fname += '_' + cell_method
	if field[2] != []:
		coord_string = get_coord_string(field[2])
		fname += "_" + coord_string
	if field[3] != 'all':
		fname += "_" + field[3]
	return fname
	
# Just have item number time freq and meaning (and any spatial meaning if necessary)
def get_output_field_name3(field):
	time_freq=time_freq_friendly(field[6])
	cell_method=field[7]
	fname = 'item'+str(field[1])
	fname += '_'+time_freq
	fname += '_' + cell_method
	if field[3] != 'all':
		fname += "_" + field[3]
	return fname

###############################################################################

def get_filename(taskpath, field,output_dir,zipstart,zipend,structure='std',zip_freq='month'):
	stream_map={'ma':'atmos','ga':'region','ka':'atmos','ko':'ocean'}
	# Different components used in file name and path
	boinc=taskpath.split('/')[-1]
	
	# When splitting up the file name by underscore
	# hadcm3 apps have one less component (e.g. compared to wah2_eu50)
	if boinc[:6]=='hadcm3':
		umid=boinc.split('_')[1]
		datecode=boinc.split('_')[2]
	else:
		umid=boinc.split('_')[2]
		datecode=boinc.split('_')[3]
	# Get start year and month (old filenames don't contain start month so assume 12)
	syear=int(datecode[:4])
	try:
		smon=int(datecode[4:6])
	except: 
		smon = 12
	# Work out start and end date of output file
	datestart=datetime(int(syear),int(smon),1)
	if zip_freq=='month':
		date1 = add_months(datestart,zipstart-1)
		date2 = add_months(datestart,zipend-1)
	elif zip_freq=='year':
		date1=datestart.replace(year=int(syear)+zipstart-1)
		datetmp=add_months(date1,11) # First add 11 months for yearly output
		date2=datetmp.replace(year=datetmp.year+zipend-zipstart) #Add number of years
	else:
		raise Exception('Error, zip freq must be month or year')
	date_range = str(date1.year)+'-'+str(date1.month).zfill(2)+'_'+str(date2.year)+'-'+str(date2.month).zfill(2)
	# Other components
	time_freq=time_freq_friendly(field[6])
	cell_method=field[7]
	varname = get_output_field_name3(field)
	model = stream_map[field[0][:2]]
	if field[2]!=[]:
		coord_string = '_'+ get_coord_string(field[2])
	else:
		coord_string = ''

	# construct file name
	if structure=='std':
		fname = os.path.join(output_dir,model+coord_string,varname,varname+'_'+umid+'_'+date_range+'.nc')
	elif structure=='startdate-dir':
		fname = os.path.join(output_dir,model+coord_string,varname,datecode,varname+'_'+umid+'_'+date_range+'.nc')
		
	return fname

###############################################################################

def check_files_exist(taskpath, field_list,output_dir,zipstart,zipend,structure,zip_freq):

	# Loop over fields/ variables
	for field in field_list:
		# If the file doesn't exist return false
		fname=get_filename(taskpath,field,output_dir,zipstart,zipend,structure=structure,zip_freq=zip_freq)
		if not os.path.exists(fname):
			return False
	# We got to the end, all files must exist
	return True

###############################################################################

def get_idx(point, array):
	D = array[1] - array[0]
	S = array[0]
	I = int(0.5+(point - S) / D)
	return I

###############################################################################

def subset_dimensions(in_dimensions, field, plon, plat):
	fs = field[2]
	# fs has elements [lon_l, lat_l, lon_r, lat_r]
	out_dims = []
	subset_dims = []
	# check whether we need to translate from global to rotated grid
	if plon == 0.0 and plat == 90.0:
		if fs != []:
			rlon_s = fs[0]
			rlon_e = fs[2]
			rlat_s = fs[1]
			rlat_e = fs[3]
	else:
		if fs != []:
			rlon_s, rlat_s = glob2rot(fs[0], fs[1], plon, plat)
			rlon_e, rlat_e = glob2rot(fs[2], fs[3], plon, plat)
	# get the lon / lat indices
	remap_data = False
	for d in in_dimensions:
		if "longitude" in d[0]:
			if fs == []:
				lon_idx_s = 0
				lon_idx_e = d[1].shape[0]
			else:
				lon_idx_s = get_idx(rlon_s, d[1])
				lon_idx_e = get_idx(rlon_e, d[1]) + 1
				print 'lon i',lon_idx_s,lon_idx_e
			if lon_idx_s < 0:
				remap_data = True
			if lon_idx_e > d[1].shape[0]:
				remap_data = True
			# if the data needs remapping
			if remap_data:
				d_len = d[1].shape[0]				# get the length
				d_len_d2 = d_len / 2				# get the length div 2
				lon_idx_s += d_len_d2				# remap the start index
				lon_idx_e += d_len_d2				# remap the end index
				d_new = numpy.zeros([d_len], 'f')	# create a new dimension variable
				d_new[0:d_len_d2] = d[1][d_len_d2:d_len]	# copy the right hand half to the left hand
				d_new[d_len_d2:d_len] = d[1][0:d_len_d2]	# copy the left hand half to the right hand
				d[1] = d_new						# reassign
			# if processing data then do not append dimension to output dimensions
			if field[3] == "all":
				out_dims.append([d[0], d[1][lon_idx_s:lon_idx_e]])
			subset_dims.append([d[0], d[1][lon_idx_s:lon_idx_e]])

		elif "latitude" in d[0]:
			if fs == []:
				lat_idx_s = 0
				lat_idx_e = d[1].shape[0]
			else:
				lat_idx_s = get_idx(rlat_s, d[1])
				lat_idx_e = get_idx(rlat_e, d[1]) +1
			if lat_idx_e < lat_idx_s:
				temp = lat_idx_e
				lat_idx_e = lat_idx_s
				lat_idx_s = temp
			if lat_idx_s < 0:
				lat_idx_s = 0
			if lat_idx_e > d[1].shape[0]:
				lat_idx_e = d[1].shape[0]
			# if processing data then do not append dimension
			if field[3] == "all":
				out_dims.append([d[0], d[1][lat_idx_s:lat_idx_e]])
			subset_dims.append([d[0], d[1][lat_idx_s:lat_idx_e]])
		else:
			out_dims.append([d[0], d[1]])
			subset_dims.append([d[0], d[1]])
	# if processing data then need a "pt" dimension
	if field[3] != "all":
		out_dims.append(["pt", numpy.array([1.0],dtype=numpy.float32)])
	return out_dims, subset_dims, [lon_idx_s, lat_idx_s, lon_idx_e, lat_idx_e], remap_data

###############################################################################

def calc_grid_box_area(lon, lat, lon_d, lat_d, plon, plat):
	# calculate the area of a grid box.  This is only an approximation as it
	# assumes the grid box is square, rather than the polygonal shape the
	# rotated boxes actually are.
	lon1_rad, lat1_rad = rot2glob(lon-lon_d,lat+lat_d, plon, plat)
	lon2_rad, lat2_rad = rot2glob(lon+lon_d,lat-lat_d, plon, plat)
		
	area = math.fabs(lon2_rad-lon1_rad) *\
		   math.fabs(math.sin(lat2_rad) - math.sin(lat1_rad))
	return area

###############################################################################

def aamean(var_ma_data, plon, plat, subset_dims):
	# calculate the weights
	if plon == 0.0 and plat == 90.0:
		# just a regular grid so the weights are simply the cosine of the latitude
		for dim in subset_dims:
			if "latitude" in dim[0]:
				weights = numpy.cos(numpy.radians(dim[1]))
		lon_means = numpy.ma.mean(var_ma_data, axis=3)
		means = numpy.ma.average(lon_means, weights=weights, axis=2)
	else:
		# identify the latitude and longitude dimensions and get the coordinates
		for dim in subset_dims:
			if "latitude" in dim[0]:
				lats = dim[1]
			if "longitude" in dim[0]:
				lons = dim[1]
		# calculate the weights
		weights = numpy.zeros([lats.shape[0], lons.shape[0]], 'f')
		lon_d = 0.5 * (lons[1] - lons[0])
		lat_d = 0.5 * (lats[1] - lats[0])
		for j in range(0, lats.shape[0]):
			for i in range(0, lons.shape[0]):
				# weights are area grid box
				weights[j,i] = calc_grid_box_area(lons[i], lats[j], lon_d, lat_d, plon, plat)
		# multiply through each timestep / level by the weights
		weighted_data = var_ma_data[:,:] * weights
		# calculate the means - sums first
		means = numpy.ma.sum(numpy.ma.sum(weighted_data, axis=3), axis=2)
		# calculate the means
		for t in range(0, var_ma_data.shape[0]):
			for z in range(0, var_ma_data.shape[1]):
				# only want to use the sum of the weights of the non missing values
				weights_masked = numpy.ma.masked_where(var_ma_data[t,z].mask,weights)
				# now calculate the sum of the weights
				sum_weights = weights_masked.sum()
				# Normalise the means by the sum of weights
				means[t,z] =  means[t,z] / sum_weights
	return means

###############################################################################

def process_data(var_in_data, process, mv, plon, plat, subset_dims, valid_min, valid_max):
	# mask array before processing
	# mask is either the missing value or where the data is outside the
	# valid range
	var_ma_data = numpy.ma.masked_where((var_in_data == mv) | \
										(var_in_data < valid_min) | \
										(var_in_data > valid_max), var_in_data)
	# do the various processes based on what has been requested
	if process == "min":
		out_data = numpy.ma.min(numpy.ma.min(var_ma_data, axis=2), axis=2)
	elif process == "max":
		out_data = numpy.ma.max(numpy.ma.max(var_ma_data, axis=2), axis=2)
	elif process == "mean":
		out_data = aamean(var_ma_data, plon, plat, subset_dims)
	elif process == "sum":
		out_data = numpy.ma.sum(numpy.ma.sum(var_ma_data, axis=2), axis=2)
	if len(out_data.shape) != len(var_in_data.shape)-1:
		out_data = out_data.reshape(out_data.shape[0], out_data.shape[1], 1)
	return out_data

###############################################################################
# Process data: Assumes var_in_data is a masked array
def process_data2(var_in_data, process,plon, plat, subset_dims):
	# do the various processes based on what has been requested
	if process == "min":
		out_data = numpy.ma.min(numpy.ma.min(var_ma_data, axis=2), axis=2)
	elif process == "max":
		out_data = numpy.ma.max(numpy.ma.max(var_ma_data, axis=2), axis=2)
	elif process == "mean":
		out_data = aamean(var_ma_data, plon, plat, subset_dims)
	elif process == "sum":
		out_data = numpy.ma.sum(numpy.ma.sum(var_ma_data, axis=2), axis=2)
	if len(out_data.shape) != len(var_in_data.shape)-1:
		out_data = out_data.reshape(out_data.shape[0], out_data.shape[1], 1)
	return out_data

###############################################################################

def get_missing_value(nc_in_file):
	try:
		mv = getattr(nc_in_file,"missing_value")
	except:
		mv = getattr(nc_in_file,"_FillValue")
	return mv

###############################################################################

def get_rotated_pole(nc_in_file,nc_in_var):
	# get the rotated pole longitude / latitude (for calculating weights)
	try:
		grid_map_name = getattr(nc_in_var,"grid_mapping")
		grid_map_var = nc_in_file.variables[grid_map_name]	
		plon = getattr(grid_map_var,"grid_north_pole_longitude")
		plat = getattr(grid_map_var,"grid_north_pole_latitude")
	except:
		plon = 0.0
		plat = 90.0
	return plon, plat


##############################################################################

# Function select_var
# searches for variable name in netcdf file that matches stash code, meaning period and time cell method
# Stash code is stash_section*1000 + stash_item
# meaning period is in units of hours (e.g. 24 is daily data, 720 is monthly data)
# cell method is e.g. 'mean', 'min', 'max'
#
def select_var(nc_file,stash_code,meaning_period,cell_method):
	for varname,var in nc_file.variables.iteritems():
		# look at fields matching field_name e.g. field16, field16_1 etc. 
		try:
			var_stash_code=int(var.stash_section)*1000+int(var.stash_item)
		except:
			# Not a stash item
			continue
#		if varname[:len(field_name)]==field_name:
		if int(stash_code)==var_stash_code:
			# Get cell method
			tmp=var.cell_method
			dim,var_cell_method=tmp.split()
			if not dim=='time:':
				raise Exception('Error, expecting cell method for time, got: '+dim)
			# Get meaning period from time dimension
			time_dim=nc_file.variables[var.dimensions[0]]
			if 'meaning_period' in time_dim.ncattrs():
				var_meaning_period,units=time_dim.meaning_period.split()
				if not units=='hours':
					raise Exception('Error, expecting meaning period in hours, got: '+units)
			else: # If there is no meaning period, just use expected value
				var_meaning_period = meaning_period

			if int(meaning_period)==int(var_meaning_period) and cell_method==var_cell_method:
				return varname
			else:
				continue
	# Haven't found correct variable:
	raise Exception('Error, could not find variable: stash code='+str(stash_code)+' with meaning period '+str(meaning_period)+' and cell_method '+cell_method)

##############################################################################

# Function select_vars_stash
# searches for variable name in netcdf file that matches stash code, meaning period and time cell method
# Stash code is stash_section*1000 + stash_item
# meaning period is in units of hours (e.g. 24 is daily data, 720 is monthly data)
# cell method is e.g. 'mean', 'min', 'max'
#
def select_vars_stash(nc_file,stash_code,meaning_period,cell_method,vert_lev):
	varnames=[]
	if vert_lev=='':
		vert_lev='any'
	for varname,var in nc_file.variables.iteritems():
		# look at fields matching field_name e.g. field16, field16_1 etc. 
		try:
			var_stash_code=int(var.stash_section)*1000+int(var.stash_item)
		except:
			# Not a stash item
			continue

		# Check for matching stash code
		if int(stash_code)==var_stash_code:

			# Get cell method
			if 'cell_method' in var.ncattrs():
				tmp = var.cell_method.split()
				dim = tmp[0]
				var_cell_method=tmp[1]
				# Debug statement
				#print var.cell_method
				if not dim=='time:':
					raise Exception('Error, expecting cell method for time, got: '+dim)
			else: # no cell method
				var_cell_method='inst'

			# Get meaning period from time dimension
			dims=var.dimensions
			time_dim=nc_file.variables[dims[0]]
			if 'meaning_period' in time_dim.ncattrs():
				var_meaning_period,units=time_dim.meaning_period.split()
				if not units=='hours':
					raise Exception('Error, expecting meaning period in hours, got: '+units)
			else: # If there is no meaning period to check, just set expected value
				var_meaning_period = meaning_period

			# Check if this variable matches the required meaning period and cell method
			if int(meaning_period)==int(var_meaning_period) and cell_method==var_cell_method:
				if vert_lev=='any': # Any level
					varnames.append(varname)
				elif vert_lev== dims[1]: #field[8] matches vertical level 
					varnames.append(varname)
			else:
				continue
	# Haven't found correct variable:
	if varnames==[]:
		raise Exception('Error, could not find variable: stash code='+str(stash_code)+' with meaning period '+str(meaning_period)+' and cell_method '+cell_method+' and vert_lev '+vert_lev)
	else:
		return varnames
		
# Function select_vars_field
# searches for variable name in netcdf file that matches field code, meaning period and time cell method
# meaning period is in units of hours (e.g. 24 is daily data, 720 is monthly data)
# cell method is e.g. 'mean', 'min', 'max'
#
def select_vars_field(nc_file,field_name,meaning_period,cell_method,vert_lev):
	varnames=[]
	if vert_lev=='':
		vert_lev='any'
	for varname,var in nc_file.variables.iteritems():
		if varname[:len(field_name)]==field_name:
			# Get cell method
			tmp=var.cell_method
			dim,var_cell_method=tmp.split()
			if not dim=='time:':
				raise Exception('Error, expecting cell method for time, got: '+dim)
			# Get meaning period from time dimension
			time_dim=nc_file.variables[var.dimensions[0]]
			tmp=time_dim.meaning_period
			var_meaning_period,units=tmp.split()
			if not units=='hours':
				raise Exception('Error, expecting meaning period in hours, got: '+units)
			# Check if this variable matches the required meaning period and cell method
			if int(meaning_period)==int(var_meaning_period) and cell_method==var_cell_method:
				if vert_lev=='any': # Any level
					varnames.append(varname)
				elif vert_lev== dims[1]: # check vert_lev matches vertical level in file
					varnames.append(varname)
			else:
				continue
	# Haven't found correct variable:
	if varnames==[]:
		raise Exception('Error, could not find variable: field name='+field_name+' with meaning period '+str(meaning_period)+' and cell_method '+cell_method+' and vert_lev '+vert_lev)
	else:
		return varnames

# main function to read in raw netcdf files and write to single variable files
def process_netcdf(in_ncf,out_name,field,append,zip_freq='month'):

	try:
		item_code = field[1]
		process = field[3]
		v_min = field[4]
		v_max = field[5]
		meaning_period = field[6]
		cell_method = field[7]
		vert_lev = field[8]
		
		in_ncf_end=os.path.basename(in_ncf)
		umid,datestamp=in_ncf_end[:-3].split(field[0])
	
		# open as netCDF to a temporary file
		nc_in_file = netcdf_file(in_ncf,'r')

		# get the variable from the input (choose first variable from possible variables)
		in_vars = select_vars_stash(nc_in_file,item_code,meaning_period,cell_method,vert_lev)
		in_vars.sort()
		print in_vars,
		if len(in_vars)>1:
			print 'Warning, multiple variables found matching request, choosing first variable',in_ncf_end,
		in_var=in_vars[0]
	
		nc_in_var = nc_in_file.variables[in_var]
		in_dimensions = []

		
		# Get the dimensions from input netcdf
		for d in nc_in_var.dimensions:
			# get the input dimension and the data
			dim_in_var = nc_in_file.variables[d]
			dim_in_data = dim_in_var[:]
			in_dimensions.append([d, dim_in_data])
		
		# get the rotated pole definition
		plon, plat = get_rotated_pole(nc_in_file,nc_in_var)
		# subset the dimensions to create the out_dimensions
		out_dims, subset_dims, lon_lat_idxs, remap_data = subset_dimensions(in_dimensions, field, plon, plat)
		# if the longitude and latitude indexes are < 0 then we need to remap the data so that 0deg is
		# in the middle of the field, not at the beginning
		if remap_data:
			in_data = nc_in_var[:,:,lon_lat_idxs[1]:lon_lat_idxs[3],:]	# get the input data - can subset latitude early
			new_data = numpy.ma.zeros(in_data.shape, 'f') # create a new store
			d_len = in_data.shape[3]					# get the longitude length
			d_len_d2 = d_len / 2						# lon length div 2
			new_data[:,:,:,0:d_len_d2] = in_data[:,:,:,d_len_d2:d_len]	# copy right hand half to left hand
			new_data[:,:,:,d_len_d2:d_len] = in_data[:,:,:,0:d_len_d2]  # copy left hand half to right hand
			var_out_data = new_data[:,:,:,lon_lat_idxs[0]:lon_lat_idxs[2]] # get the subset data
		else:		
			var_out_data = nc_in_var[:,:,lon_lat_idxs[1]:lon_lat_idxs[3], lon_lat_idxs[0]:lon_lat_idxs[2]]

		# Check we have the correct number of time values:
		# Note this assumes monthly output data
		ntime=nc_in_var.shape[0]
		if zip_freq=='month':
			factor = 720. # hours in a month
		elif zip_freq=='year':
			factor = 8640. # hours in a year
		if ntime != factor / (meaning_period*1.0):
			raise Exception('Data has wrong number of times ('+str(ntime)+' for meaning period: '+str(meaning_period))
		
		# Check data is within range
		mv = get_missing_value(nc_in_var)
		if not numpy.all(numpy.isfinite(var_out_data)) or var_out_data.min()<v_min or var_out_data.max()>v_max:
			raise Exception('Data outside valid range ('+str(v_min)+' - '+str(v_max)+') in netcdf file: '+str(var_out_data.min())+','+str(var_out_data.max()))

		# if the data is going to be processed then do the processing here
		if process != "all":
			var_out_data = process_data2(var_out_data, process, plon, plat, subset_dims)
			
			
		# Sort out output file:
		#
		out_var = get_output_field_name3(field)
		# create the output netCDF file if not appending
		if append:
			if not os.path.exists(out_name):
				raise Exception('Error, expecting to append to file but no file exists')
			else:
				nc_out_file = netcdf_file(out_name, "a")
		else:
			# check whether it exists
			if os.path.exists(out_name):
				# remove existing file to make sure this is clean
				os.remove(out_name)

			# Set up new file
			nc_out_file = netcdf_file(out_name, "w",format='NETCDF3_CLASSIC')

			nc_out_file.setncatts(nc_in_file.__dict__)
			# create the dimensions
			for d in out_dims:
				# create the output dimension and variable
				if d[0][:4]!='time':
					dlen=d[1].shape[0]
				else:
					dlen=0 # Time has unlimited dimension
				nc_out_file.createDimension(d[0],dlen)
				dim_out_var = nc_out_file.createVariable(d[0], d[1].dtype, (d[0],))
				# assign the output variable data and attributes from the input
				if d[0] in nc_in_file.variables.keys():
					dim_in_var = nc_in_file.variables[d[0]]
					dim_out_var.setncatts(dim_in_var.__dict__)
				elif d[0] == "pt":
					# if it's the "pt" dimension then create an attribute indicating the domain of the
					# mean-ed / max-ed / min-ed variable
					dom_str = ""
					if field[2] == []:
						dom_str = "global  "
					else:
						for i in range(0, 4):
							dom_str += str(field[2][i]) + ", "
					dim_out_var.domain= dom_str[:-2]
				dim_out_var[:] = d[1][:]
	
			# create the variable
			out_dim_names = [d[0] for d in out_dims]
			nc_out_var = nc_out_file.createVariable(out_var, var_out_data.dtype, out_dim_names)
			# assign the attributes
			nc_out_var.setncatts(nc_in_var.__dict__)
			# remove the grid mapping and coordinates from the dictionary if they exist and process is not all
			if process != "all":
				if "grid_mapping" in nc_out_var.ncattrs():
					del nc_out_var.grid_mapping
				if "coordinates" in nc_out_var.ncattrs():
					del nc_out_var.coordinates
				if "cell_method" in nc_out_var.ncattrs():
					nc_out_var.cell_method += ", area: " + process + " "
		

			# check for rotated pole and copy variable if it exists
			if "grid_mapping" in nc_out_var.ncattrs() and len(out_dims) == 4:
				grid_map_name = getattr(nc_out_var,"grid_mapping")
				grid_map_var = nc_in_file.variables[grid_map_name]
				grid_map_out_var = nc_out_file.createVariable(grid_map_name, 'c', ())
				grid_map_out_var.setncatts(grid_map_var.__dict__)
				# get the global longitude / global latitude vars
				coords = getattr(nc_out_var,"coordinates").split(" ")
				global_lon_var = nc_in_file.variables[coords[0]]
				global_lat_var = nc_in_file.variables[coords[1]]
				global_lon_data = global_lon_var[lon_lat_idxs[1]:lon_lat_idxs[3], lon_lat_idxs[0]:lon_lat_idxs[2]]
				global_lat_data = global_lat_var[lon_lat_idxs[1]:lon_lat_idxs[3], lon_lat_idxs[0]:lon_lat_idxs[2]]
				# create the global latitude / global longitude variables
				out_global_lon_var = nc_out_file.createVariable(coords[0], global_lon_data.dtype, (out_dims[2][0], out_dims[3][0]))
				out_global_lon_var[:] = global_lon_data
				out_global_lat_var = nc_out_file.createVariable(coords[1], global_lat_data.dtype, (out_dims[2][0], out_dims[3][0]))
				out_global_lat_var[:] = global_lat_data
				out_global_lon_var.setncatts(global_lon_var.__dict__)
				out_global_lat_var.setncatts(global_lat_var.__dict__)
		
			# assign the data
			nc_out_var[:] = var_out_data

		# Append data
		if append:
			# find time dimension to append to
			for var in nc_out_file.variables.keys():
				if var[:4]=='time':
					out_time=var
			
			for d in out_dims:
				if d[0][:4]=='time':
					dim_out_var = nc_out_file.variables[out_time]
					tlen=len(dim_out_var)
					dim_out_var[tlen:] = d[1][:]

			nc_out_var = nc_out_file.variables[out_var]
			nc_out_var[tlen:,:]=var_out_data[:]
			
		nc_out_file.close()
		nc_in_file.close()
	except Exception,e:
		print 'Failed to create netcdf file'#,os.path.basename(out_name)
		print e
#		raise
		if os.path.exists(out_name):
			os.remove(out_name)
		return False
	return True

# Add months to datetime object
def add_months(date,months):
	yr = date.year
	mon = date.month
	new_month = ((mon-1)+months)%12 +1
	new_year = yr + ((mon-1)+months)/12
	newdate = date.replace(year=new_year,month=new_month)
	return newdate

###############################################################################

def extract_local(taskpath, field_list, output_dir, temp_dir, zipstart, zipend):
	boinc=taskpath.split('/')[-1]

	# Set up dictionary for list of extracted files (by file stream)
	extracted_netcdfs={}
	for field in field_list:
		extracted_netcdfs[field[0]]=[]

	#loop over zipfiles and extract netcdf files
	try:
		for i in range(zipstart,zipend+1):
			path=os.path.join(taskpath,boinc+'_'+str(i)+'.zip')
			# open and extract contents of zip
			zf = zipfile.ZipFile(path,'r')
			zf.extractall(temp_dir)

			# list the zip contents
			zf_list = zf.namelist()
			# Loop over files in zip and check if we are going to use them
			for zf_file in zf_list:
				found=False
				fname=temp_dir + "/" + zf_file
				if not os.path.exists(fname):
					raise Exception("file not extracted successfully")
				for field in field_list:
					file_stream = field[0]
					if file_stream in zf_file and zf_file[-3:]=='.nc':
						if fname not in extracted_netcdfs[file_stream]:
							extracted_netcdfs[file_stream].append(fname)
						found=True
				if not found: # We are not using this file
					os.remove(fname)
			zf.close()
	except Exception,e:
		print "Could not extract file: " + path
		print e
		# Clean up extracted files
		for nc_list in extracted_netcdfs.itervalues():
			for fname in nc_list:
				os.remove(fname)
		return False
	# Success
	return extracted_netcdfs

###############################################################################

def extract_url(taskurl, field_list, output_dir, temp_dir, zipstart, zipend):
	boinc=taskurl.split('/')[-1]
	
	# Set up dictionary for list of extracted files (by file stream)
	extracted_netcdfs={}
	for field in field_list:
		extracted_netcdfs[field[0]]=[]

	#loop over zipfiles and extract netcdf files
	try:
		for i in range(zipstart,zipend+1):
			url=os.path.join(taskurl,boinc+'_'+str(i)+'.zip')
#			print url
			# check whether this has already been processed # TODO, change this to check each zip rather than folder!
		
			# Download zip and extract files
			zf_fh = tempfile.NamedTemporaryFile(mode='w', delete=False,dir=temp_dir)
			urlret = urllib.urlretrieve(url, zf_fh.name)
			if urlret[1].gettype()!='application/zip':
				raise Exception('Error downloading url: '+url)
			zf = zipfile.ZipFile(zf_fh.name,'r')
			zf.extractall(temp_dir)

			# list the zip contents
			zf_list = zf.namelist()
			# Loop over files in zip and check if we are going to use them
			for zf_file in zf_list:
				found=False
				fname=temp_dir + "/" + zf_file
				if not os.path.exists(fname):
					raise Exception("file not extracted successfully")
				for field in field_list:
					file_stream = field[0]
					if file_stream in zf_file and zf_file[-3:]=='.nc':
						if fname not in extracted_netcdfs[file_stream]:
							extracted_netcdfs[file_stream].append(fname)
						found=True
				if not found: # We are not using this file
					os.remove(fname)
			# Remove downloaded zipfile and clean up file handles
			zf.close()
			os.remove(zf_fh.name)
			zf_fh.close()
	except Exception,e:
		print "Could not extract url: "
		print e
		# Clean up extracted files
		for nc_list in extracted_netcdfs.itervalues():
			for fname in nc_list:
				os.remove(fname)
		# Remove downloaded zipfile and clean up file handle
		if os.path.exists(zf_fh.name):
			os.remove(zf_fh.name)
		if not zf_fh.closed:
			zf_fh.close()
#		raise
		return False
	# Success
#	print base_path,extracted_netcdfs
	return extracted_netcdfs

###############################################################################

def read_urls(urls_file):
	fh = gzip.open(urls_file, 'r')
	urls = fh.readlines()
	fh.close()
	urls = map(string.strip, urls)
	return urls
	
