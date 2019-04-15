# -*- coding: utf-8 -*-
#   This work is part of the Core Imaging Library developed by
#   Visual Analytics and Imaging System Group of the Science Technology
#   Facilities Council, STFC

#   Copyright 2018-2019 Edoardo Pasca

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy
import sys
from datetime import timedelta, datetime
import warnings
from functools import reduce
from numbers import Number


def find_key(dic, val):
    """return the key of dictionary dic given the value"""
    return [k for k, v in dic.items() if v == val][0]

def message(cls, msg, *args):
    msg = "{0}: " + msg
    for i in range(len(args)):
        msg += " {%d}" %(i+1)
    args = list(args)
    args.insert(0, cls.__name__ )
    
    return msg.format(*args )


class ImageGeometry(object):
    RANDOM = 'random'
    RANDOM_INT = 'random_int'
    CHANNEL = 'channel'
    ANGLE = 'angle'
    VERTICAL = 'vertical'
    HORIZONTAL_X = 'horizontal_x'
    HORIZONTAL_Y = 'horizontal_y'
    
    def __init__(self, 
                 voxel_num_x=0, 
                 voxel_num_y=0, 
                 voxel_num_z=0, 
                 voxel_size_x=1, 
                 voxel_size_y=1, 
                 voxel_size_z=1, 
                 center_x=0, 
                 center_y=0, 
                 center_z=0, 
                 channels=1):
        
        self.voxel_num_x = voxel_num_x
        self.voxel_num_y = voxel_num_y
        self.voxel_num_z = voxel_num_z
        self.voxel_size_x = voxel_size_x
        self.voxel_size_y = voxel_size_y
        self.voxel_size_z = voxel_size_z
        self.center_x = center_x
        self.center_y = center_y
        self.center_z = center_z  
        self.channels = channels
        
        # this is some code repetition
        if self.channels > 1:            
            if self.voxel_num_z>1:
                self.length = 4
                self.shape = (self.channels, self.voxel_num_z, self.voxel_num_y, self.voxel_num_x)
                dim_labels = [ImageGeometry.CHANNEL, ImageGeometry.VERTICAL,
                ImageGeometry.HORIZONTAL_Y, ImageGeometry.HORIZONTAL_X]
            else:
                self.length = 3
                self.shape = (self.channels, self.voxel_num_y, self.voxel_num_x)
                dim_labels = [ImageGeometry.CHANNEL, ImageGeometry.HORIZONTAL_Y, ImageGeometry.HORIZONTAL_X]
        else:
            if self.voxel_num_z>1:
                self.length = 3
                self.shape = (self.voxel_num_z, self.voxel_num_y, self.voxel_num_x)
                dim_labels = [ImageGeometry.VERTICAL, ImageGeometry.HORIZONTAL_Y,
                 ImageGeometry.HORIZONTAL_X]
            else:
                self.length = 2  
                self.shape = (self.voxel_num_y, self.voxel_num_x)
                dim_labels = [ImageGeometry.HORIZONTAL_Y, ImageGeometry.HORIZONTAL_X]
        
        self.dimension_labels = dim_labels
        
    def get_min_x(self):
        return self.center_x - 0.5*self.voxel_num_x*self.voxel_size_x
        
    def get_max_x(self):
        return self.center_x + 0.5*self.voxel_num_x*self.voxel_size_x
        
    def get_min_y(self):
        return self.center_y - 0.5*self.voxel_num_y*self.voxel_size_y
        
    def get_max_y(self):
        return self.center_y + 0.5*self.voxel_num_y*self.voxel_size_y
        
    def get_min_z(self):
        if not self.voxel_num_z == 0:
            return self.center_z - 0.5*self.voxel_num_z*self.voxel_size_z
        else:
            return 0
        
    def get_max_z(self):
        if not self.voxel_num_z == 0:
            return self.center_z + 0.5*self.voxel_num_z*self.voxel_size_z
        else:
            return 0
        
    def clone(self):
        '''returns a copy of ImageGeometry'''
        return ImageGeometry(
                            self.voxel_num_x, 
                            self.voxel_num_y, 
                            self.voxel_num_z, 
                            self.voxel_size_x, 
                            self.voxel_size_y, 
                            self.voxel_size_z, 
                            self.center_x, 
                            self.center_y, 
                            self.center_z, 
                            self.channels)
    def __str__ (self):
        repres = ""
        repres += "Number of channels: {0}\n".format(self.channels)
        repres += "voxel_num : x{0},y{1},z{2}\n".format(self.voxel_num_x, self.voxel_num_y, self.voxel_num_z)
        repres += "voxel_size : x{0},y{1},z{2}\n".format(self.voxel_size_x, self.voxel_size_y, self.voxel_size_z)
        repres += "center : x{0},y{1},z{2}\n".format(self.center_x, self.center_y, self.center_z)
        return repres
    def allocate(self, value=0, dimension_labels=None, **kwargs):
        '''allocates an ImageData according to the size expressed in the instance'''
        out = ImageData(geometry=self)
        if isinstance(value, Number):
            if value != 0:
                out += value
        else:
            if value == ImageGeometry.RANDOM:
                seed = kwargs.get('seed', None)
                if seed is not None:
                    numpy.random.seed(seed) 
                out.fill(numpy.random.random_sample(self.shape))
            elif value == ImageGeometry.RANDOM_INT:
                seed = kwargs.get('seed', None)
                if seed is not None:
                    numpy.random.seed(seed)
                max_value = kwargs.get('max_value', 100)
                out.fill(numpy.random.randint(max_value,size=self.shape))
            else:
                raise ValueError('Value {} unknown'.format(value))
        if dimension_labels is not None:
            if dimension_labels != self.dimension_labels:
                return out.subset(dimensions=dimension_labels)
        return out
    # The following methods return 2 members of the class, therefore I 
    # don't think we need to implement them. 
    # Additionally using __len__ is confusing as one would think this is 
    # an iterable. 
    #def __len__(self):
    #    '''returns the length of the geometry'''
    #    return self.length
    #def shape(self):
    #    '''Returns the shape of the array of the ImageData it describes'''
    #    return self.shape

