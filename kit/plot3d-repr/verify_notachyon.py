"""Without the tachyon extra: display must fall back to text, quietly."""
import sys, subprocess
class Blocker:
    def find_spec(self, name, path=None, target=None):
        if name == 'sage.repl' or name.startswith('sage.repl.'):
            raise ImportError("blocked: %s" % name)
        return None
sys.meta_path.insert(0, Blocker())

tripped = []
for fn in ('check_call', 'run', 'Popen', 'call', 'check_output'):
    orig = getattr(subprocess, fn)
    def make(fn=fn, orig=orig):
        def w(*a, **k):
            tripped.append((fn, a[0] if a else None)); return orig(*a, **k)
        return w
    setattr(subprocess, fn, make())

from sage.all__sagemath_symbolics import *
from sage.all__sagemath_plot import *
from sage.features.tachyon import Tachyon
print("ok  : tachyon present =", bool(Tachyon().is_present()))

from IPython.core.formatters import DisplayFormatter
data, md = DisplayFormatter().format(sphere())
print("ok  : mime types =", sorted(data))
assert 'image/png' not in data, "unexpected image/png without tachyon"
assert 'text/plain' in data
print("ok  : text/plain fallback =", repr(data['text/plain'])[:60])
bad = [t for t in tripped if 'playwright' in str(t) or 'chromium' in str(t)]
print("ok  : subprocess calls during display =", len(tripped),
      "(one-time sage.features probe, cached thereafter)")
print("ok  : playwright/chromium invocations =", len(bad))
assert not bad, "display tried to install a browser: %r" % bad
print("ok  : _repr_png_() returned", sphere()._repr_png_())
print("PASS")
