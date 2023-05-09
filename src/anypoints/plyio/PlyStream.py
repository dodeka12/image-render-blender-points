#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \plystream.py
# Created Date: Tuesday, March 16th 2021, 8:55:11 am
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


class CPlyStream:

    #####################################################################
    def __init__(self, _xStream, bRead=True, bRewind=True):

        self.xStream = None

        if isinstance(_xStream, str):
            try:
                self.xStream = open(_xStream, "rb" if bRead else "wb")
            except Exception:
                raise CPlyException(
                    "Error opening file '{0}' for {1}".format(
                        _xStream, "reading" if bRead else "writing"
                    )
                )
            # endtry
        elif isinstance(_xStream, CPlyStream):
            raise CPlyException(
                "Cannot construct PlyStream object from another PlyStream instance."
            )
        elif (hasattr(_xStream, "read") and bRead) or (
            hasattr(_xStream, "write") and not bRead
        ):
            self.xStream = _xStream
            if bRead and bRewind:
                self.xStream.seek(0)
            # endif
        else:
            raise CPlyException(
                "Given object is not a {0} stream.".format(
                    "readable" if bRead else "writable"
                )
            )
        # endif

        self.iNextReadLine = 0

    # enddef

    #####################################################################
    def __del__(self):

        if self.xStream is not None:
            self.xStream.close()
        # endif
        self.xStream = None

    # enddef

    #####################################################################
    def ReadBinaryArray(self, *, xDType, iCount):
        return np.fromfile(self.xStream, dtype=xDType, count=iCount)

    # enddef

    #####################################################################
    def ReadAsciiLine(self):
        xL = self.xStream.readline()
        self.iNextReadLine += 1
        if xL is None:
            return None
        # endif
        sL = xL.decode("ascii").strip()
        return sL

    # enddef

    #####################################################################
    def ReadKeywordLine(self):
        while True:
            sL = self.ReadAsciiLine()
            if sL is None:
                return None
            # endif
            lW = sL.split(None, 1)
            if len(lW) > 0:
                break
            # endif
        # endwhile
        return lW

    # enddef

    #####################################################################
    def ReadLineAsList(self):
        sL = self.ReadAsciiLine()
        if sL is None:
            return None
        # endif
        lW = sL.split()
        return lW

    # enddef

    #####################################################################
    def ReadNextKeywordLineOf(
        self, _lTargetKeywords, _lIgnoreKeywords, bIgnoreAllNonTarget=False
    ):

        while True:
            lKey = self.ReadKeywordLine()
            if lKey is None:
                return None
            # endif

            sKey = lKey[0]
            if sKey in _lTargetKeywords:
                break
            elif bIgnoreAllNonTarget or (sKey in _lIgnoreKeywords):
                continue
            else:
                raise CPlyException(
                    "Unexpected keyword '{0}' at line {1}.".format(
                        sKey, self.CurrentLine()
                    )
                )
            # endif
        # endwhile

        return lKey

    # enddef

    #####################################################################
    def CurrentLine(self):
        return self.iNextReadLine - 1

    # enddef

    #####################################################################
    def GetKeyPars(self, _lKey, _lCnt):

        sCnt = " or ".join([str(i) for i in _lCnt])

        if len(_lKey) == 1:
            raise CPlyException(
                "Expected {0} parameters for keyword '{1}' in line {2}, but found none.".format(
                    sCnt, _lKey[0], self._CurrentLine()
                )
            )
        # endif

        lPars = _lKey[1].split()
        if len(lPars) not in _lCnt:
            raise CPlyException(
                "Expected {0} parameters for keyword '{1}' in line {2}, but found {3}.".format(
                    sCnt, _lKey[0], self._CurrentLine(), len(lPars)
                )
            )
        # endif

        return lPars

    # enddef


# endclass PlyStream
