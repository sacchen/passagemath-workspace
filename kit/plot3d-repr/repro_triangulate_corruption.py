"""Repro for triangulate() corruption in parametric_surface.pyx.

An exception raised inside the face-construction loop (KeyboardInterrupt from
sig_check(), or an error from a user color_function) leaves the surface with
fcount = m*n but uninitialized face.vertices pointers.  The retry then
short-circuits on `render_grid == (urange, vrange) and fcount` and hands the
half-built mesh to the renderer.

Modes (argv[1]):
  interrupt-then-facelist  KeyboardInterrupt mid-loop, then face_list()
                           -> expect IndexError (soft symptom)
  interrupt-then-render    KeyboardInterrupt mid-loop, then re-render
                           -> expect hard crash (SIGBUS/SIGSEGV) in
                              _separate_creases; run me in a subprocess
  colorfn-then-render      ValueError from color_function, retry, re-render
                           -> expect hard crash
  shortcircuit-check       show that attempt 2 returns without raising
"""
import sys

from sage.all__sagemath_plot import *
from sage.plot.plot3d.parametric_surface import ParametricSurface


def make_surface(boom_exc, boom_at=200, persistent=False):
    """Surface whose color_function raises boom_exc on call #boom_at
    (every call from #boom_at on, if persistent).

    The color_function runs inside the face-construction loop, a few
    statements after that iteration's sig_check(); raising
    KeyboardInterrupt from it produces the same class of corruption as a
    real Ctrl-C (fcount set, face data incompletely initialized).
    """
    calls = {'n': 0}

    def c(x, y):
        calls['n'] += 1
        if calls['n'] == boom_at or (persistent and calls['n'] > boom_at):
            raise boom_exc('injected at face %d' % calls['n'])
        return 0.5

    def f(x, y):
        return x, y, x * y

    cm = colormaps.gist_rainbow
    dom = (srange(0, 5, 0.1), srange(0, 5, 0.1))   # 50x50 = 2500 faces
    return ParametricSurface(f, dom, color=(c, cm))


def first_attempt(P, exc_type):
    try:
        P.triangulate()
    except exc_type as e:
        print('attempt 1: raised %s: %s' % (type(e).__name__, e), flush=True)
        return
    print('attempt 1: did NOT raise (repro broken)', flush=True)
    sys.exit(2)


mode = sys.argv[1]

if mode == 'shortcircuit-check':
    # color_function fails persistently, so an honest recompute must
    # raise again; returning without raising proves the short-circuit.
    P = make_surface(ValueError, persistent=True)
    first_attempt(P, ValueError)
    try:
        P.triangulate()
        print('attempt 2: triangulate() returned WITHOUT raising  <-- short-circuit', flush=True)
    except ValueError as e:
        print('attempt 2: raised again (%s) -- honest recompute, no short-circuit' % e, flush=True)

elif mode == 'interrupt-then-facelist':
    P = make_surface(KeyboardInterrupt)
    first_attempt(P, KeyboardInterrupt)
    try:
        faces = P.face_list()
        print('face_list: returned %d faces (no error)' % len(faces), flush=True)
    except IndexError as e:
        print('face_list: IndexError: %s  <-- corruption visible' % e, flush=True)

elif mode == 'interrupt-then-render':
    P = make_surface(KeyboardInterrupt)
    first_attempt(P, KeyboardInterrupt)
    print('user now re-renders the same object ...', flush=True)
    P.save(sys.argv[2] if len(sys.argv) > 2 else '/tmp/out.png')
    print('render: completed without crash', flush=True)

elif mode == 'colorfn-then-render':
    P = make_surface(ValueError)
    first_attempt(P, ValueError)
    print('user now re-renders the same object ...', flush=True)
    P.save(sys.argv[2] if len(sys.argv) > 2 else '/tmp/out.png')
    print('render: completed without crash', flush=True)

else:
    sys.exit('unknown mode %r' % mode)