class AcquisitionGeometry(object):
    RANDOM = 'random'
    RANDOM_INT = 'random_int'
    ANGLE_UNIT = 'angle_unit'
    DEGREE = 'degree'
    RADIAN = 'radian'
    CHANNEL = 'channel'
    ANGLE = 'angle'
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'
    def __init__(self, 
                 geom_type, 
                 dimension, 
                 angles, 
                 pixel_num_h=0, 
                 pixel_size_h=1, 
                 pixel_num_v=0, 
                 pixel_size_v=1, 
                 dist_source_center=None, 
                 dist_center_detector=None, 
                 channels=1,
                 **kwargs
                 ):
        """
        General inputs for standard type projection geometries
        detectorDomain or detectorpixelSize:
            If 2D
                If scalar: Width of detector or single detector pixel
                If 2-vec: Error
            If 3D
                If scalar: Width in both dimensions
                If 2-vec: Vertical then horizontal size
        grid
            If 2D
                If scalar: number of detectors
                If 2-vec: error
            If 3D
                If scalar: Square grid that size
                If 2-vec vertical then horizontal size
        cone or parallel
        2D or 3D
        parallel_parameters: ?
        cone_parameters:
            source_to_center_dist (if parallel: NaN)
            center_to_detector_dist (if parallel: NaN)
        standard or nonstandard (vec) geometry
        angles
        angles_format radians or degrees
        """
        self.geom_type = geom_type   # 'parallel' or 'cone'
        self.dimension = dimension # 2D or 3D
        self.angles = angles
        num_of_angles = len (angles)
        
        self.dist_source_center = dist_source_center
        self.dist_center_detector = dist_center_detector
        
        self.pixel_num_h = pixel_num_h
        self.pixel_size_h = pixel_size_h
        self.pixel_num_v = pixel_num_v
        self.pixel_size_v = pixel_size_v
        
        self.channels = channels
        self.angle_unit=kwargs.get(AcquisitionGeometry.ANGLE_UNIT, 
                               AcquisitionGeometry.DEGREE)
        if channels > 1:
            if pixel_num_v > 1:
                shape = (channels, num_of_angles , pixel_num_v, pixel_num_h)
                dim_labels = [AcquisitionGeometry.CHANNEL ,
                 AcquisitionGeometry.ANGLE , AcquisitionGeometry.VERTICAL ,
                 AcquisitionGeometry.HORIZONTAL]
            else:
                shape = (channels , num_of_angles, pixel_num_h)
                dim_labels = [AcquisitionGeometry.CHANNEL ,
                 AcquisitionGeometry.ANGLE, AcquisitionGeometry.HORIZONTAL]
        else:
            if pixel_num_v > 1:
                shape = (num_of_angles, pixel_num_v, pixel_num_h)
                dim_labels = [AcquisitionGeometry.ANGLE , AcquisitionGeometry.VERTICAL ,
                 AcquisitionGeometry.HORIZONTAL]
            else:
                shape = (num_of_angles, pixel_num_h)
                dim_labels = [AcquisitionGeometry.ANGLE, AcquisitionGeometry.HORIZONTAL]
        self.shape = shape

        self.dimension_labels = dim_labels
        
    def clone(self):
        '''returns a copy of the AcquisitionGeometry'''
        return AcquisitionGeometry(self.geom_type,
                                   self.dimension, 
                                   self.angles, 
                                   self.pixel_num_h, 
                                   self.pixel_size_h, 
                                   self.pixel_num_v, 
                                   self.pixel_size_v, 
                                   self.dist_source_center, 
                                   self.dist_center_detector, 
                                   self.channels)
        
    def __str__ (self):
        repres = ""
        repres += "Number of dimensions: {0}\n".format(self.dimension)
        repres += "angles: {0}\n".format(self.angles)
        repres += "voxel_num : h{0},v{1}\n".format(self.pixel_num_h, self.pixel_num_v)
        repres += "voxel size: h{0},v{1}\n".format(self.pixel_size_h, self.pixel_size_v)
        repres += "geometry type: {0}\n".format(self.geom_type)
        repres += "distance source-detector: {0}\n".format(self.dist_source_center)
        repres += "distance center-detector: {0}\n".format(self.dist_source_center)
        repres += "number of channels: {0}\n".format(self.channels)
        return repres
    def allocate(self, value=0, dimension_labels=None):
        '''allocates an AcquisitionData according to the size expressed in the instance'''
        out = AcquisitionData(geometry=self)
        if isinstance(value, Number):
            if value != 0:
                out += value
        else:
            if value == AcquisitionData.RANDOM:
                seed = kwargs.get('seed', None)
                if seed is not None:
                    numpy.random.seed(seed) 
                out.fill(numpy.random.random_sample(self.shape))
            elif value == AcquisitionData.RANDOM_INT:
                seed = kwargs.get('seed', None)
                if seed is not None:
                    numpy.random.seed(seed)
                max_value = kwargs.get('max_value', 100)
                out.fill(numpy.random.randint(max_value,size=self.shape))
            else:
                raise ValueError('Value {} unknown'.format(value))
        if dimension_labels is not None:
            if dimension_labels != self.dimension_labels:
                return out.subset(dimensions=dimension_labels)
        return out
    
