#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \PlyElement.py
# Created Date: Tuesday, March 16th 2021, 9:44:57 am
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
from .PlyProperty import CPlyProperty


class CPlyElement:

    ##################################################
    def __init__(self, *, sFormat):
        self.sFormat = sFormat
        self.sName = None
        self.iCount = None
        self.bIsList = False
        self.bCanMemMap = False
        self.lProps = None
        self.dicValues = None
        self.aValues = None

    # enddef

    ##################################################
    def IsValid(self):
        return (
            self.sName is not None
            and self.iCount is not None
            and self.lProps is not None
        )

    # enddef

    ##################################################
    def IsListArray(self):
        return self.bIsList

    # enddef

    ##################################################
    def GetName(self):
        return self.sName

    # enddef

    ##################################################
    def GetValueCount(self):
        return self.iCount

    # enddef

    ##################################################
    def GetPropNames(self):
        return [x.sName for x in self.lProps]

    # enddef

    ##################################################
    def GetProperty(self, _xId):

        if isinstance(_xId, str):
            return next((x for x in self.lProps if x.sName == _xId), None)
        elif isinstance(_xId, int):
            if _xId < 0 or _xId > len(self.lProps):
                raise CPlyException("Index {0} is out of bounds".format(_xId))
            # endif
            return self.lProps[_xId]
        # endif

        raise CPlyException(
            "Invalid id type '{0}' to access property".format(type(_xId))
        )

    # enddef

    ##################################################
    def GetPropertyCount(self):
        return len(self.lProps)

    # enddef

    ##################################################
    def GetPropertyValues(self, sId=None):
        if self.sFormat == "ascii":
            if sId is None:
                lKeys = self.dicValues.keys()
                if len(lKeys) != 1:
                    raise CPlyException("No property selected")
                # endif
                return self.dicValues.get(lKeys[0])
            else:
                return self.dicValues.get(sId)
            # endif
        else:
            if self.bIsList:
                if sId is None:
                    lKeys = self.dicValues.keys()
                    if len(lKeys) != 1:
                        raise CPlyException("No property selected")
                    # endif
                    return self.dicValues.get(lKeys[0])
                else:
                    return self.dicValues.get(sId)
                # endif
            else:
                if sId is None:
                    lKeys = self.aValues.dtype.names
                    if len(lKeys) != 1:
                        raise CPlyException("No property selected")
                    # endif
                    return self.aValues[lKeys[0]]
                else:
                    return self.aValues[sId]
                # endif
            # endif
        # endif

    # enddef

    ##################################################
    def ParseHeader(self, _lKey, _xStream):
        try:
            self.lProps = []
            lPars = _xStream.GetKeyPars(_lKey, [2])
            self.sName = lPars[0]
            self.iCount = int(lPars[1])
            self.bCanMemMap = self.sFormat != "ascii"
            self.bIsList = False

            while True:
                lKey = _xStream.ReadNextKeywordLineOf(
                    ["element", "property", "end_header"], ["comment"]
                )
                if lKey is None:
                    raise CPlyException("End-of-header keyword not found")
                elif lKey[0] == "end_header" or lKey[0] == "element":
                    break
                else:  # lKey[0] == "property":
                    xProp = CPlyProperty(
                        sFormat=self.sFormat,
                        lParseParameters=_xStream.GetKeyPars(lKey, [2, 4]),
                    )
                    if xProp.IsList():
                        if len(self.lProps) > 0:
                            raise CPlyException(
                                "Unsupported property for element '{0}' at line {1}: Only single list elements or structured scalar elements are supported".format(
                                    _lKey[0], self.xStream.CurrentLine()
                                )
                            )
                        # endif

                        self.bIsList = True
                        self.bCanMemMap = False
                    else:
                        if self.bIsList:
                            raise CPlyException(
                                "Unsupported property for element '{0}' at line {1}: Only single list elements or structured scalar elements are supported".format(
                                    _lKey[0], self.xStream.CurrentLine()
                                )
                            )
                        # endif
                    # endif

                    self.lProps.append(xProp)
                # endif
            # endwhile

            if len(self.lProps) == 0:
                self.lProps = None
                raise CPlyException(
                    "No properties defined for element '{0}' at line {1}".format(
                        _lKey[0], _xStream.CurrentLine()
                    )
                )
            # endif
        except Exception as xEx:
            raise CPlyException(
                "Error reading element '{0}' at line {1}".format(
                    _lKey[0], _xStream.CurrentLine()
                ),
                xEx,
            )
        # endtry

        return lKey

    # enddef

    ##################################################
    def Read(self, _xStream):
        try:
            if not self.IsValid():
                raise CPlyException("Invalid element cannot be read")
            # endif

            if self.sFormat == "ascii":
                self._ReadAscii(_xStream)
            elif (
                self.sFormat == "binary_little_endian"
                or self.sFormat == "binary_big_endian"
            ):
                self._ReadBinary(_xStream)
            # endif
        except Exception as xEx:
            raise CPlyException("Error reading element '{0}'".format(self.sName), xEx)
        # endtry

    # enddef

    ##################################################
    def _ReadAscii(self, _xStream):

        self.dicValues = {}
        self.aValues = None
        iRowCnt = self.iCount

        if self.bIsList:
            lRows = []
            for iRowIdx in range(iRowCnt):
                lRow = _xStream.ReadLineAsList()
                iColCnt = int(lRow[0])
                if iColCnt + 1 != len(lRow):
                    raise CPlyException(
                        "Expected {0} elements in list at row {1}, found {2}".format(
                            iColCnt + 1, _xStream.CurrentLine(), len(lRow)
                        )
                    )
                # endif
                sRow = " ".join(lRow[1:])
                aRowVal = np.fromstring(sRow, dtype=self.lProps[0].GetElType(), sep=" ")
                lRows.append(aRowVal)
            # endfor
            self.dicValues[self.lProps[0].sName] = lRows
        else:
            iColCnt = len(self.lProps)

            lText = []
            for iRowIdx in range(iRowCnt):
                lRow = _xStream.ReadLineAsList()
                if len(lRow) != iColCnt:
                    raise CPlyException(
                        "Expected {0} elements in row {1}, found {2}".format(
                            iColCnt, _xStream.CurrentLine(), len(lRow)
                        )
                    )
                # endif
                lText.append(lRow)
            # endfor
            lText = np.array(lText).transpose()
            for iCol, lCol in enumerate(lText):
                sCol = " ".join(lCol)
                aColVal = np.fromstring(
                    sCol, dtype=self.lProps[iCol].GetElType(), sep=" "
                )
                self.dicValues[self.lProps[iCol].sName] = aColVal
            # endfor
        # endif

    # enddef

    ##################################################
    def _ReadBinary(self, _xStream):

        iRowCnt = self.iCount

        if self.bIsList:
            self.aValues = None
            self.dicValues = {}
            xProp = self.lProps[0]
            lValues = []
            for iRowIdx in range(iRowCnt):
                aCount = _xStream.ReadBinaryArray(xDType=xProp.GetCntType(), iCount=1)
                lValues.append(
                    _xStream.ReadBinaryArray(xDType=xProp.GetElType(), iCount=aCount[0])
                )
            # endfor
            self.dicValues[xProp.sName] = lValues
        else:
            self.aValues = None
            self.dicValues = None
            lTypes = []
            for xProp in self.lProps:
                lTypes.extend(xProp.GetNamedElType().descr)
            # endfor
            xDType = np.dtype(lTypes)
            self.aValues = _xStream.ReadBinaryArray(xDType=xDType, iCount=iRowCnt)
        # endif

    # enddef


# endclass
