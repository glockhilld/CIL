# -*- coding: utf-8 -*-
#  Copyright 2019 United Kingdom Research and Innovation
#  Copyright 2019 The University of Manchester
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# Authors:
# CIL Developers, listed at: https://github.com/TomographicImaging/CIL/blob/master/NOTICE.txt

import numpy
import sys
from datetime import timedelta, datetime
import warnings
from functools import reduce
from .cilacc import cilacc
from .AcquisitionData import AcquisitionData
from .acquisition_geometry import AcquisitionGeometry, SystemConfiguration
from .framework import find_key
from .DataContainer import message, ImageGeometry, DataContainer, ImageData, VectorData, VectorGeometry
from .framework import DataProcessor, Processor
from .framework import AX, PixelByPixelDataProcessor, CastDataContainer
from .BlockDataContainer import BlockDataContainer
from .BlockGeometry import BlockGeometry
from .Partitioner import Partitioner
from .label import acquisition_labels, image_labels, data_order, get_order_for_engine, check_order_for_engine
