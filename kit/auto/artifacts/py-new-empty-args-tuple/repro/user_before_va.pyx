# Same, but constructing the __cinit__(self, *args) shape, where the size the
# adapter reads is live rather than dead.

from cpython.object cimport PyTypeObject, PyObject
from ratlike cimport Helper2

cdef inline PY_NEW(type t):
    return (<PyTypeObject*>t).tp_new(t, <PyObject*>NULL, <PyObject*>NULL)

cdef Helper2 rat_temp = PY_NEW(Helper2)

def check():
    return rat_temp.b
