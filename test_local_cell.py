import sys
import os

_pm_explore_src_root = os.path.abspath('/home/dev/sandbox/passagemath/src')
_pm_explore_module = 'sage.graphs.generators.chessboard'
_pm_explore_root_package = 'sage'

if _pm_explore_root_package == 'sage':
    exec('from sage.all import *', globals())
    for key in list(sys.modules):
        if key == _pm_explore_module or key.startswith(_pm_explore_module + '.'):
            del sys.modules[key]

_pm_explore_modules_before = {
    name: module
    for name, module in sys.modules.items()
    if name == _pm_explore_root_package or name.startswith(_pm_explore_root_package + '.')
}

sys.path.insert(0, _pm_explore_src_root)
try:
    exec(f'from {_pm_explore_module} import *', globals())
    print(f'Imported {_pm_explore_module} from local checkout: {_pm_explore_src_root}')
    print("Partitions in globals?", 'Partitions' in globals())
except Exception as exc:
    if sys.path and sys.path[0] == _pm_explore_src_root:
        sys.path.pop(0)
    for name in list(sys.modules):
        if name != _pm_explore_root_package and not name.startswith(_pm_explore_root_package + '.'):
            continue
        previous = _pm_explore_modules_before.get(name)
        current = sys.modules.get(name)
        if previous is None or current is not previous:
            sys.modules.pop(name, None)
    print(
        f'Local checkout import failed for {_pm_explore_module} '
        f'({exc.__class__.__name__}: {exc}). Falling back to installed package.'
    )
    try:
        if _pm_explore_root_package == 'sage':
            exec('from sage.all import *', globals())
        exec(f'from {_pm_explore_module} import *', globals())
    except Exception as fallback_exc:
        raise RuntimeError("failed")
