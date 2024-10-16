#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \unit_test\class_pointcloud.py
# Created Date: Wednesday, April 21st 2021, 4:09:34 pm
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

import math
import numpy as np

import bpy
import bmesh
from .plyio import CPlyReader
from anybase import config
from anybase.cls_anyexcept import CAnyExcept
import anyblend
from . import solids

# Representation of point cloud objects in Blender scene graph
class CPointCloud:

    ###################################################################
    def __init__(self, _sName):

        self.sName = _sName

    # enddef

    ###################################################################
    def GetName(self):
        return self.sName

    # enddef

    ###################################################################
    def Import(self, *, xContext, sFilePath, fImportPercent, fVoxelSize, bUseVoxel):

        print("Reading data from '{0}'...".format(sFilePath))
        xPly = CPlyReader()
        xPly.Read(sFilePath)
        xVexList = xPly.GetElement("vertex")

        fPerc = fImportPercent / 100.0
        iTotalElCnt = xVexList.GetValueCount()
        print("Found {0} elements. Reading...".format(iTotalElCnt))
        # return {"FINISHED"}

        lPosFull = np.c_[
            xVexList.GetPropertyValues("x").astype(np.float32),
            xVexList.GetPropertyValues("y").astype(np.float32),
            xVexList.GetPropertyValues("z").astype(np.float32),
        ]

        lColFull = (
            np.c_[
                xVexList.GetPropertyValues("red").astype(np.float32),
                xVexList.GetPropertyValues("green").astype(np.float32),
                xVexList.GetPropertyValues("blue").astype(np.float32),
            ]
            / 255.0
        )

        print("Checking validity...")
        lPosIdx = np.transpose(np.argwhere(np.all(np.isfinite(lPosFull), axis=1)))[
            0
        ].astype(int)
        lPosValid = lPosFull[lPosIdx]
        lColValid = lColFull[lPosIdx]

        print("Extracting {0}% of points".format(fImportPercent))
        if fPerc == 1.0:
            lPos = lPosValid
            lCol = lColValid
        elif fPerc * iTotalElCnt < 1.0:
            lPos = [lPosValid[0]]
            lCol = [lColValid[0]]
        else:
            lDataIdx = np.transpose(
                np.argwhere(
                    np.round(np.fmod(fPerc * np.arange(len(lPosValid)), 1.0), 2) < fPerc
                )
            )[0]
            lPos = lPosValid[lDataIdx]
            lCol = lColValid[lDataIdx]
        # endif

        iElCnt = len(lPos)
        print("Using {0} elements...".format(iElCnt))

        print("Preparing colors...")
        lCol = np.c_[lCol, np.ones(iElCnt)]

        if bUseVoxel:
            print("Mapping vertices to voxel grid...")
            lG, lGidx = np.unique(
                np.round(lPos / fVoxelSize), return_index=True, axis=0
            )
            lPos = lG * fVoxelSize
            print("Using {0} voxel...".format(len(lPos)))
            lCol = lCol[lGidx]
        # endif

        lCol_flat = lCol.flatten()

        print("Creating image...")
        iVexCnt = len(lPos)
        iImgW = 2048
        iImgH = int(math.ceil(iVexCnt / iImgW))
        dHalfX = 1.0 / (2.0 * iImgW)
        dHalfY = 1.0 / (2.0 * iImgH)

        sImgName = self.sName + ".Color"
        imgA = bpy.data.images.new(sImgName, iImgW, iImgH)
        sImgName = imgA.name
        # bpy.ops.image.new(name=sImgName, width=iImgW, height=iImgH)
        # imgA = bpy.data.images[sImgName]
        imgA.use_fake_user = True

        iPixCnt = iImgW * iImgH
        iColorCnt = len(lCol)

        iAddCnt = iPixCnt - iColorCnt
        imgA.pixels = list(np.r_[lCol_flat, np.zeros(iAddCnt * 4)])
        anyblend.ops_image.Pack(imgA)

        # print(imgA.name)
        texA = bpy.data.textures.new(self.sName + ".Color.Tex", type="IMAGE")
        # print(texA.name)
        texA.image = imgA
        texA.use_fake_user = True
        # print(texA.image.name)
        print("Creating vertex list...")

        #################################
        # Squares
        # dEh = 0.5*fVoxelSize
        # lV1 = lPos + [-dEh, -dEh, 0.0]
        # lV2 = lPos + [dEh, -dEh, 0.0]
        # lV3 = lPos + [dEh,  dEh, 0.0]
        # lV4 = lPos + [-dEh,  dEh, 0.0]
        # lP = [lV1, lV2, lV3, lV4]
        # lP = np.swapaxes(lP, 0, 1)
        # lP = lP.reshape(4*iVexCnt, 3)

        # lF = np.arange(4*iVexCnt)
        # lF = lF.reshape(iVexCnt, 4)

        #################################
        # Triangles
        dH2 = math.sqrt(3) * 0.25 * fVoxelSize
        dS2 = fVoxelSize * 0.5
        lV1 = lPos + [-dS2, -dH2, 0.0]
        lV2 = lPos + [0.0, dH2, 0.0]
        lV3 = lPos + [dS2, -dH2, 0.0]
        lP = [lV1, lV2, lV3]
        lP = np.swapaxes(lP, 0, 1)
        lP = lP.reshape(3 * iVexCnt, 3)

        lF = np.arange(3 * iVexCnt)
        lF = lF.reshape(iVexCnt, 3)
        #################################

        print("Creating mesh...")

        objA = anyblend.object.CreateObject(xContext, self.sName)
        meshA = objA.data
        meshA.from_pydata(lP.tolist(), [], lF.tolist())

        print("Setting texture coordinates...")
        bm = bmesh.new()
        bm.from_mesh(meshA)
        bm.faces.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.verify()
        # bm.faces.layers.tex.verify()

        uv_layer = bm.loops.layers.uv[0]
        for iIdx, faceA in enumerate(bm.faces):
            iY = int(math.floor(iIdx / iImgW))
            iX = iIdx - iY * iImgW
            dY = iY / iImgH + dHalfY
            dX = iX / iImgW + dHalfX
            faceA.loops[0][uv_layer].uv = (dX, dY)
            faceA.loops[1][uv_layer].uv = (dX, dY)
            faceA.loops[2][uv_layer].uv = (dX, dY)
            # faceA.loops[3][uv_layer].uv = (dX, dY)
        # endfor
        bm.to_mesh(meshA)
        bm.free()

        #############################################################
        print("Creating particle prototype...")
        sNameP = self.sName + ".Particle"

        # Create the material with texture color
        sNameMat = sNameP + ".Mat.Tex"
        matTex = bpy.data.materials.new(name=sNameMat)
        matTex.use_nodes = True
        matTex.use_fake_user = True
        nodesP = matTex.node_tree.nodes
        linksP = matTex.node_tree.links

        nodeBSDF = nodesP.get("Principled BSDF")
        inBC = nodeBSDF.inputs["Base Color"]
        inBC.default_value = (0, 0, 0, 1)

        nodeTex = nodesP.new("ShaderNodeTexImage")
        nodeTex.location = (-300, 300)
        nodeTex.image = imgA

        nodeTC = nodesP.new("ShaderNodeTexCoord")
        nodeTC.location = (-500, 300)
        nodeTC.from_instancer = True

        linksP.new(nodeTex.inputs["Vector"], nodeTC.outputs["UV"])
        linksP.new(nodeBSDF.inputs["Emission"], nodeTex.outputs["Color"])

        # Create the material with single color
        sNameMat = sNameP + ".Mat.Color"
        matCol = bpy.data.materials.new(name=sNameMat)
        matCol.use_nodes = True
        matCol.use_fake_user = True
        nodesP = matCol.node_tree.nodes
        linksP = matCol.node_tree.links

        nodeBSDF = nodesP.get("Principled BSDF")
        inBC = nodeBSDF.inputs["Base Color"]
        inBC.default_value = (0.85, 0.01, 0.015, 1)
        nodeBSDF.inputs["Roughness"].default_value = 0.1

        # Create the Cube particle object
        objPartCube = solids.CreateCube(xContext, sNameP + ".Cube", 1.0)
        objPartCube.active_material = matTex
        objPartCube.hide_set(True)

        # Create the Tetrahedron particle object
        objPartTetra = solids.CreateTetraeder(xContext, sNameP + ".Tetra", 1.0)
        objPartTetra.active_material = matTex
        objPartTetra.hide_set(True)

        #############################################################
        print("Creating particle system...")
        iMaxPartShown = 10000
        # dViewRatio = max(1.0, min(100.0 * iMaxPartShown / iVexCnt, 100.0))

        pmA = objA.modifiers.new(self.sName, type="PARTICLE_SYSTEM")
        psA = objA.particle_systems[pmA.name]
        psetA = psA.settings

        # psetA.count = iVexCnt
        # psetA.type = "HAIR"
        # psetA.hair_length = 1.0
        # psetA.hair_step = 2
        # psetA.emit_from = "FACE"
        # psetA.distribution = "JIT"
        # psetA.use_emit_random = False
        # psetA.userjit = 1
        # psetA.jitter_factor = 0.0
        # psetA.render_type = "OBJECT"
        # psetA.particle_size = fVoxelSize
        # psetA.instance_object = objPartCube
        # psetA.display_percentage = dViewRatio

        psetA.count = iVexCnt
        psetA.type = "EMITTER"
        psetA.frame_start = 0
        psetA.frame_end = 0
        psetA.lifetime = 1000000
        psetA.hair_length = 1.0
        psetA.hair_step = 2
        psetA.emit_from = "FACE"
        psetA.distribution = "JIT"
        psetA.use_emit_random = False
        psetA.userjit = 1
        psetA.jitter_factor = 0.0

        psetA.normal_factor = 0.0
        psetA.physics_type = "NO"
        psetA.render_type = "OBJECT"
        psetA.particle_size = fVoxelSize
        psetA.instance_object = objPartCube

        psetA.display_method = "DOT"
        psetA.display_percentage = 100
        psetA.display_size = fVoxelSize

        objA.show_instancer_for_render = False
        objA.show_instancer_for_viewport = False

    # enddef

    ###################################################################
    def Remove(self):
        anyblend.object.RemoveCollection(self.sName)

    # enddef

    ###################################################################
    def GetObject(self):

        objPcl = bpy.data.objects.get(self.sName)
        if objPcl is None:
            raise Exception(
                "Point cloud object with name '{0}' not found".format(self.sName)
            )
        # endif

        return objPcl

    # enddef

    ###################################################################
    def GetParticleSystem(self):

        objPcl = self.GetObject()

        psPcl = objPcl.particle_systems.get(self.sName)
        if psPcl is None:
            raise Exception(
                "Point cloud with name '{0}' does not have a particle system of the same name".format(
                    self.sName
                )
            )
        # endif

        return psPcl

    # enddef

    ###################################################################
    def GetParticleObject(self, sType):

        sPartName = "{0}.Particle.{1}".format(self.sName, sType)
        objPart = bpy.data.objects.get(sPartName)
        if objPart is None:
            raise Exception(
                "Particle object with name '{0}' not found".format(sPartName)
            )
        # endif

        return objPart

    # enddef

    ###################################################################
    def IsValid(self):
        return bpy.data.objects.get(self.sName) is not None

    # enddef

    ###################################################################
    def AssertIsValid(self):
        if not self.IsValid():
            raise Exception(
                "Point cloud object with name '{0}' not found".format(self.sName)
            )
        # endif

    # enddef

    ###################################################################
    def _GetElementNamesOfType(self, *, sType, xContainer):

        sPat = "{0}.{1}.".format(self.sName, sType)
        lEl = [x for x in xContainer if x.name.startswith(sPat)]

        iStartIdx = len(sPat)
        lElNames = []
        for xEl in lEl:
            lElNames.append(xEl.name[iStartIdx:])
        # endfor

        return lElNames

    # enddef

    ###################################################################
    def GetParticleTypes(self):

        self.AssertIsValid()
        return self._GetElementNamesOfType(
            sType="Particle", xContainer=bpy.data.objects
        )

    # enddef

    ###################################################################
    def GetParticleMaterialTypes(self):

        self.AssertIsValid()
        return self._GetElementNamesOfType(
            sType="Particle.Mat", xContainer=bpy.data.materials
        )

    # enddef

    ###################################################################
    def GetParticleMaterial(self, _sType):

        sMatName = "{0}.Particle.Mat.{1}".format(self.sName, _sType)
        matPart = bpy.data.materials.get(sMatName)
        if matPart is None:
            raise Exception(
                "Particle material with name '{0}' not found".format(sMatName)
            )
        # endif

        return matPart

    # enddef

    ###################################################################
    def SetParticleType(self, _sType):

        psPcl = self.GetParticleSystem()
        objPart = self.GetParticleObject(_sType)

        psPcl.settings.instance_object = objPart

    # enddef

    ###################################################################
    # Expects material dictionary of type "point-cloud/material:1"
    def SetActiveParticleMaterial(self, _dicMaterial):

        psPcl = self.GetParticleSystem()
        self._SetObjectMaterial(
            xObject=psPcl.settings.instance_object, dicMaterial=_dicMaterial
        )

    # enddef

    ###################################################################
    def SetParticleMaterial(self, *, sParticleType, dicMaterial):

        objPart = self.GetParticleObject(sParticleType)
        self._SetObjectMaterial(xObject=objPart, dicMaterial=dicMaterial)

    # enddef

    ###################################################################
    def _SetObjectMaterial(self, *, xObject, dicMaterial):

        sDti = "point-cloud/material:1"
        dicResult = config.CheckConfigType(dicMaterial, sDti)
        if not dicResult.get("bOK"):
            raise CAnyExcept(
                "Expect particle material dictionary of type '{0}', found type '{1}'".format(
                    sDti, dicResult.get("sCfgDti")
                )
            )
        # endif

        lMatTypes = self.GetParticleMaterialTypes()
        sType = dicMaterial.get("sType")
        if sType is None:
            raise CAnyExcept("No material type given")
        # endif

        if sType not in lMatTypes:
            raise CAnyExcept(
                "Material type '{0}' not supported. Available types are: {1}".format(
                    sType, lMatTypes
                )
            )
        # endif

        matPart = self.GetParticleMaterial(sType)

        nodesP = matPart.node_tree.nodes
        nodeBSDF = nodesP.get("Principled BSDF")

        lBaseColor_rgba = dicMaterial.get("lBaseColor_rgba")
        if lBaseColor_rgba is not None:
            nodeBSDF.inputs["Base Color"].default_value = tuple(lBaseColor_rgba)
        # endif

        fRoughness = dicMaterial.get("fRoughness")
        if fRoughness is not None:
            nodeBSDF.inputs["Roughness"].default_value = float(fRoughness)
        # endif

        xObject.active_material = matPart

    # enddef


# endclass
