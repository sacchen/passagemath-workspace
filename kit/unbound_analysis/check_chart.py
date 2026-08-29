import ast
from pathlib import Path

file_path = Path('~/foundry/sandbox/passagemath/passagemath/src/sage/manifolds/chart_func.py').expanduser()
with open(file_path, 'r') as f:
    content = f.read()

tree = ast.parse(content)

for node in ast.walk(tree):
    if isinstance(node, ast.Try):
        has_import_error = False
        for handler in node.handlers:
            if getattr(handler.type, 'id', None) == 'ImportError':
                has_import_error = True
        
        if has_import_error:
            imports = []
            for stmt in node.body:
                if isinstance(stmt, ast.ImportFrom):
                    imports.extend([a.name for a in stmt.names])
                elif isinstance(stmt, ast.Import):
                    imports.extend([a.name for a in stmt.names])
            if 'sympy' in imports:
                print(f"Found at line {node.lineno}:")
                print(ast.unparse(node))
                print("-" * 40)