class DataContainer(object):
    '''Generic class to hold data
    
    Data is currently held in a numpy arrays'''
    
    __container_priority__ = 1
    def __init__ (self, array, deep_copy=True, dimension_labels=None, 
                  **kwargs):
        '''Holds the data'''
        
        self.shape = numpy.shape(array)
        self.number_of_dimensions = len (self.shape)
        self.dimension_labels = {}
        self.geometry = None # Only relevant for AcquisitionData and ImageData
        
        if dimension_labels is not None and \
           len (dimension_labels) == self.number_of_dimensions:
            for i in range(self.number_of_dimensions):
                self.dimension_labels[i] = dimension_labels[i]
        else:
            for i in range(self.number_of_dimensions):
                self.dimension_labels[i] = 'dimension_{0:02}'.format(i)
        
        if type(array) == numpy.ndarray:
            if deep_copy:
                self.array = array.copy()
            else:
                self.array = array    
        else:
            raise TypeError('Array must be NumpyArray, passed {0}'\
                            .format(type(array)))
        
        # finally copy the geometry
        if 'geometry' in kwargs.keys():
            self.geometry = kwargs['geometry']
        else:
            # assume it is parallel beam
            pass
        
    def get_dimension_size(self, dimension_label):
        if dimension_label in self.dimension_labels.values():
            acq_size = -1
            for k,v in self.dimension_labels.items():
                if v == dimension_label:
                    acq_size = self.shape[k]
            return acq_size
        else:
            raise ValueError('Unknown dimension {0}. Should be one of'.format(dimension_label,
                             self.dimension_labels))
    def get_dimension_axis(self, dimension_label):
        if dimension_label in self.dimension_labels.values():
            for k,v in self.dimension_labels.items():
                if v == dimension_label:
                    return k
        else:
            raise ValueError('Unknown dimension {0}. Should be one of'.format(dimension_label,
                             self.dimension_labels.values()))
                        

    def as_array(self, dimensions=None):
        '''Returns the DataContainer as Numpy Array
        
        Returns the pointer to the array if dimensions is not set.
        If dimensions is set, it first creates a new DataContainer with the subset
        and then it returns the pointer to the array'''
        if dimensions is not None:
            return self.subset(dimensions).as_array()
        return self.array
    
    
    def subset(self, dimensions=None, **kw):
        '''Creates a DataContainer containing a subset of self according to the 
        labels in dimensions'''
        if dimensions is None:
            if kw == {}:
                return self.array.copy()
            else:
                reduced_dims = [v for k,v in self.dimension_labels.items()]
                for dim_l, dim_v in kw.items():
                    for k,v in self.dimension_labels.items():
                        if v == dim_l:
                            reduced_dims.pop(k)
                return self.subset(dimensions=reduced_dims, **kw)
        else:
            # check that all the requested dimensions are in the array
            # this is done by checking the dimension_labels
            proceed = True
            unknown_key = ''
            # axis_order contains the order of the axis that the user wants
            # in the output DataContainer
            axis_order = []
            if type(dimensions) == list:
                for dl in dimensions:
                    if dl not in self.dimension_labels.values():
                        proceed = False
                        unknown_key = dl
                        break
                    else:
                        axis_order.append(find_key(self.dimension_labels, dl))
                if not proceed:
                    raise KeyError('Subset error: Unknown key specified {0}'.format(dl))
                    
                # slice away the unwanted data from the array
                unwanted_dimensions = self.dimension_labels.copy()
                left_dimensions = []
                for ax in sorted(axis_order):
                    this_dimension = unwanted_dimensions.pop(ax)
                    left_dimensions.append(this_dimension)
                #print ("unwanted_dimensions {0}".format(unwanted_dimensions))
                #print ("left_dimensions {0}".format(left_dimensions))
                #new_shape = [self.shape[ax] for ax in axis_order]
                #print ("new_shape {0}".format(new_shape))
                command = "self.array["
                for i in range(self.number_of_dimensions):
                    if self.dimension_labels[i] in unwanted_dimensions.values():
                        value = 0
                        for k,v in kw.items():
                            if k == self.dimension_labels[i]:
                                value = v
                                
                        command = command + str(value)
                    else:
                        command = command + ":"
                    if i < self.number_of_dimensions -1:
                        command = command + ','
                command = command + ']'
                
                cleaned = eval(command)
                # cleaned has collapsed dimensions in the same order of
                # self.array, but we want it in the order stated in the 
                # "dimensions". 
                # create axes order for numpy.transpose
                axes = []
                for key in dimensions:
                    #print ("key {0}".format( key))
                    for i in range(len( left_dimensions )):
                        ld = left_dimensions[i]
                        #print ("ld {0}".format( ld))
                        if ld == key:
                            axes.append(i)
                #print ("axes {0}".format(axes))
                
                cleaned = numpy.transpose(cleaned, axes).copy()
                
                return type(self)(cleaned , True, dimensions)
    
    def fill(self, array, **dimension):
        '''fills the internal numpy array with the one provided'''
        if dimension == {}:
            if issubclass(type(array), DataContainer) or\
               issubclass(type(array), numpy.ndarray):
                if array.shape != self.shape:
                    raise ValueError('Cannot fill with the provided array.' + \
                                     'Expecting {0} got {1}'.format(
                                     self.shape,array.shape))
                if issubclass(type(array), DataContainer):
                    numpy.copyto(self.array, array.array)
                else:
                    #self.array[:] = array
                    numpy.copyto(self.array, array)
        else:
            
            command = 'self.array['
            i = 0
            for k,v in self.dimension_labels.items():
                for dim_label, dim_value in dimension.items():    
                    if dim_label == v:
                        command = command + str(dim_value)
                    else:
                        command = command + ":"
                if i < self.number_of_dimensions -1:
                    command = command + ','
                i += 1
            command = command + "] = array[:]" 
            exec(command)
            
        
    def check_dimensions(self, other):
        return self.shape == other.shape
    
    ## algebra 
    
    def __add__(self, other):
        return self.add(other)
    def __mul__(self, other):
        return self.multiply(other)
    def __sub__(self, other):
        return self.subtract(other)
    def __div__(self, other):
        return self.divide(other)
    def __truediv__(self, other):
        return self.divide(other)
    def __pow__(self, other):
        return self.power(other)
    
    
    
    # reverse operand
    def __radd__(self, other):
        return self + other
    # __radd__
    
    def __rsub__(self, other):
        return (-1 * self) + other
    # __rsub__
    
    def __rmul__(self, other):
        return self * other
    # __rmul__
    
    def __rdiv__(self, other):
        print ("call __rdiv__")
        return pow(self / other, -1)
    # __rdiv__
    def __rtruediv__(self, other):
        return self.__rdiv__(other)
    
    def __rpow__(self, other):
        if isinstance(other, (int, float)) :
            fother = numpy.ones(numpy.shape(self.array)) * other
            return type(self)(fother ** self.array , 
                           dimension_labels=self.dimension_labels,
                           geometry=self.geometry)
        elif issubclass(type(other), DataContainer):
            if self.check_dimensions(other):
                return type(self)(other.as_array() ** self.array , 
                           dimension_labels=self.dimension_labels,
                           geometry=self.geometry)
            else:
                raise ValueError('Dimensions do not match')
    # __rpow__
    
    # in-place arithmetic operators:
    # (+=, -=, *=, /= , //=,
    # must return self
    
    def __iadd__(self, other):
        kw = {'out':self}
        return self.add(other, **kw)
    
    def __imul__(self, other):
        kw = {'out':self}
        return self.multiply(other, **kw)
    
    def __isub__(self, other):
        kw = {'out':self}
        return self.subtract(other, **kw)
    
    def __idiv__(self, other):
        kw = {'out':self}
        return self.divide(other, **kw)
    
    def __itruediv__(self, other):
        kw = {'out':self}
        return self.divide(other, **kw)
    

    
    def __str__ (self, representation=False):
        repres = ""
        repres += "Number of dimensions: {0}\n".format(self.number_of_dimensions)
        repres += "Shape: {0}\n".format(self.shape)
        repres += "Axis labels: {0}\n".format(self.dimension_labels)
        if representation:
            repres += "Representation: \n{0}\n".format(self.array)
        return repres
    
    def clone(self):
        '''returns a copy of itself'''
        
        return type(self)(self.array, 
                          dimension_labels=self.dimension_labels,
                          deep_copy=True,
                          geometry=self.geometry )
    
    def get_data_axes_order(self,new_order=None):
        '''returns the axes label of self as a list
        
        if new_order is None returns the labels of the axes as a sorted-by-key list
        if new_order is a list of length number_of_dimensions, returns a list
        with the indices of the axes in new_order with respect to those in 
        self.dimension_labels: i.e.
          self.dimension_labels = {0:'horizontal',1:'vertical'}
          new_order = ['vertical','horizontal']
          returns [1,0]
        '''
        if new_order is None:
            
            axes_order = [i for i in range(len(self.shape))]
            for k,v in self.dimension_labels.items():
                axes_order[k] = v
            return axes_order
        else:
            if len(new_order) == self.number_of_dimensions:
                axes_order = [i for i in range(self.number_of_dimensions)]
                
                for i in range(len(self.shape)):
                    found = False
                    for k,v in self.dimension_labels.items():
                        if new_order[i] == v:
                            axes_order[i] = k
                            found = True
                    if not found:
                        raise ValueError('Axis label {0} not found.'.format(new_order[i]))
                return axes_order
            else:
                raise ValueError('Expecting {0} axes, got {2}'\
                                 .format(len(self.shape),len(new_order)))
        
                
    def copy(self):
        '''alias of clone'''    
        return self.clone()
    
    ## binary operations
            
    def pixel_wise_binary(self, pwop, x2, *args,  **kwargs):    
        out = kwargs.get('out', None)
        if out is None:
            if isinstance(x2, (int, float, complex)):
                out = pwop(self.as_array() , x2 , *args, **kwargs )
            elif isinstance(x2, (numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.int64,\
                                 numpy.float, numpy.float16, numpy.float32, numpy.float64, \
                                 numpy.complex)):
                out = pwop(self.as_array() , x2 , *args, **kwargs )
            elif issubclass(type(x2) , DataContainer):
                out = pwop(self.as_array() , x2.as_array() , *args, **kwargs )
            return type(self)(out,
                   deep_copy=False, 
                   dimension_labels=self.dimension_labels,
                   geometry=self.geometry)
            
        
        elif issubclass(type(out), DataContainer) and issubclass(type(x2), DataContainer):
            if self.check_dimensions(out) and self.check_dimensions(x2):
                kwargs['out'] = out.as_array()
                pwop(self.as_array(), x2.as_array(), *args, **kwargs )
                #return type(self)(out.as_array(),
                #       deep_copy=False, 
                #       dimension_labels=self.dimension_labels,
                #       geometry=self.geometry)
                return out
            else:
                raise ValueError(message(type(self),"Wrong size for data memory: ", out.shape,self.shape))
        elif issubclass(type(out), DataContainer) and isinstance(x2, (int,float,complex)):
            if self.check_dimensions(out):
                kwargs['out']=out.as_array()
                pwop(self.as_array(), x2, *args, **kwargs )
                return out
            else:
                raise ValueError(message(type(self),"Wrong size for data memory: ", out.shape,self.shape))
        elif issubclass(type(out), numpy.ndarray):
            if self.array.shape == out.shape and self.array.dtype == out.dtype:
                kwargs['out'] = out
                pwop(self.as_array(), x2, *args, **kwargs)
                #return type(self)(out,
                #       deep_copy=False, 
                #       dimension_labels=self.dimension_labels,
                #       geometry=self.geometry)
        else:
            raise ValueError (message(type(self),  "incompatible class:" , pwop.__name__, type(out)))
    
    def add(self, other, *args, **kwargs):
        if hasattr(other, '__container_priority__') and \
           self.__class__.__container_priority__ < other.__class__.__container_priority__:
            return other.add(self, *args, **kwargs)
        return self.pixel_wise_binary(numpy.add, other, *args, **kwargs)
    
    def subtract(self, other, *args, **kwargs):
        if hasattr(other, '__container_priority__') and \
           self.__class__.__container_priority__ < other.__class__.__container_priority__:
            return other.subtract(self, *args, **kwargs)
        return self.pixel_wise_binary(numpy.subtract, other, *args, **kwargs)

    def multiply(self, other, *args, **kwargs):
        if hasattr(other, '__container_priority__') and \
           self.__class__.__container_priority__ < other.__class__.__container_priority__:
            return other.multiply(self, *args, **kwargs)
        return self.pixel_wise_binary(numpy.multiply, other, *args, **kwargs)
    
    def divide(self, other, *args, **kwargs):
        if hasattr(other, '__container_priority__') and \
           self.__class__.__container_priority__ < other.__class__.__container_priority__:
            return other.divide(self, *args, **kwargs)
        return self.pixel_wise_binary(numpy.divide, other, *args, **kwargs)
    
    def power(self, other, *args, **kwargs):
        return self.pixel_wise_binary(numpy.power, other, *args, **kwargs)
    
    def maximum(self, x2, *args, **kwargs):
        return self.pixel_wise_binary(numpy.maximum, x2, *args, **kwargs)
    
    ## unary operations
    def pixel_wise_unary(self, pwop, *args,  **kwargs):
        out = kwargs.get('out', None)
        if out is None:
            out = pwop(self.as_array() , *args, **kwargs )
            return type(self)(out,
                       deep_copy=False, 
                       dimension_labels=self.dimension_labels,
                       geometry=self.geometry)
        elif issubclass(type(out), DataContainer):
            if self.check_dimensions(out):
                kwargs['out'] = out.as_array()
                pwop(self.as_array(), *args, **kwargs )
            else:
                raise ValueError(message(type(self),"Wrong size for data memory: ", out.shape,self.shape))
        elif issubclass(type(out), numpy.ndarray):
            if self.array.shape == out.shape and self.array.dtype == out.dtype:
                kwargs['out'] = out
                pwop(self.as_array(), *args, **kwargs)
        else:
            raise ValueError (message(type(self),  "incompatible class:" , pwop.__name__, type(out)))
    
    def abs(self, *args,  **kwargs):
        return self.pixel_wise_unary(numpy.abs, *args,  **kwargs)
    
    def sign(self, *args,  **kwargs):
        return self.pixel_wise_unary(numpy.sign, *args,  **kwargs)
    
    def sqrt(self, *args,  **kwargs):
        return self.pixel_wise_unary(numpy.sqrt, *args,  **kwargs)

    def conjugate(self, *args,  **kwargs):
        return self.pixel_wise_unary(numpy.conjugate, *args,  **kwargs)
    #def __abs__(self):
    #    operation = FM.OPERATION.ABS
    #    return self.callFieldMath(operation, None, self.mask, self.maskOnValue)
    # __abs__
    
    ## reductions
    def sum(self, *args, **kwargs):
        return self.as_array().sum(*args, **kwargs)
    def squared_norm(self):
        '''return the squared euclidean norm of the DataContainer viewed as a vector'''
        #shape = self.shape
        #size = reduce(lambda x,y:x*y, shape, 1)
        #y = numpy.reshape(self.as_array(), (size, ))
        return self.dot(self.conjugate())
        #return self.dot(self)
    def norm(self):
        '''return the euclidean norm of the DataContainer viewed as a vector'''
        return numpy.sqrt(self.squared_norm())
    def dot(self, other, *args, **kwargs):
        '''return the inner product of 2 DataContainers viewed as vectors'''
        if self.shape == other.shape:
            return numpy.dot(self.as_array().ravel(), other.as_array().ravel())
        else:
            raise ValueError('Shapes are not aligned: {} != {}'.format(self.shape, other.shape))
    
    
    
    
    
