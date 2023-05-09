#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \test_read_01.py
# Created Date: Monday, March 15th 2021, 12:34:28 pm
# Author: Christian Perwass (CR/AEC5)
# <LICENSE id="GPL-3.0">
#
#   Image-Render Blender Point-Cloud importer add-on module
#   Copyright (C) 2022 Robert Bosch GmbH and its subsidiaries
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# </LICENSE>
###

# Test reading with numpy memmap

import os
from pathlib import Path
import numpy as np

from ..PlyReader import CPlyReader
from ..PlyException import CPlyException

# sPlyFile = "test_01.ply"
# sPlyFile = "points_free1.ply"
sPlyFile = "Bearded guy.ply"

sRootPath = Path(os.path.abspath(__file__)).parent.as_posix()
sDataFolder = "_data"

sDataPath = os.path.join(sRootPath, sDataFolder)
sFpData = os.path.normpath(os.path.join(sDataPath, sPlyFile))

# class PlyElement:

# 	def __init__(self, _sType, _iPropCnt):
# 		self.sType = _sType
# 		self.iPropCnt = _iPropCnt
# 		self.xType =

try:
    # open file
    xPly = CPlyReader()
    xPly.Read(sFpData, bHeaderOnly=True)
    xPly.PrintHeaderInfo()

    # xVex = xPly.GetElement(0)
    # lF = xVex.GetPropertyValues("x")
    # xA = lF[0]

    pass

except Exception as xEx:
    CPlyException.Print(xEx, bTraceback=True)
# endtry
