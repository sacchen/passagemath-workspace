# Stands in for common_conversion.pyx: PY_NEW at module level, so the call
# runs at import.  PY_NEW is inlined here rather than cimported so the repro
# needs no sage tree; the generated call site is the same either way.

from cpython.object cimport PyTypeObject, PyObject
from ratlike cimport Ratlike

cdef inline PY_NEW(type t):
    return (<PyTypeObject*>t).tp_new(t, <PyObject*>(), <PyObject*>NULL)

cdef Ratlike rat_temp = PY_NEW(Ratlike)

def check():
    return rat_temp.num
