#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \class_pointcloudselection.py
# Created Date: Thursday, April 22nd 2021, 8:47:01 am
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

import copy
from anybase import config
from anybase.cls_anyexcept import CAnyExcept


class CPointCloudSelection:

    ###########################################################################################################
    def __init__(self):
        self.dicSel = None
        self.xPcs = None

    # enddef

    ###########################################################################################################
    # Initialize instance from dictionary containing a "point-cloud/selection:1" config structure,
    # and an initialized CPointCloudSet instance.
    def Init(self, *, dicSel, xPointCloudSet):

        sDti = "point-cloud/selection:1"
        dicResult = config.CheckConfigType(dicSel, sDti)
        if not dicResult.get("bOK"):
            raise CAnyExcept(
                "Expect point cloud selection configuration of type '{0}', but found '{1}'".format(
                    sDti, dicResult.get("sCfgDti")
                )
            )
        # endif

        self.dicSel = copy.deepcopy(dicSel)
        self.xPcs = xPointCloudSet

    # enddef

    ###########################################################################################################
    def IsValid(self):
        return self.dicSel is not None and self.xPcs is not None

    # enddef

    ###########################################################################################################
    def AssertValid(self):
        if not self.IsValid():
            raise CAnyExcept("Point cloud selection class instance not valid")
        # endif

    # enddef

    ###########################################################################################################
    # Import point clouds of selection
    # if bAnimated is true, then only import animated point clouds for the given frame.
    # Otherwise, import only static point clouds.

    def Import(self, *, bUseAnimated, iFrame=None):

        self.AssertValid()
        if bUseAnimated and iFrame is None:
            raise CAnyExcept("No frame number given for animated point cloud import")
        # endif

        # store names and frames of imported point clouds and return them to caller
        dicSel = {}

        bDefAnimate = self.dicSel.get("bAnimate", False)
        iDefFrameOffset = self.dicSel.get("iFrameOffset", 0)

        dicDefMat = self.dicSel.get("mMaterial")
        lDefFrameId = self.dicSel.get("lFrameId")

        dicNames = self.dicSel.get("mNames")
        if dicNames is None:
            lNames = self.xPcs.GetNames()
        else:
            lNames = list(dicNames.keys())
        # endif

        for sName in lNames:

            if dicNames is None:
                # initialize with default settings
                bAnimate = bDefAnimate
                iFrameOffset = iDefFrameOffset
                dicMat = dicDefMat
                lFrameId = lDefFrameId

            else:
                dicData = dicNames.get(sName)
                bAnimate = dicData.get("bAnimate", bDefAnimate)
                iFrameOffset = dicData.get("iFrameOffset", iDefFrameOffset)
                lFrameId = dicData.get("lFrameId", lDefFrameId)
                dicMat = dicData.get("mMaterial", dicDefMat)

            # endif

            bDoImport = False
            if bUseAnimated and bAnimate:
                lFrameId = [str(iFrame + iFrameOffset)]
                bDoImport = True

            elif not bUseAnimated and not bAnimate:

                if lFrameId is None:
                    lFrameId = self.xPcs.GetFrames(sName)
                # endif
                bDoImport = True
            # endif

            if bDoImport:
                if not isinstance(lFrameId, list):
                    raise CAnyExcept(
                        "Element 'lFrameId' must be a list, received: {0}".format(
                            str(lFrameId)
                        )
                    )
                # endif
                dicSel[sName] = lFrameId

                # Actually import the point clouds
                self.xPcs.Import([sName], lFrameId)

                if dicMat is not None:
                    self.xPcs.SetParticleMaterial([sName], lFrameId, dicMat)
                # endif
            # endif

        # endfor

        return dicSel

    # enddef


# endclass
