#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \class_pointcloudset.py
# Created Date: Tuesday, April 20th 2021, 2:43:48 pm
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
import os
import re

from pathlib import Path
from anybase import config
from anybase.cls_anyexcept import CAnyExcept
import anyblend
from . import pcimport


class CPointCloudSet:

    ####################################################################################
    # Constructor
    def __init__(self):

        self.dicPcSet = None

        self.Clear()

    # enddef

    ####################################################################################
    # Clear point cloud set
    def Clear(self):
        self.dicPcSet = {}

    # enddef

    ####################################################################################
    # Load data from file
    def AddFromFile(self, _sFpData):

        xPath = Path(_sFpData)
        sCfgPath = xPath.parent.as_posix()
        sCfgFile = xPath.name

        dicCfg = config.Load(xPath, sDTI="/catharsys/point-cloud/set:1")
        lPointClouds = dicCfg.get("lPointClouds")

        for dicCfg in lPointClouds:
            if dicCfg.get("sName") in self.dicPcSet:
                raise CAnyExcept(
                    "Point cloud name '{0}' duplicate while loading '{1}'".format(
                        dicCfg.get("sName"), sCfgFile
                    )
                )
            # endif

            sPathData = os.path.join(sCfgPath, dicCfg.get("sPath"))
            sFilePat = dicCfg.get("sFilePattern")
            sFileIdType = dicCfg.get("sFileIdType", "str")

            rePat = re.compile(sFilePat)
            lFiles = [x for x in os.listdir(sPathData) if rePat.match(x)]

            dicPc = self.dicPcSet[dicCfg.get("sName")] = {}
            dicPc["iId"] = dicCfg.get("iId")

            dicFrames = dicPc["dicFrames"] = {}

            for sFile in lFiles:
                xMatch = rePat.search(sFile)
                sFrame = xMatch.group(1)
                if sFileIdType == "int":
                    sFrame = str(int(sFrame))
                # endif

                dicFrames[sFrame] = {
                    "sFpData": os.path.normpath(os.path.join(sPathData, sFile)),
                    "sFrame": sFrame,
                    "xPcl": None,
                }
            # endif

        # endfor

    # enddef

    ####################################################################################
    def GetFrame(self, _sName, _sFrame):

        dicPc = self.dicPcSet.get(_sName)
        if dicPc is None:
            raise CAnyExcept("Point cloud with name '{0}' not found".format(_sName))
        # endif

        dicFrames = dicPc.get("dicFrames")
        dicFrame = dicFrames.get(str(_sFrame))
        if dicFrame is None:
            raise CAnyExcept(
                "Frame {0} for point cloud '{1}' not found".format(_sFrame, _sName)
            )
        # endif

        return dicFrame

    # enddef

    ####################################################################################
    def GetCount(self):
        return len(self.dicPcSet)

    # enddef

    ####################################################################################
    def GetNames(self):
        return list(self.dicPcSet.keys())

    # enddef

    ####################################################################################
    def GetFrames(self, _sName):

        dicPc = self.dicPcSet.get(_sName)
        if dicPc is None:
            raise CAnyExcept("Point cloud with name '{0}' not found".format(_sName))
        # endif

        dicFrames = dicPc.get("dicFrames")
        return list(dicFrames.keys())

    # enddef

    ####################################################################################
    # Import point cloud with given name and frame id
    def ImportSingle(self, _sName, _sFrame, bForce=False):

        dicFrame = self.GetFrame(_sName, _sFrame)

        if dicFrame.get("xPcl") is not None:
            if not bForce:
                return
            # endif
            anyblend.collection.RemoveCollection(dicFrame.get("xPcl").GetName())
            dicFrame["xPcl"] = None
        # endif

        sFpData = dicFrame.get("sFpData")

        xPcl = pcimport.ImportPointCloud(
            bpy.context, sFpData, sName="{0}.{1}".format(_sName, _sFrame)
        )
        dicFrame["xPcl"] = xPcl

    # enddef

    ####################################################################################
    # Import point cloud set
    def ImportSet(self, _lNames, _lFrames, bForce=False):

        for sName in _lNames:
            for sFrame in _lFrames:
                self.ImportSingle(sName, sFrame, bForce=bForce)
            # endfor
        # endfor

    # enddef

    ####################################################################################
    def Import(self, _xNames, _xFrames, bForce=False):

        if isinstance(_xNames, str) and isinstance(_xFrames, str):
            self.ImportSingle(_xNames, _xFrames, bForce=bForce)
        elif hasattr(_xNames, "__iter__") and hasattr(_xFrames, "__iter__"):
            self.ImportSet(_xNames, _xFrames, bForce=bForce)
        else:
            raise Exception(
                "Arguments either have to be two strings or two iterable objects"
            )
        # endif

    # enddef

    ####################################################################################
    def SetParticleMaterialForSet(self, _lNames, _lFrames, _dicMaterial):

        for sName in _lNames:
            for sFrame in _lFrames:
                self.SetParticleMaterialSingle(sName, sFrame, _dicMaterial)
            # endfor
        # endfor

    # enddef

    ####################################################################################
    def SetParticleMaterialSingle(self, _sName, _sFrame, _dicMaterial):

        dicFrame = self.GetFrame(_sName, _sFrame)
        xPcl = dicFrame.get("xPcl")
        if xPcl is None:
            raise Exception(
                "Frame {0} of point cloud '{1}' is not loaded".format(_sFrame, _sName)
            )
        # endif

        xPcl.SetActiveParticleMaterial(_dicMaterial)

    # enddef

    ####################################################################################
    def SetParticleMaterial(self, _xNames, _xFrames, _dicMaterial):

        if isinstance(_xNames, str) and isinstance(_xFrames, str):
            self.SetParticleMaterialSingle(_xNames, _xFrames, _dicMaterial)

        elif hasattr(_xNames, "__iter__") and hasattr(_xFrames, "__iter__"):
            self.SetParticleMaterialForSet(_xNames, _xFrames, _dicMaterial)

        else:
            raise Exception(
                "Arguments either have to be two strings or two iterable objects"
            )
        # endif

    # enddef

    ####################################################################################
    # Import point cloud set
    def RemovePointCloudSet(self, _lNames, _lFrames):

        for sName in _lNames:
            for sFrame in _lFrames:
                self.RemovePointCloud(sName, sFrame)
            # endfor
        # endfor

    # enddef

    ####################################################################################
    # Import point cloud set
    def RemovePointCloudDict(self, _dicPcl):

        for sName in _dicPcl:
            lFrames = _dicPcl.get(sName)
            for sFrame in lFrames:
                self.RemovePointCloud(sName, sFrame)
            # endfor
        # endfor

    # enddef

    ####################################################################################
    # Remove imported point cloud from Blender scene graph
    def RemovePointCloud(self, _sName, _sFrame):

        dicFrame = self.GetFrame(_sName, _sFrame)

        xPcl = dicFrame.get("xPcl")
        if xPcl is not None:
            xPcl.Remove()
            dicFrame["xPcl"] = None
        # endif

    # enddef

    ####################################################################################
    # Remove all imported point clouds from Blender scene graph
    def RemoveAllPointClouds(self):

        for sPc in self.dicPcSet:
            dicPc = self.dicPcSet.get(sPc)

            dicFrames = dicPc.get("dicFrames")
            for sFrame in dicFrames:
                dicFrame = dicFrames.get(sFrame)
                xPcl = dicFrame.get("xPcl")
                if xPcl is not None:
                    xPcl.Remove()
                    dicFrame["xPcl"] = None
                # endif
            # endfor
        # endfor

    # enddef


# endclass
