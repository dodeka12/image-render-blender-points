#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \plyexception.py
# Created Date: Tuesday, March 16th 2021, 8:54:38 am
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


class CPlyException(Exception):
    def __init__(self, _sMsg, xEx=None):

        if xEx is not None:
            lMsg = [_sMsg]
            lLines = str(xEx).split("\n")
            for sLine in lLines:
                if sLine.startswith(">"):
                    sLine = ">" + sLine
                else:
                    sLine = "> " + sLine
                # endif
                lMsg.append(sLine)
            # endfor

            self.message = "\n".join(lMsg)
        else:
            self.message = _sMsg
        # endif
        super().__init__(self.message)

    # enddef

    ##################################################################################
    @staticmethod
    def Print(_xEx, bTraceback=False):

        import traceback

        print("")
        print("===================================================================")
        print("EXCEPTION ({0})".format(type(_xEx)))
        print(_xEx)
        print("")
        if bTraceback:
            traceback.print_exception(type(_xEx), _xEx, _xEx.__traceback__)
        # endif
        print("===================================================================")
        print("")

    # enddef


# endclass
