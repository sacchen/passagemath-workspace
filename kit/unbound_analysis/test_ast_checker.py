import ast
import sys
from pathlib import Path

def is_control_flow_terminator(node):
    return isinstance(node, (ast.Return, ast.Raise, ast.Continue, ast.Break))

def has_terminator(body):
    for stmt in body:
        if is_control_flow_terminator(stmt):
            return True
    return False

def get_assigned_names(node):
    names = set()
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            names.add(elt.id)
    return names

def get_enclosing_scope(tree, target_node):
    # Find the innermost FunctionDef, ClassDef, or Module that contains the target_node
    # We can do this by keeping a parent map or walking down.
    parent_map = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent_map[child] = node
            
    current = target_node
    while current in parent_map:
        current = parent_map[current]
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            return current
    return tree

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=str(filepath))
    except Exception:
        return []

    issues = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            has_import_error_handler = False
            terminates = False
            for handler in node.handlers:
                # Check for `except ImportError:` or bare `except:`
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
                    assigned_names.update(get_assigned_names(handler))
                                            
                unbound = imported_names - assigned_names
                if not unbound:
                    continue

                # To avoid false positives, we need to collect all usages
                # But we must exclude usages that are:
                # 1. Inside the try body
                # 2. Inside the else body
                # 3. Inside the except body
                
                safe_nodes = set()
                for stmt in node.body + node.orelse:
                    for subnode in ast.walk(stmt):
                        safe_nodes.add(id(subnode))
                for handler in node.handlers:
                    for stmt in handler.body:
                        for subnode in ast.walk(stmt):
                            safe_nodes.add(id(subnode))

                scope = get_enclosing_scope(tree, node)

                for name in unbound:
                    # check if it's used elsewhere in the SAME scope
                    usages = []
                    for n in ast.walk(scope):
                        if isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load):
                            if id(n) not in safe_nodes:
                                usages.append(n)
                    
                    if usages:
                        issues.append((name, node.lineno, len(usages)))

    return issues

if __name__ == '__main__':
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    for py_file in src_dir.rglob('*.py'):
        issues = check_file(py_file)
        if issues:
            print(f"{py_file}")
            for name, lineno, count in issues:
                print(f"  - {name} (import line {lineno}): used {count} time(s)")
