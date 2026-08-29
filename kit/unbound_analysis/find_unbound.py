import ast
from pathlib import Path

def is_control_flow_terminator(node):
    """Check if a node guarantees we leave the current execution flow."""
    return isinstance(node, (ast.Return, ast.Raise, ast.Continue, ast.Break))

def has_terminator(body):
    """Check if a block of statements contains an unconditional terminator at the top level."""
    for stmt in body:
        if is_control_flow_terminator(stmt):
            return True
        # For now, we won't do deep CFG analysis. Just checking top-level of except block.
    return False

def find_unbound_imports(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=str(filepath))
    except Exception as e:
        return None

    results = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            has_import_error_handler = False
            terminates = False
            for handler in node.handlers:
                # Check for `except ImportError:` or `except (..., ImportError, ...):`
                if handler.type:
                    if isinstance(handler.type, ast.Name) and handler.type.id == 'ImportError':
                        has_import_error_handler = True
                        if has_terminator(handler.body): terminates = True
                    elif isinstance(handler.type, ast.Tuple):
                        for elt in handler.type.elts:
                            if isinstance(elt, ast.Name) and elt.id == 'ImportError':
                                has_import_error_handler = True
                                if has_terminator(handler.body): terminates = True
                else:
                    # Bare except
                    has_import_error_handler = True
                    if has_terminator(handler.body): terminates = True
            
            if has_import_error_handler and not terminates:
                imported_names = set()
                # find imports in try block
                for stmt in node.body:
                    for subnode in ast.walk(stmt):
                        if isinstance(subnode, ast.Import):
                            for alias in subnode.names:
                                imported_names.add(alias.asname or alias.name.split('.')[0])
                        elif isinstance(subnode, ast.ImportFrom):
                            for alias in subnode.names:
                                imported_names.add(alias.asname or alias.name)
                            
                # find assigned names in except block
                assigned_names = set()
                for handler in node.handlers:
                    for stmt in ast.walk(handler):
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Name):
                                    assigned_names.add(target.id)
                                elif isinstance(target, ast.Tuple):
                                    for elt in target.elts:
                                        if isinstance(elt, ast.Name):
                                            assigned_names.add(elt.id)
                                            
                unbound = imported_names - assigned_names
                if unbound:
                    usages = {name: [] for name in unbound}
                    
                    # Look for usages OUTSIDE the `else` block of this specific `try` node.
                    # We will just traverse the whole tree, but collect all nodes in the `else` block to exclude them
                    else_nodes = set()
                    for stmt in node.orelse:
                        for subnode in ast.walk(stmt):
                            else_nodes.add(id(subnode))
                    
                    for n in ast.walk(tree):
                        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                            if n.id in usages and id(n) not in else_nodes:
                                usages[n.id].append(n.lineno)
                                
                    for name, lines in usages.items():
                        if len(lines) > 0:
                            if name not in results:
                                results[name] = {'import_line': node.lineno, 'usage_lines': lines, 'count': len(lines)}

    return results if results else None

if __name__ == '__main__':
    src_dir = Path('~/foundry/sandbox/passagemath/passagemath/src/sage').expanduser()
    results = {}
    
    for py_file in src_dir.rglob('*.py'):
        res = find_unbound_imports(py_file)
        if res:
            rel_path = py_file.relative_to(src_dir)
            results[str(rel_path)] = res
            
    for filepath, unbound in sorted(results.items()):
        print(f"\n{filepath}")
        for name, data in sorted(unbound.items()):
            print(f"  - {name} (imported line {data['import_line']}): used {data['count']} time(s) (e.g. lines {data['usage_lines'][:3]})")