class ImageData(DataContainer):
    '''DataContainer for holding 2D or 3D DataContainer'''
    __container_priority__ = 1
    
    
    def __init__(self, 
                 array = None, 
                 deep_copy=False, 
                 dimension_labels=None, 
                 **kwargs):
        
        self.geometry = kwargs.get('geometry', None)
        if array is None:
            if self.geometry is not None:
                shape, dimension_labels = self.get_shape_labels(self.geometry)
                    
                array = numpy.zeros( shape , dtype=numpy.float32) 
                super(ImageData, self).__init__(array, deep_copy,
                                 dimension_labels, **kwargs)
                
            else:
                raise ValueError('Please pass either a DataContainer, ' +\
                                 'a numpy array or a geometry')
        else:
            if self.geometry is not None:
                shape, labels = self.get_shape_labels(self.geometry, dimension_labels)
                if array.shape != shape:
                    raise ValueError('Shape mismatch {} {}'.format(shape, array.shape))
            
            if issubclass(type(array) , DataContainer):
                # if the array is a DataContainer get the info from there
                if not ( array.number_of_dimensions == 2 or \
                         array.number_of_dimensions == 3 or \
                         array.number_of_dimensions == 4):
                    raise ValueError('Number of dimensions are not 2 or 3 or 4: {0}'\
                                     .format(array.number_of_dimensions))
                
                #DataContainer.__init__(self, array.as_array(), deep_copy,
                #                 array.dimension_labels, **kwargs)
                super(ImageData, self).__init__(array.as_array(), deep_copy,
                                 array.dimension_labels, **kwargs)
            elif issubclass(type(array) , numpy.ndarray):
                if not ( array.ndim == 2 or array.ndim == 3 or array.ndim == 4 ):
                    raise ValueError(
                            'Number of dimensions are not 2 or 3 or 4 : {0}'\
                            .format(array.ndim))
                    
                if dimension_labels is None:
                    if array.ndim == 4:
                        dimension_labels = [ImageGeometry.CHANNEL, 
                                            ImageGeometry.VERTICAL,
                                            ImageGeometry.HORIZONTAL_Y,
                                            ImageGeometry.HORIZONTAL_X]
                    elif array.ndim == 3:
                        dimension_labels = [ImageGeometry.VERTICAL,
                                            ImageGeometry.HORIZONTAL_Y,
                                            ImageGeometry.HORIZONTAL_X]
                    else:
                        dimension_labels = [ ImageGeometry.HORIZONTAL_Y,
                                             ImageGeometry.HORIZONTAL_X]   
                
                #DataContainer.__init__(self, array, deep_copy, dimension_labels, **kwargs)
                super(ImageData, self).__init__(array, deep_copy, 
                     dimension_labels, **kwargs)
       
        # load metadata from kwargs if present
        for key, value in kwargs.items():
            if (type(value) == list or type(value) == tuple) and \
                ( len (value) == 3 and len (value) == 2) :
                    if key == 'origin' :    
                        self.origin = value
                    if key == 'spacing' :
                        self.spacing = value
                        
        def subset(self, dimensions=None, **kw):
            # FIXME: this is clearly not rigth
            # it should be something like 
            # out = DataContainer.subset(self, dimensions, **kw)
            # followed by regeneration of the proper geometry. 
            out = super(ImageData, self).subset(dimensions, **kw)
            #out.geometry = self.recalculate_geometry(dimensions , **kw)
            out.geometry = self.geometry
            return out

    def get_shape_labels(self, geometry, dimension_labels=None):
        channels  = geometry.channels
        horiz_x   = geometry.voxel_num_x
        horiz_y   = geometry.voxel_num_y
        vert      = 1 if geometry.voxel_num_z is None\
                      else geometry.voxel_num_z # this should be 1 for 2D
        if dimension_labels is None:
            if channels > 1:
                if vert > 1:
                    shape = (channels, vert, horiz_y, horiz_x)
                    dim_labels = [ImageGeometry.CHANNEL, 
                                  ImageGeometry.VERTICAL,
                                  ImageGeometry.HORIZONTAL_Y,
                                  ImageGeometry.HORIZONTAL_X]
                else:
                    shape = (channels , horiz_y, horiz_x)
                    dim_labels = [ImageGeometry.CHANNEL,
                                  ImageGeometry.HORIZONTAL_Y,
                                  ImageGeometry.HORIZONTAL_X]
            else:
                if vert > 1:
                    shape = (vert, horiz_y, horiz_x)
                    dim_labels = [ImageGeometry.VERTICAL,
                                  ImageGeometry.HORIZONTAL_Y,
                                  ImageGeometry.HORIZONTAL_X]
                else:
                    shape = (horiz_y, horiz_x)
                    dim_labels = [ImageGeometry.HORIZONTAL_Y,
                                  ImageGeometry.HORIZONTAL_X]
            dimension_labels = dim_labels
        else:
            shape = []
            for i in range(len(dimension_labels)):
                dim = dimension_labels[i]
                if dim == ImageGeometry.CHANNEL:
                    shape.append(channels)
                elif dim == ImageGeometry.HORIZONTAL_Y:
                    shape.append(horiz_y)
                elif dim == ImageGeometry.VERTICAL:
                    shape.append(vert)
                elif dim == ImageGeometry.HORIZONTAL_X:
                    shape.append(horiz_x)
            if len(shape) != len(dimension_labels):
                raise ValueError('Missing {0} axes {1} shape {2}'.format(
                        len(dimension_labels) - len(shape), dimension_labels, shape))
            shape = tuple(shape)
            
        return (shape, dimension_labels)
                            

