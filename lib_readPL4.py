#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lib_readPL4_py3.py
#  https://github.com/ldemattos/readPL4
#  
#  Copyright 2019 Leonardo M. N. de Mattos <l@mattos.eng.br>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3.0.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
import os


# Read PISA's binary PL4
def readPL4(pl4file):
	
	import mmap
	import struct
	import pandas as pd
	import numpy as np
	
	miscData = {
		'pl4type':0,
		'pL4headcomment':" ",
		'numint':0,
		'precision':0,
		'knt':0,
		'nenerg':0,
		'tmax':0.0,
		'deltat':0.0,
		'nv':0,
		'nc':0,
		'ihspl4':0,
		'modHFS':0,
		'numHFS':0,
		'lfirst':0,
		'nvar':0,
		'pl4size':0,
		'steps':0,
		'commBytes':0
	}

	# open binary file for reading
	with open(pl4file, 'rb') as f:
		pl4 = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

		# read Pl4Type
		miscData['pl4type'] = struct.unpack('B', pl4[0:1])[0]

		# read Pl4 Head Comment
		miscData['pL4headcomment'] = struct.unpack('19s', pl4[1:20])[0].decode()

		# read numint
		miscData['numint'] = struct.unpack('i', pl4[20:24])[0]

		# read precision
		miscData['precision'] = struct.unpack('i', pl4[24:28])[0]

		# read knt
		miscData['knt'] = struct.unpack('i', pl4[28:32])[0]

		# read nEnerg
		miscData['nenerg'] = struct.unpack('i', pl4[32:36])[0]

		# read TMAX
		miscData['tmax'] = struct.unpack('<f', pl4[36:40])[0]

		# read DELTAT
		miscData['deltat'] = struct.unpack('<f', pl4[40:44])[0]

		# read NV
		miscData['nv'] = struct.unpack('i', pl4[44:48])[0]

		# read number of vars
		miscData['nc'] = struct.unpack('<L', pl4[48:52])[0]
		miscData['nvar'] = miscData['nc'] // 2

		# read lFist
		miscData['lfirst'] = struct.unpack('i', pl4[52:56])[0]

		# read PL4 disk size
		miscData['pl4size'] = struct.unpack('<L', pl4[56:60])[0] - 1

		# read IHSPl4
		miscData['ihspl4'] = struct.unpack('i', pl4[60:64])[0]

		# read modhfs
		miscData['modhfs'] = struct.unpack('i', pl4[64:68])[0]

		# read numhfs
		miscData['numhfs'] = struct.unpack('i', pl4[68:72])[0]

		# read commbytes
		miscData['commbytes'] = struct.unpack('i', pl4[72:76])[0]

		# compute the number of simulation miscData['steps'] from the PL4's file size
		miscData['steps'] = (miscData['pl4size'] - 5*16 - miscData['nvar']*16) // \
							((miscData['nvar']+1)*4)
		miscData['tmax'] = (miscData['steps']-1)*miscData['deltat']

		# generate pandas dataframe	to store the PL4's header
		dfHEAD = pd.DataFrame(columns=['TYPE','FROM','TO'])
		
		for i in range(0,miscData['nvar']):
			pos = 5*16 + i*16
			h = struct.unpack('3x1c6s6s',pl4[pos:pos+16])
			if (float(pd.__version__[0:3]) >= 1.4):
				dfHEAD.loc[len(dfHEAD)] = {'TYPE': int(h[0]),'FROM': h[1],'TO': h[2]}
			else:
				dfHEAD = dfHEAD.append({'TYPE': int(h[0]),'FROM': h[1],'TO': h[2]}, ignore_index=True)
		
		# Correct 'TO' and 'FROM' columns types
		dfHEAD['FROM'] = dfHEAD['FROM'].str.decode('utf-8')
		dfHEAD['TO'] = dfHEAD['TO'].str.decode('utf-8')
		
		# Check for unexpected rows of zeroes
		# See https://github.com/ldemattos/readPL4/issues/2
		expsize = (5 + miscData['nvar'])*16 + miscData['steps']*(miscData['nvar']+1)*4
		nullbytes = 0
		if miscData['pl4size'] > expsize: 
			nullbytes = miscData['pl4size']-expsize


		# read and store actual data, map it to a numpy read only array

		data = np.memmap(f,dtype=np.float32,mode='r',shape=(miscData['steps'],miscData['nvar']+1),offset=(5 + miscData['nvar'])*16 + nullbytes)

		return dfHEAD,data,miscData

# Convert types from integers to strings
def convertType(df):
	#df['TYPE'] = df['TYPE'].apply(lambda x: 'TACS  ' if x == 2 else x)
	#df['TYPE'] = df['TYPE'].apply(lambda x: 'MODELS' if x == 3 else x)
	df['TYPE'] = df['TYPE'].apply(lambda x: 'V-node' if x == 4 else x)
	#df['TYPE'] = df['TYPE'].apply(lambda x: 'UM    ' if x == 5 else x)
	df['TYPE'] = df['TYPE'].apply(lambda x: 'E-bran' if x == 7 else x)
	df['TYPE'] = df['TYPE'].apply(lambda x: 'V-bran' if x == 8 else x)
	df['TYPE'] = df['TYPE'].apply(lambda x: 'I-bran' if x == 9 else x)
	
	return 0
	
# Get desired variable data
def getVarData(dfHEAD,data,Type,From,To):
	
	# Search for desired data in header
	df = dfHEAD[(dfHEAD['TYPE'] == Type) & (dfHEAD['FROM'] == From) & (dfHEAD['TO'] == To)]
				
	if not df.empty:
		data_sel = data[:,df.index.values[0]+1] # One column shift given time vector
		
	else:
		print("Variable %s-%s of %s not found!"%(From,To,Type))
		return(None)

	return(data_sel)

# Get desired variable data
def getVarDataIndex(dfHEAD,data,Type,From,To):
	
	# Search for desired data in header
	df = dfHEAD[(dfHEAD['TYPE'] == Type) & (dfHEAD['FROM'] == From) & (dfHEAD['TO'] == To)]
				
	if not df.empty:
		return(df.index.values[0]+1) # One column shift given time vector
		
	else:
		print("Variable %s-%s of %s not found!"%(From,To,Type))
		return(None)

