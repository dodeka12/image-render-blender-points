#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \Tetraeder.py
# Created Date: Sunday, March 14th 2021, 9:20:36 am
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

import bpy
import bmesh
import math

import anyblend

################################################################################
def CreateTetraeder(_xContext, _sName, _fSize):

    objA = anyblend.object.CreateObject(_xContext, _sName)

    # Edge length
    fA = _fSize
    # Inner sphere radius
    fRi = fA / 12.0 * math.sqrt(6)
    # Outer sphere radius
    fRu = 3.0 * fRi
    # Edge sphere radius
    fRk = fA / 4.0 * math.sqrt(2)
    # Pyramid height
    fHp = fRi + fRu
    # Face height
    fHf = fA * math.sqrt(3.0 / 4.0)

    lP = []

    fX = math.sqrt(fRu * fRu - fRi * fRi)
    fY = 0.0
    fZ = -fRi
    lP.append([fX, fY, fZ])

    fX = -(fHf - fX)
    fY = -0.5 * fA
    lP.append([fX, fY, fZ])

    fY = -fY
    lP.append([fX, fY, fZ])

    fX = 0.0
    fY = 0.0
    fZ = fHp - fRi
    lP.append([fX, fY, fZ])

    lF = [[0, 1, 2], [0, 3, 1], [1, 3, 2], [0, 2, 3]]

    # Set object mesh
    objA.data.from_pydata(lP, [], lF)
    return objA


# enddef

################################################################################
# Create Cube


def CreateCube(_xContext, _sName, _fSize):

    objA = anyblend.object.CreateObject(_xContext, _sName)

    bm = bmesh.new()
    bm.from_mesh(objA.data)
    bmesh.ops.create_cube(bm, size=_fSize)
    bm.to_mesh(objA.data)
    bm.free()

    return objA


# enddef
