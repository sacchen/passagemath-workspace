import sys
import sage.all
import importlib

# Clean up sys.modules for partition
for key in list(sys.modules):
    if key == 'sage.combinat.partition' or key.startswith('sage.combinat.partition.'):
        del sys.modules[key]

sys.path.insert(0, '/home/dev/sandbox/passagemath/src')

try:
    import sage.combinat.partition
    print("SUCCESS")
    print(sage.combinat.partition.__file__)
except Exception as e:
    print("FAILED", type(e), e)