class AcquisitionData(DataContainer):
    '''DataContainer for holding 2D or 3D sinogram'''
    __container_priority__ = 1
    
    
    def __init__(self, 
                 array = None, 
                 deep_copy=True, 
                 dimension_labels=None, 
                 **kwargs):
        self.geometry = kwargs.get('geometry', None)
        if array is None:
            if 'geometry' in kwargs.keys():
                geometry      = kwargs['geometry']
                self.geometry = geometry
                
                shape, dimension_labels = self.get_shape_labels(geometry, dimension_labels)
                
                    
                array = numpy.zeros( shape , dtype=numpy.float32) 
                super(AcquisitionData, self).__init__(array, deep_copy,
                                 dimension_labels, **kwargs)
        else:
            if self.geometry is not None:
                shape, labels = self.get_shape_labels(self.geometry, dimension_labels)
                if array.shape != shape:
                    raise ValueError('Shape mismatch {} {}'.format(shape, array.shape))
                    
            if issubclass(type(array) ,DataContainer):
                # if the array is a DataContainer get the info from there
                if not ( array.number_of_dimensions == 2 or \
                         array.number_of_dimensions == 3 or \
                         array.number_of_dimensions == 4):
                    raise ValueError('Number of dimensions are not 2 or 3 or 4: {0}'\
                                     .format(array.number_of_dimensions))
                
                #DataContainer.__init__(self, array.as_array(), deep_copy,
                #                 array.dimension_labels, **kwargs)
                super(AcquisitionData, self).__init__(array.as_array(), deep_copy,
                                 array.dimension_labels, **kwargs)
            elif issubclass(type(array) ,numpy.ndarray):
                if not ( array.ndim == 2 or array.ndim == 3 or array.ndim == 4 ):
                    raise ValueError(
                            'Number of dimensions are not 2 or 3 or 4 : {0}'\
                            .format(array.ndim))
                    
                if dimension_labels is None:
                    if array.ndim == 4:
                        dimension_labels = [AcquisitionGeometry.CHANNEL,
                                            AcquisitionGeometry.ANGLE,
                                            AcquisitionGeometry.VERTICAL,
                                            AcquisitionGeometry.HORIZONTAL]
                    elif array.ndim == 3:
                        dimension_labels = [AcquisitionGeometry.ANGLE,
                                            AcquisitionGeometry.VERTICAL,
                                            AcquisitionGeometry.HORIZONTAL]
                    else:
                        dimension_labels = [AcquisitionGeometry.ANGLE,
                                            AcquisitionGeometry.HORIZONTAL]

                super(AcquisitionData, self).__init__(array, deep_copy, 
                     dimension_labels, **kwargs)
                
    def get_shape_labels(self, geometry, dimension_labels=None):
        channels      = geometry.channels
        horiz         = geometry.pixel_num_h
        vert          = geometry.pixel_num_v
        angles        = geometry.angles
        num_of_angles = numpy.shape(angles)[0]
        
        if dimension_labels is None:
            if channels > 1:
                if vert > 1:
                    shape = (channels, num_of_angles , vert, horiz)
                    dim_labels = [AcquisitionGeometry.CHANNEL,
                                  AcquisitionGeometry.ANGLE,
                                  AcquisitionGeometry.VERTICAL,
                                  AcquisitionGeometry.HORIZONTAL]
                else:
                    shape = (channels , num_of_angles, horiz)
                    dim_labels = [AcquisitionGeometry.CHANNEL,
                                  AcquisitionGeometry.ANGLE,
                                  AcquisitionGeometry.HORIZONTAL]
            else:
                if vert > 1:
                    shape = (num_of_angles, vert, horiz)
                    dim_labels = [AcquisitionGeometry.ANGLE,
                                  AcquisitionGeometry.VERTICAL,
                                  AcquisitionGeometry.HORIZONTAL
                                  ]
                else:
                    shape = (num_of_angles, horiz)
                    dim_labels = [AcquisitionGeometry.ANGLE,
                                  AcquisitionGeometry.HORIZONTAL
                                  ]
            
            dimension_labels = dim_labels
        else:
            shape = []
            for i in range(len(dimension_labels)):
                dim = dimension_labels[i]
                
                if dim == AcquisitionGeometry.CHANNEL:
                    shape.append(channels)
                elif dim == AcquisitionGeometry.ANGLE:
                    shape.append(num_of_angles)
                elif dim == AcquisitionGeometry.VERTICAL:
                    shape.append(vert)
                elif dim == AcquisitionGeometry.HORIZONTAL:
                    shape.append(horiz)
            if len(shape) != len(dimension_labels):
                raise ValueError('Missing {0} axes.\nExpected{1} got {2}'\
                    .format(
                        len(dimension_labels) - len(shape),
                        dimension_labels, shape) 
                    )
            shape = tuple(shape)
        return (shape, dimension_labels)
    
                
            
