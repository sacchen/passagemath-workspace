# Stands in for rational.pyx: several cdef classes in one module, the one we
# construct having a no-argument __cinit__ like Rational's.

cdef class Ratlike:
    def __cinit__(self):
        self.num = 3

cdef class Helper1:
    def __cinit__(self):
        self.a = 1

cdef class Helper2:
    def __cinit__(self, *args):
        self.b = 2
