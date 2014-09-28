# Author: Ryan P. Adams <rpa@seas.harvard.edu>
# Copyright 2014, The President and Fellows of Harvard University

import numpy as np

from .        import Differentiable
from util     import broadcast

class MatMult(Differentiable):

    def __init__(self, A, B, *args):
        # Recurse to handle lists of arguments.
        if len(args) > 0:
            B = MatMult(B, *args)

        super(MatMult, self).__init__([A, B])

        if A.shape[1] != B.shape[0]:
            raise Exception("Cannot multiply %s by %s matrices." % (A.shape, B.shape))
        if len(A.shape) != 2 or len(B.shape) != 2:
            raise Exception("Inputs of shape %s and %s are not matrices" % (A.shape, B.shape))
        self.A = A
        self.B = B

    def _compute_value(self):
        return np.dot(self.A.value, self.B.value)

    def _local_grad(self, parent, d_out_d_self):
        if parent == 0:
            return np.dot(d_out_d_self, self.B.value.T)
        elif parent == 1:
            return np.dot(self.A.value.T, d_out_d_self)
        else:
            raise Exception("Not a parent of me")

class MatSum(Differentiable):
     
    def __init__(self, A, axis=None):
        super(MatSum, self).__init__([A])
        if axis is not None and type(axis) != int:
            raise Exception("Can only sum over one axis at a time.")
        self.A    = A
        self.axis = axis

    def _compute_value(self):
        return np.sum(self.A.value, axis=self.axis, keepdims=True)

    def _local_grad(self, parent, d_out_d_self):
        return d_out_d_self * np.ones(self.A.shape)

class MatAdd(Differentiable):

    def __init__(self, A, B, *args):
        # Recurse to handle lists of arguments.
        if len(args) > 0:
            B = MatAdd(B, *args)
        super(MatAdd, self).__init__([A,B])
        if broadcast(A.shape, B.shape) is None:
            raise Exception("Matrices are not broadcastable: %s vs %s" % (A.shape, B.shape))
        self.A = A
        self.B = B

    def _compute_value(self):
        return self.A.value + self.B.value

    def _local_grad(self, parent, d_out_d_self):
        parent_shape = self._parents[parent].shape
        sum_axes = tuple(np.where(np.array(parent_shape) == 1)[0])
        return np.sum(d_out_d_self, axis=sum_axes, keepdims=True)

class MatDet(Differentiable):
    pass

class MatLogDet(Differentiable):
    pass

class MatTrace(Differentiable):
    pass

class Transpose(Differentiable):

    def __init__(self, A, axes=None):
        super(Transpose, self).__init__([A])
        self.A    = A
        self.axes = axes

    def _compute_value(self):
        return np.transpose(self.A.value, axes=self.axes)

    def _local_grad(self, parent, d_out_d_self):
        if self.axes is None:
            return np.transpose(d_out_d_self)
        else:
            return np.transpose(d_out_d_self, axes=np.argsort(self.axes))

class Reshape(Differentiable):

    def __init__(self, A, new_shape):
        super(Reshape, self).__init__([A])
        self.A         = A
        self.new_shape = new_shape

    def _compute_value(self):
        return np.reshape(self.A.value, self.new_shape)

    def _local_grad(self, parent, d_out_d_self):
        return np.reshape(d_out_d_self, self.A.shape)

class Concatenate(Differentiable):

    def __init__(self, axis, A, B, *args):
        # Recurse to handle lists of arguments.
        if len(args) > 0:
            B = Concatenate(axis, B, *args)
        super(Concatenate, self).__init__([A, B])
        self.A = A
        self.B = B
        self.axis = axis

    def _compute_value(self):
        return np.concatenate((self.A.value,
                               self.B.value), axis=self.axis)

    def _local_grad(self, parent, d_out_d_self):
        local_grad_both = np.split(d_out_d_self, [self.A.shape[self.axis]], axis=self.axis)
        return local_grad_both[parent]

class TensorMult(Differentiable):
    pass
       
