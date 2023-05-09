#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \unit_test\test_pcimport_01.py
# Created Date: Tuesday, April 20th 2021, 11:54:33 am
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

from numpy.lib.financial import fv
import bpy
from anypoints import pcimport
from anypoints import util

sFpPoints = r"[path]"

# xColl = pcimport.ImportPointCloud(bpy.context, sFpPoints,
# 					sName = "Hello",
# 					fImportPercent=100,
# 					bUseVoxel=True,
# 					fVoxelSize=0.02)

# print(xColl.name)

util.RemoveCollection("Hello")
# util.RemoveOrphaned()
