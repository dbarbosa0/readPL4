#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lib_writePL4.py
#  
#  Copyright 2024 Daniel Barbosa <dbarbosa@ufba.br>
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

# Write PISA's binary PL4
# Based on PlotXY Open Source code and lib_readPL4_py3.py
# https://github.com/max-privato/PlotXY_OpenSource
# https://github.com/ldemattos/readPL4
# 	Pl4Type = 132
# 	PL4HeadComment = "11-Nov-18  11.00.00"
# 	numInt = 15
# 	precision = 0
# 	KNT = 1
# 	nEnerg = 0
# 	tMax = miscData['tmax']
# 	deltaT = miscData['deltat']
# 	NV = 0
# 	NC = miscData['nvar']*2
# 	IHSPl4 = 0
# 	modHFS = 0
# 	numHFS = 0
# 	#lFirst = int(76 + 16 * (miscData['nvar'] / (numHFS + 1) - 1) + 1)
# 	lFirst = int(80 + 16 * (miscData['nvar'] / (numHFS + 1)) + 1)
# 	lLast = int((5 + miscData['nvar'])*16 + miscData['steps']*(miscData['nvar']+1)*4 +1)
# 	commBytes = 0


def writePL4(pl4file, dfHEAD, data, miscData):

	import struct

	# open binary file for writing
	with open(pl4file, 'wb') as of:
		if of.writable():
			of.write(miscData['pl4type'].to_bytes(1))
			of.write(miscData['pL4headcomment'].encode())
			of.write(struct.pack('i', miscData['numint']))
			of.write(struct.pack('i', miscData['precision']))
			of.write(struct.pack('i', miscData['knt']))
			of.write(struct.pack('i', miscData['nenerg']))
			of.write(struct.pack('<f', miscData['tmax']))
			of.write(struct.pack('<f', miscData['deltat']))
			of.write(struct.pack('i', miscData['nv']))
			of.write(struct.pack('i', miscData['nc']))
			of.write(struct.pack('i', miscData['lfirst']))
			of.write(struct.pack('i', miscData['pl4size'] + 1))
			of.write(struct.pack('i', miscData['ihspl4']))
			of.write(struct.pack('i', miscData['modhfs']))
			of.write(struct.pack('i', miscData['numhfs']))
			of.write(struct.pack('i', miscData['commbytes']))
			of.write(struct.pack('i', miscData['commbytes']))

			for i in range(0,miscData['nvar']):
				of.write(b'\x20\x20\x20')
				of.write(str(dfHEAD['TYPE'][i]).encode())
				varName = dfHEAD['FROM'][i] + dfHEAD['TO'][i]
				of.write(varName.encode())

			for ctP in range(0,len(data)):
				for ctVar in range(0,miscData['nvar'] + 1):
					of.write(struct.pack('<f', data[ctP][ctVar]))

		else:
			print('Não é possível escrever no arquivo: ' + pl4file)
