#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \__init__.py
# Created Date: Friday, March 12th 2021, 7:52:39 am
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

bl_info = {
    "name": "Point Cloud Particle Import",
    "description": "Simple importer that creates a particle system from point cloud data.",
    "author": "Christian Perwass",
    # "version": (settings.VERSION_MAJOR, settings.VERSION_MINOR),
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import",
    "warning": "",  # "You need to use Cycles in render mode to see the particle colors.",
    # "wiki_url": "",
    # "wiki_url": "",
    # "tracker_url": "",
    # "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Importer",
}

##################################################################
try:
    import _bpy
    import bpy

    # ImportHelper is a helper class, defines filename and
    # invoke() function which calls the file selector.
    from bpy_extras.io_utils import ImportHelper
    from bpy.props import (
        StringProperty,
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
    )
    from bpy.types import Operator

    bInBlenderContext = True

except Exception:
    bInBlenderContext = False
# endtry

if bInBlenderContext is True:
    try:
        import importlib

        if "util" in locals():
            importlib.reload(util)
            # else
            from . import util
        # endif

        if "pcimport" in locals():
            importlib.reload(pcimport)
            # else
            from . import pcimport
        # endif

        if "CPointCloudSet" in locals():
            importlib.reload(CPointCloudSet)
        else:
            from .class_pointcloudset import CPointCloudSet
        # endif

        if "CPointCloud" in locals():
            importlib.reload(CPointCloud)
        else:
            from .class_pointcloud import CPointCloud
        # endif

        if "CPointCloudSelection" in locals():
            importlib.reload(CPointCloudSelection)
        else:
            from .class_pointcloudselection import CPointCloudSelection
        # endif
    except Exception as xEx:
        # pass
        print(">>>> Exception importing libs:\n{}".format(str(xEx)))
    # endif

    ###########################################################################################
    class ImportPointCloud(Operator, ImportHelper):
        """Importing point clouds from PLY files"""

        bl_idname = "import_point_cloud.particles"
        bl_label = "Import Point Cloud"

        # ImportHelper mixin class uses this
        filename_ext = ".ply"

        filter_glob: StringProperty(
            default="*.ply;*.json",
            options={"HIDDEN"},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
        )

        sName: StringProperty(
            name="Object Name",
            description="Object name for the imported point cloud",
            default="PointCloud",
        )

        fImportPrecent: FloatProperty(
            name="Import Percentage",
            description="Percentage of points to import",
            default=100,
        )

        bUseVoxel: BoolProperty(
            name="Use voxel space",
            description="Quantizes space into voxels and only keeps one point per voxel.",
            default=True,
        )

        fVoxelSize: FloatProperty(name="Voxel size", description="Side length of voxel.", default=0.02)

        def execute(self, context):
            pcimport.ImportPointCloud(
                context,
                self.filepath,
                sName=self.sName,
                fImportPercent=self.fImportPrecent,
                bUseVoxel=self.bUseVoxel,
                fVoxelSize=self.fVoxelSize,
            )

            return {"FINISHED"}

        # enddef

    # endclass

# endif in Blender Context

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportPointCloud.bl_idname, text="Particle Point Cloud (*.ply, *.json)")


# enddef


def register():
    bpy.utils.register_class(ImportPointCloud)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


# enddef


def unregister():
    bpy.utils.unregister_class(ImportPointCloud)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


# enddef

# if __name__ == "__main__":
# 	register()

# 	# test call
# 	bpy.ops.import_point_cloud.particles('INVOKE_DEFAULT')
# # endif
