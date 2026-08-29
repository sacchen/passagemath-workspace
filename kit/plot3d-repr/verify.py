"""Verify the change in the environment the doctest runner cannot reach:
plain IPython DisplayFormatter, with sage.repl blocked."""
import sys, subprocess, builtins

# --- Block sage.repl entirely (simulates passagemath-plot without passagemath-repl)
class Blocker:
    def find_spec(self, name, path=None, target=None):
        if name == 'sage.repl' or name.startswith('sage.repl.'):
            raise ImportError("blocked: %s" % name)
        return None
sys.meta_path.insert(0, Blocker())

# --- Trip-wire on subprocess: display must never shell out
tripped = []
for fn in ('check_call', 'run', 'Popen', 'call', 'check_output'):
    orig = getattr(subprocess, fn)
    def make(fn=fn, orig=orig):
        def wrapper(*a, **k):
            tripped.append((fn, a[0] if a else None))
            return orig(*a, **k)
        return wrapper
    setattr(subprocess, fn, make())

from sage.all__sagemath_symbolics import *
from sage.all__sagemath_plot import *

try:
    import sage.repl
    print("FAIL: sage.repl importable, blocker did not work")
except ImportError:
    print("ok  : sage.repl is blocked")

from IPython.core.formatters import DisplayFormatter
fmt = DisplayFormatter()
data, md = fmt.format(sphere())
print("ok  : mime types =", sorted(data))
assert 'image/png' in data, "no image/png"
png = data['image/png']
if isinstance(png, str):
    import base64; png = base64.b64decode(png)
assert png[:8] == b'\x89PNG\r\n\x1a\n', "not a PNG"
print("ok  : image/png is %d bytes, valid PNG magic" % len(png))
assert 'text/html' not in data, "unexpected text/html"
print("ok  : no text/html (no Three.js payload duplicated into the notebook)")

# tachyon renders via the tachyon executable, so one subprocess is expected;
# what must NOT appear is a playwright/browser install.
bad = [t for t in tripped if 'playwright' in str(t)]
print("ok  : subprocess calls =", len(tripped), "| playwright invocations =", len(bad))
assert not bad, "playwright was invoked from a display hook: %r" % bad
print("PASS")
