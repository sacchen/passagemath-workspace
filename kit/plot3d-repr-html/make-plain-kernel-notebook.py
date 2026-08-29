import json, nbformat
from nbformat.v4 import new_notebook, new_code_cell
nb = new_notebook(cells=[
    new_code_cell("import sys, IPython\n"
                  "fmt = get_ipython().display_formatter\n"
                  "assert type(fmt).__name__ == 'DisplayFormatter', 'not a plain kernel'\n"
                  "print('kernel formatter:', type(fmt).__module__ + '.' + type(fmt).__name__)"),
    new_code_cell("from sage.all__sagemath_symbolics import *\n"
                  "from sage.all__sagemath_plot import *\n"
                  "x, y, z = var('x y z')\n"
                  "implicit_plot3d(cos(x)*sin(y) + cos(y)*sin(z) + cos(z)*sin(x) == 0,\n"
                  "                (x, -2*pi, 2*pi), (y, -2*pi, 2*pi), (z, -2*pi, 2*pi),\n"
                  "                plot_points=40,\n"
                  "                color=(lambda a,b,c: (sin(a)+1)/2, colormaps.viridis))"),
])
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
nbformat.write(nb, 'plainkernel.ipynb')
