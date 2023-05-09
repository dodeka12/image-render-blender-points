#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \PlyReader.py
# Created Date: Tuesday, March 16th 2021, 8:56:34 am
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

from .PlyException import CPlyException
from .PlyStream import CPlyStream
from .PlyElement import CPlyElement


class CPlyReader:

    #####################################################################
    def __init__(self):
        self.xStream = None
        self.iNextReadLine = 0
        self.sFormat = None
        self.sFormatVersion = None
        self.lSupportedFormats = ["ascii", "binary_little_endian", "binary_big_endian"]

        self.lElement = []

    # enddef

    #####################################################################
    def GetElement(self, _xId):

        if isinstance(_xId, str):
            return next((x for x in self.lElement if x.sName == _xId), None)
        elif isinstance(_xId, int):
            if _xId < 0 or _xId > len(self.lElement):
                raise CPlyException("Index {0} is out of bounds".format(_xId))
            # endif
            return self.lElement[_xId]
        # endif

        raise CPlyException(
            "Invalid id type '{0}' to access element".format(type(_xId))
        )

    # enddef

    #####################################################################
    def GetElementNames(self):
        return [x.sName for x in self.lElement]

    # enddef

    #####################################################################
    def GetElementCount(self):
        return len(self.lElement)

    # enddef

    #####################################################################
    def _ParseHeader(self):

        try:
            ###############################################################
            # Read magic word
            lKey = self.xStream.ReadKeywordLine()
            if not lKey:
                raise CPlyException("File appears to be empty")
            # endif

            if lKey[0] != "ply":
                raise CPlyException("Given file does not appear to be a 'ply' file")
            # endif

            ###############################################################
            # Read file format
            try:
                lKey = self.xStream.ReadNextKeywordLineOf(["format"], ["comment"])
            except CPlyException as xEx:
                raise CPlyException(
                    "Error parsing header searching for 'format' keyword", xEx
                )
            # endtry

            lPars = self.xStream.GetKeyPars(lKey, [2])
            if lPars[0] not in self.lSupportedFormats:
                raise CPlyException("File format '{0}' not supported".format(lPars[0]))
            # endif

            self.sFormat = lPars[0]
            self.sFormatVersion = lPars[1]

            ###############################################################
            # Read elements
            self._ParseElementList()
        except Exception as xEx:
            raise CPlyException("Error parsing PLY header", xEx)
        # endtry

    # enddef

    #####################################################################
    def _ParseElementList(self):
        try:
            self.lElement = []

            lKey = self.xStream.ReadNextKeywordLineOf(
                ["element", "end_header"], [], bIgnoreAllNonTarget=True
            )
            while True:
                if lKey is not None:
                    sKey = lKey[0]
                    if sKey == "end_header":
                        break
                    elif sKey == "element":
                        xEl = CPlyElement(sFormat=self.sFormat)
                        lKey = xEl.ParseHeader(lKey, self.xStream)
                        self.lElement.append(xEl)
                    else:
                        raise CPlyException("This should never throw")
                    # endif
                else:
                    raise CPlyException("End-of-header keyword not found")
                # endif
            # endwhile
        except CPlyException as xEx:
            raise CPlyException("Error reading element definitions from header", xEx)
        # endtry

    # enddef

    #####################################################################
    def Read(self, _xStream, bHeaderOnly=False):

        try:
            self.xStream = CPlyStream(_xStream, bRead=True, bRewind=True)
            self._ParseHeader()

            if not bHeaderOnly:
                for xEl in self.lElement:
                    xEl.Read(self.xStream)
                # endfor
            # endif
        except Exception as xEx:
            del self.xStream
            if isinstance(_xStream, str):
                raise CPlyException("Error reading file '{0}'".format(_xStream), xEx)
            else:
                raise CPlyException("Error reading from stream", xEx)
            # endif
        # endtry

        del self.xStream

    # enddef

    #####################################################################
    def PrintHeaderInfo(self):

        for xEl in self.lElement:
            print(
                "Element '{0}' with {1} data sets of:".format(
                    xEl.GetName(), xEl.GetValueCount()
                )
            )
            lPropNames = xEl.GetPropNames()
            for sPropName in lPropNames:
                xProp = xEl.GetProperty(sPropName)
                if xProp.IsList():
                    print(
                        "> list ({0}) of type {1}".format(
                            str(xProp.GetCntType()), str(xProp.GetElType())
                        )
                    )
                else:
                    print("> {0} ({1})".format(sPropName, str(xProp.GetElType())))
                # endif
            # endfor
            print("")
        # endfor

    # enddef


# endclass
