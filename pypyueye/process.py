# -*- coding: utf-8 -*-
#!/usr/env python3

# Copyright (C) 2021 J L Garrett

# Author: J L Garrett  <j.landon.garrett@gmail.com>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json
import numpy as np
import imageio as iio

class Processing(object):
    """
    This class defines the processing done on incoming images in the
    the pypyueye library, and can be used by threads_processing

    the parameters should be defined in a .json config file

    the output file name is defined separately, so that it can
    be chosen from the command line
    """
    def __init__(self, config_file, base_name, folder):
        self.config_file = config_file
        self.base_name = base_name
        self.folder = folder

        with open(config_file) as f:
            self.config = json.load(f)

        self.tempfile = self.folder + self.base_name + ".temp"
        self.initialized = False
        self.define_temp_file()

        # here you would initialize the config parameters

    def define_temp_file(self):
        # this should be done in the case that the file is saved as a 1-d image
        with open(self.tempfile, "wb") as f:
            print("initializing ", self.base_name + ".temp")

    def finish(self):
        intermediate = np.fromfile(self.tempfile,
                                   dtype = self.output_dtype)
        print(intermediate.shape, intermediate.dtype)
        print(intermediate)
        iio.imwrite(self.folder + self.base_name + '.tiff', intermediate.reshape(self.output_shape + (-1,)))

        return 0

    def process(self, x):
        #do any preprocessing to image

        #do main processing
        #this current sum is just a placeholder
        a_list = np.sum(x, dtype = np.uint16, axis = 1)

        # on the first execution, set capture parameters
        # so that the data shape/type does not change
        if not self.initialized:
            self.initialized = True
            self.input_shape = x.shape
            self.output_shape = a_list.shape
            self.output_dtype = a_list.dtype
        else:
            if x.shape != self.input_shape:
                print("input frame size change")
                return -1
            elif a_list.shape != self.output_shape:
                print("output frame size change")
                return -2
            elif a_list.dtype != self.output_dtype:
                print("output dtype change")
                return -3

        #save image
        with open(self.tempfile, 'a') as f:
            np.array(a_list).tofile(f)