class DataProcessor(object):
    
    '''Defines a generic DataContainer processor
    
    accepts DataContainer as inputs and 
    outputs DataContainer
    additional attributes can be defined with __setattr__
    '''
    
    def __init__(self, **attributes):
        if not 'store_output' in attributes.keys():
            attributes['store_output'] = True
            attributes['output'] = False
            attributes['runTime'] = -1
            attributes['mTime'] = datetime.now()
            attributes['input'] = None
        for key, value in attributes.items():
            self.__dict__[key] = value
        
    
    def __setattr__(self, name, value):
        if name == 'input':
            self.set_input(value)
        elif name in self.__dict__.keys():
            self.__dict__[name] = value
            self.__dict__['mTime'] = datetime.now()
        else:
            raise KeyError('Attribute {0} not found'.format(name))
        #pass
    
    def set_input(self, dataset):
        if issubclass(type(dataset), DataContainer):
            if self.check_input(dataset):
                self.__dict__['input'] = dataset
        else:
            raise TypeError("Input type mismatch: got {0} expecting {1}"\
                            .format(type(dataset), DataContainer))
    
    def check_input(self, dataset):
        '''Checks parameters of the input DataContainer
        
        Should raise an Error if the DataContainer does not match expectation, e.g.
        if the expected input DataContainer is 3D and the Processor expects 2D.
        '''
        raise NotImplementedError('Implement basic checks for input DataContainer')
        
    def get_output(self, out=None):
        
        for k,v in self.__dict__.items():
            if v is None and k != 'output':
                raise ValueError('Key {0} is None'.format(k))
        shouldRun = False
        if self.runTime == -1:
            shouldRun = True
        elif self.mTime > self.runTime:
            shouldRun = True
            
        # CHECK this
        if self.store_output and shouldRun:
            self.runTime = datetime.now()
            try:
                self.output = self.process(out=out)
                return self.output
            except TypeError as te:
                self.output = self.process()
                return self.output
        self.runTime = datetime.now()
        try:
            return self.process(out=out)
        except TypeError as te:
            return self.process()
            
    
    def set_input_processor(self, processor):
        if issubclass(type(processor), DataProcessor):
            self.__dict__['input'] = processor
        else:
            raise TypeError("Input type mismatch: got {0} expecting {1}"\
                            .format(type(processor), DataProcessor))
        
    def get_input(self):
        '''returns the input DataContainer
        
        It is useful in the case the user has provided a DataProcessor as
        input
        '''
        if issubclass(type(self.input), DataProcessor):
            dsi = self.input.get_output()
        else:
            dsi = self.input
        return dsi
        
    def process(self, out=None):
        raise NotImplementedError('process must be implemented')
        
    
    

