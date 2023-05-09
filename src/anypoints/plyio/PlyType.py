#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \PlyType.py
# Created Date: Tuesday, March 16th 2021, 10:57:39 am
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

import numpy as np
from .PlyException import CPlyException

dicPlyToNp = {
    "char": "i1",
    "short": "i2",
    "int": "i4",
    "uchar": "u1",
    "ushort": "u2",
    "uint": "u4",
    "int8": "i1",
    "int16": "i2",
    "int32": "i4",
    "uint8": "u1",
    "uint16": "u2",
    "uint32": "u4",
    "float": "f4",
    "double": "f8",
    "float16": "f2",
    "float32": "f4",
    "float64": "f8",
}

dicNpToPly = {
    "i1": "char",
    "i2": "short",
    "i4": "int",
    "u1": "uchar",
    "u2": "ushort",
    "u4": "uint",
    "f2": "float16",
    "f4": "float",
    "f8": "double",
}


def _ApplyFormatToType(_sType, _sFormat):

    if _sFormat == "binary_little_endian":
        sType = "<" + _sType
    elif _sFormat == "binary_big_endian":
        sType = ">" + _sType
    elif _sFormat == "ascii":
        sType = _sType
    else:
        raise CPlyException("Unknown PLY format identifier '{0}'".format(sFormat))
    # endif

    return sType


# enddef


def GetNamedNumpyType(*, sName, sPlyType, sFormat):
    sNpType = dicPlyToNp.get(sPlyType)
    if sNpType is None:
        raise CPlyException("Unknown PLY type identifier '{0}'".format(sPlyType))
    # endif

    sNpType = _ApplyFormatToType(sNpType, sFormat)
    return np.dtype([(sName, sNpType)])


# enddef


def GetNumpyType(*, sPlyType, sFormat):
    sNpType = dicPlyToNp.get(sPlyType)
    if sNpType is None:
        raise CPlyException("Unknown PLY type identifier '{0}'".format(sPlyType))
    # endif

    sNpType = _ApplyFormatToType(sNpType, sFormat)
    return np.dtype(sNpType)


# enddef
