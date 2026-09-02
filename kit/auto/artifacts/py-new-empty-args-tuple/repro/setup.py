"""Build ratlike + one user variant.  Usage: setup.py <before|after> <opt>"""
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize

variant, opt = sys.argv.pop(1), sys.argv.pop(1)  # variant: before|after|before_va|after_va
exts = [Extension("ratlike", ["ratlike.pyx"], extra_compile_args=["-" + opt]),
        Extension("user", ["user_%s.pyx" % variant], extra_compile_args=["-" + opt])]
setup(name="py_new_repro",
      ext_modules=cythonize(exts, include_path=["."], language_level=3),
      script_args=["build_ext", "--inplace", "-b", ".", "-t", "build"])