class DataProcessor23D(DataProcessor):
    '''Regularizers DataProcessor
    '''
            
    def check_input(self, dataset):
        '''Checks number of dimensions input DataContainer
        
        Expected input is 2D or 3D
        '''
        if dataset.number_of_dimensions == 2 or \
           dataset.number_of_dimensions == 3:
               return True
        else:
            raise ValueError("Expected input dimensions is 2 or 3, got {0}"\
                             .format(dataset.number_of_dimensions))
    
###### Example of DataProcessors

class AX(DataProcessor):
    '''Example DataProcessor
    The AXPY routines perform a vector multiplication operation defined as

    y := a*x
    where:

    a is a scalar

    x a DataContainer.
    '''
    
    def __init__(self):
        kwargs = {'scalar':None, 
                  'input':None, 
                  }
        
        #DataProcessor.__init__(self, **kwargs)
        super(AX, self).__init__(**kwargs)
    
    def check_input(self, dataset):
        return True
        
    def process(self, out=None):
        
        dsi = self.get_input()
        a = self.scalar
        if out is None:
            y = DataContainer( a * dsi.as_array() , True, 
                        dimension_labels=dsi.dimension_labels )
            #self.setParameter(output_dataset=y)
            return y
        else:
            out.fill(a * dsi.as_array())
    

###### Example of DataProcessors

class CastDataContainer(DataProcessor):
    '''Example DataProcessor
    Cast a DataContainer array to a different type.

    y := a*x
    where:

    a is a scalar

    x a DataContainer.
    '''
    
    def __init__(self, dtype=None):
        kwargs = {'dtype':dtype, 
                  'input':None, 
                  }
        
        #DataProcessor.__init__(self, **kwargs)
        super(CastDataContainer, self).__init__(**kwargs)
    
    def check_input(self, dataset):
        return True
        
    def process(self, out=None):
        
        dsi = self.get_input()
        dtype = self.dtype
        if out is None:
            y = numpy.asarray(dsi.as_array(), dtype=dtype)
            
            return type(dsi)(numpy.asarray(dsi.as_array(), dtype=dtype),
                                dimension_labels=dsi.dimension_labels )
        else:
            out.fill(numpy.asarray(dsi.as_array(), dtype=dtype))
    
        
        
    
    
