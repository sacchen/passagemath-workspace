import ast
from pathlib import Path

test_file = Path('~/foundry/sandbox/passagemath/src/sage/schemes/elliptic_curves/ell_point.py').expanduser()

try:
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ast.parse(content, filename=str(test_file))
except Exception as e:
    print("Error parsing:", e)
    import sys; sys.exit(1)

for node in ast.walk(tree):
    if isinstance(node, ast.Try):
        print(f"Found try at line {node.lineno}")
        for handler in node.handlers:
            if handler.type:
                if isinstance(handler.type, ast.Name):
                    print(f"  Catching: {handler.type.id}")
                else:
                    print(f"  Catching: {ast.dump(handler.type)}")
            else:
                print("  Bare except")
