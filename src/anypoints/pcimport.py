#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \pcimport.py
# Created Date: Friday, March 12th 2021, 8:00:16 am
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

import re
import os

import bpy
from pathlib import Path

import anyblend
from .class_pointcloud import CPointCloud
from anybase import config


##########################################################################################
def ImportPly(*, xContext, sFilePath, sName, fImportPercent, fVoxelSize, bUseVoxel):

    xPcl = CPointCloud(sName)
    xPcl.Import(
        xContext=xContext,
        sFilePath=sFilePath,
        fImportPercent=fImportPercent,
        fVoxelSize=fVoxelSize,
        bUseVoxel=bUseVoxel,
    )

    return xPcl


# enddef


#####################################################################################
def ImportSet(*, xContext, sFilePath, sName, fImportPercent, fVoxelSize, bUseVoxel):

    xPath = Path(sFilePath)
    sPath = xPath.parent

    dicSet = config.Load(xPath, sDTI="/catharsys/point-cloud/set:1.0")

    reFrame = re.compile(r"(\d*)\.")
    xActLayCol = anyblend.collection.GetActiveLayerCollection(xContext)

    lPcl = []
    lPC = dicSet.get("lPointClouds")
    for xPC in lPC:
        sPathData = xPC.get("sPath")
        sPcId = sPathData.split("/")[0]
        sFilePat = xPC.get("sFilePattern")
        rePat = re.compile(sFilePat)
        sPathData = os.path.join(sPath, sPathData)
        lFiles = [x for x in os.listdir(sPathData) if rePat.match(x)]
        # print(lFiles)

        for sFile in lFiles:
            xMatch = reFrame.search(sFile)
            iFrame = int(xMatch.group(1))
            sFrameColName = "{0}.Frame.{1:04d}".format(sName, iFrame)
            if sFrameColName in bpy.data.collections:
                anyblend.collection.SetActiveCollection(xContext, sFrameColName)
            else:
                anyblend.collection.CreateCollection(xContext, sFrameColName)
            # endif

            sPcColName = "{0}.{1}".format(sFrameColName, sPcId)
            if sPcColName in bpy.data.collections:
                anyblend.collection.SetActiveCollection(xContext, sPcColName)
            else:
                anyblend.collection.CreateCollection(xContext, sPcColName)
            # endif

            sFpData = os.path.join(sPathData, sFile)

            xPcl = ImportPly(
                xContext=xContext,
                sFilePath=sFpData,
                sName=sPcColName,
                fImportPercent=fImportPercent,
                fVoxelSize=fVoxelSize,
                bUseVoxel=bUseVoxel,
            )
            lPcl.append(xPcl)

            anyblend.collection.SetActiveLayerCollection(xContext, xActLayCol)
        # endfor

    # endfor

    anyblend.collection.SetActiveLayerCollection(xContext, xActLayCol)
    return lPcl


# enddef


#####################################################################################
def ImportPointCloud(
    _xContext,
    _sFilePath,
    sName="PointCloud",
    fImportPercent=100.0,
    bUseVoxel=True,
    fVoxelSize=0.02,
):

    xActLayCol = anyblend.collection.GetActiveLayerCollection(_xContext)
    # xCollection = anyblend.collection.CreateCollection(_xContext, sName)

    xP = Path(_sFilePath)
    if xP.suffix == ".json":
        xResult = ImportSet(
            xContext=_xContext,
            sFilePath=_sFilePath,
            sName=sName,
            fImportPercent=fImportPercent,
            fVoxelSize=fVoxelSize,
            bUseVoxel=bUseVoxel,
        )

    elif xP.suffix == ".ply":
        xResult = ImportPly(
            xContext=_xContext,
            sFilePath=_sFilePath,
            sName=sName,
            fImportPercent=fImportPercent,
            fVoxelSize=fVoxelSize,
            bUseVoxel=bUseVoxel,
        )
    else:
        raise Exception("Invalid file type '{0}'".format(xP.suffix))
    # endif

    anyblend.collection.SetActiveLayerCollection(_xContext, xActLayCol)

    #############################################################
    print("Finished...")
    return xResult


# enddef