class PixelByPixelDataProcessor(DataProcessor):
    '''Example DataProcessor
    
    This processor applies a python function to each pixel of the DataContainer
    
    f is a python function

    x a DataSet.
    '''
    
    def __init__(self):
        kwargs = {'pyfunc':None, 
                  'input':None, 
                  }
        #DataProcessor.__init__(self, **kwargs)
        super(PixelByPixelDataProcessor, self).__init__(**kwargs)
        
    def check_input(self, dataset):
        return True
    
    def process(self, out=None):
        
        pyfunc = self.pyfunc
        dsi = self.get_input()
        
        eval_func = numpy.frompyfunc(pyfunc,1,1)

        
        y = DataContainer( eval_func( dsi.as_array() ) , True, 
                    dimension_labels=dsi.dimension_labels )
        return y
    

        
        
if __name__ == '__main__':
    shape = (2,3,4,5)
    size = shape[0]
    for i in range(1, len(shape)):
        size = size * shape[i]
    #print("a refcount " , sys.getrefcount(a))
    a = numpy.asarray([i for i in range( size )])
    print("a refcount " , sys.getrefcount(a))
    a = numpy.reshape(a, shape)
    print("a refcount " , sys.getrefcount(a))
    ds = DataContainer(a, False, ['X', 'Y','Z' ,'W'])
    print("a refcount " , sys.getrefcount(a))
    print ("ds label {0}".format(ds.dimension_labels))
    subset = ['W' ,'X']
    b = ds.subset( subset )
    print("a refcount " , sys.getrefcount(a))
    print ("b label {0} shape {1}".format(b.dimension_labels, 
           numpy.shape(b.as_array())))
    c = ds.subset(['Z','W','X'])
    print("a refcount " , sys.getrefcount(a))
    
    # Create a ImageData sharing the array with c
    volume0 = ImageData(c.as_array(), False, dimensions = c.dimension_labels)
    volume1 = ImageData(c, False)
    
    print ("volume0 {0} volume1 {1}".format(id(volume0.array),
           id(volume1.array)))
    
    # Create a ImageData copying the array from c
    volume2 = ImageData(c.as_array(), dimensions = c.dimension_labels)
    volume3 = ImageData(c)
    
    print ("volume2 {0} volume3 {1}".format(id(volume2.array),
           id(volume3.array)))
        
    # single number DataSet
    sn = DataContainer(numpy.asarray([1]))
    
    ax = AX()
    ax.scalar = 2
    ax.set_input(c)
    #ax.apply()
    print ("ax  in {0} out {1}".format(c.as_array().flatten(),
           ax.get_output().as_array().flatten()))
    
    cast = CastDataContainer(dtype=numpy.float32)
    cast.set_input(c)
    out = cast.get_output()
    out *= 0 
    axm = AX()
    axm.scalar = 0.5
    axm.set_input_processor(cast)
    axm.get_output(out)
    #axm.apply()
    print ("axm in {0} out {1}".format(c.as_array(), axm.get_output().as_array()))
    
    # check out in DataSetProcessor
   #a = numpy.asarray([i for i in range( size )])
    
        
    # create a PixelByPixelDataProcessor
    
    #define a python function which will take only one input (the pixel value)
    pyfunc = lambda x: -x if x > 20 else x
    clip = PixelByPixelDataProcessor()
    clip.pyfunc = pyfunc 
    clip.set_input(c)    
    #clip.apply()
    
    print ("clip in {0} out {1}".format(c.as_array(), clip.get_output().as_array()))
    
    #dsp = DataProcessor()
    #dsp.set_input(ds)
    #dsp.input = a
    # pipeline

    chain = AX()
    chain.scalar = 0.5
    chain.set_input_processor(ax)
    print ("chain in {0} out {1}".format(ax.get_output().as_array(), chain.get_output().as_array()))
    
    # testing arithmetic operations
    
    print (b)
    print ((b+1))
    print ((1+b))
    
    print (b)
    print ((b*2))
    
    print (b)
    print ((2*b))
    
    print (b)
    print ((b/2))
    
    print (b)
    print ((2/b))
    
    print (b)
    print ((b**2))
    
    print (b)
    print ((2**b))
    
    print (type(volume3 + 2))
    
    s = [i for i in range(3 * 4 * 4)]
    s = numpy.reshape(numpy.asarray(s), (3,4,4))
    sino = AcquisitionData( s )
    
    shape = (4,3,2)
    a = [i for i in range(2*3*4)]
    a = numpy.asarray(a)
    a = numpy.reshape(a, shape)
    print (numpy.shape(a))
    ds = DataContainer(a, True, ['X', 'Y','Z'])
    # this means that I expect the X to be of length 2 ,
    # y of length 3 and z of length 4
    subset = ['Y' ,'Z']
    b0 = ds.subset( subset )
    print ("shape b 3,2? {0}".format(numpy.shape(b0.as_array())))
    # expectation on b is that it is 
    # 3x2 cut at z = 0
    
    subset = ['X' ,'Y']
    b1 = ds.subset( subset , Z=1)
    print ("shape b 2,3? {0}".format(numpy.shape(b1.as_array())))
    
    

    # create VolumeData from geometry
    vgeometry = ImageGeometry(voxel_num_x=2, voxel_num_y=3, channels=2)
    vol = ImageData(geometry=vgeometry)
    
    sgeometry = AcquisitionGeometry(dimension=2, angles=numpy.linspace(0, 180, num=20), 
                                       geom_type='parallel', pixel_num_v=3,
                                       pixel_num_h=5 , channels=2)
    sino = AcquisitionData(geometry=sgeometry)
    sino2 = sino.clone()
    
    a0 = numpy.asarray([i for i in range(2*3*4)])
    a1 = numpy.asarray([2*i for i in range(2*3*4)])
    
            
    ds0 = DataContainer(numpy.reshape(a0,(2,3,4)))
    ds1 = DataContainer(numpy.reshape(a1,(2,3,4)))
    
    numpy.testing.assert_equal(ds0.dot(ds1), a0.dot(a1))
    
    a2 = numpy.asarray([2*i for i in range(2*3*5)])
    ds2 = DataContainer(numpy.reshape(a2,(2,3,5)))
    
#    # it should fail if the shape is wrong
#    try:
#        ds2.dot(ds0)
#        self.assertTrue(False)
#    except ValueError as ve:
#        self.assertTrue(True)
    
