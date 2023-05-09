#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \PlyProperty.py
# Created Date: Tuesday, March 16th 2021, 10:23:34 am
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
from . import PlyType


class CPlyProperty:
    def __init__(self, *, sFormat, lParseParameters=None):

        self.sFormat = sFormat
        self.sType = None
        self.sName = None
        self.xCntType = None
        self.xElType = None

        if lParseParameters is not None and sFormat is not None:
            self.ParseHeader(lPars=lParseParameters)
        # endif

    # enddef

    def IsList(self):
        return self.sType == "list"

    # enddef

    def IsScalar(self):
        return self.sType == "scalar"

    # enddef

    def GetElType(self):
        return self.xElType

    # enddef

    def GetCntType(self):
        return self.xCntType

    # enddef

    def GetNamedElType(self):
        return np.dtype([(self.sName, self.xElType)])

    # enddef

    def ParseHeader(self, *, lPars):
        self.sType = None

        iParCnt = len(lPars)
        if iParCnt != 2 and iParCnt != 4:
            raise CPlyException(
                "Expected 2 or 4 parameters for property definition, but {0} were given".format(
                    iParCnt
                )
            )
        # endif

        if lPars[0] == "list":
            if iParCnt != 4:
                raise CPlyException(
                    "Property of type 'list' requires 4 parameters, but {0} were given".format(
                        iParCnt
                    )
                )
            # endif

            self.sType = "list"
            self.xCntType = PlyType.GetNumpyType(
                sPlyType=lPars[1], sFormat=self.sFormat
            )
            self.xElType = PlyType.GetNumpyType(sPlyType=lPars[2], sFormat=self.sFormat)
            self.sName = lPars[3]

        else:
            if iParCnt != 2:
                raise CPlyException(
                    "Property of type 'scalar' requires 2 parameters, but {0} were given".format(
                        iParCnt
                    )
                )
            # endif

            self.sType = "scalar"
            self.xCntType = None
            self.xElType = PlyType.GetNumpyType(sPlyType=lPars[0], sFormat=self.sFormat)
            self.sName = lPars[1]
        # endif

    # enddef


# endclass
