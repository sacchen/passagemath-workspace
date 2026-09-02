"""Negative control for eval_grid()'s ulist/vlist leak.

`sage -t` cannot run this file's doctests in a modular plot venv: the
file-level `# sage.doctest: needs sage.symbolic` tag skips every test when
sage.symbolic is absent, so the scripted negative control has no signal to
read. This script runs the body of the new doctest directly instead, against
whichever sage.plot.plot3d.parametric_surface is importable.

    python repro.py          -> exit 1 on unpatched code, exit 0 on patched

Point it at a patched build without installing one by prepending a directory
holding the rebuilt extension to PYTHONPATH, or by importing it first.
"""
import gc
import resource
import sys

from sage.plot.plot3d.parametric_surface import ParametricSurface

THRESHOLD = 4_000_000
GRID = (range(100_000), [0.0, 1.0])


class FailingSurface(ParametricSurface):
    def eval(self, u, v):
        raise ValueError("stop")


def growth(surface):
    """Return the RSS high-water growth over 50 failed triangulations."""
    def fail():
        try:
            surface.triangulate()
        except ValueError:
            pass

    fail()  # warm up allocations
    fail()
    gc.collect()
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    for _ in range(50):
        fail()
    gc.collect()
    after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    scale = 1 if sys.platform == 'darwin' else 1024
    return (after - before) * scale


def main():
    import sage.plot.plot3d.parametric_surface as mod
    print("module: %s" % mod.__file__)

    from sage.ext.fast_callable import ExpressionTreeBuilder, fast_callable
    etb = ExpressionTreeBuilder(vars=('u', 'v'))
    u, v = etb.var('u'), etb.var('v')
    fast = fast_callable(u + v, domain=float)

    def failing_function(u, v):
        raise ValueError("stop")

    cases = [
        ("subclass", FailingSurface(None, GRID)),
        ("tuple", ParametricSurface((fast, fast, failing_function), GRID)),
    ]
    leaked = False
    for name, surface in cases:
        g = growth(surface)
        verdict = "LEAK" if g >= THRESHOLD else "ok"
        print("%-9s growth=%9d  threshold=%d  %s" % (name, g, THRESHOLD, verdict))
        leaked = leaked or g >= THRESHOLD
    return 1 if leaked else 0


if __name__ == '__main__':
    sys.exit(main())
