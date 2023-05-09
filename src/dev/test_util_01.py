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

import bpy
from anypoints import util
from anypoints import solids

xActCol = util.GetActiveCollection(bpy.context)
print("Active Collection: {0}".format(xActCol.name))

# xCol = util.CreateCollection(bpy.context, "test")
# objCube = solids.CreateCube(bpy.context, "TestCube", 2.0)

# xCol = util.FindLayerCollection(bpy.context.view_layer.layer_collection, "test")
# print(xCol.objects)

# util.RemoveCollection("test")
# util.RemoveOrphaned()

util.SetActiveCollection(bpy.context, xActCol.name)
