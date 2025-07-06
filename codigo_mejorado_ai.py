# Este módulo se implementará en la app para generar versiones mejoradas de archivos de código
# usando sugerencias detectadas previamente. Esta primera versión se centrará en añadir docstrings automáticamente.

import ast
import astor

class DocstringAdder(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        if not ast.get_docstring(node):
            doc = ast.Expr(value=ast.Str(s="""Describe aquí la funcionalidad del método."""))  # type: ignore
            node.body.insert(0, doc)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        return node

def mejorar_codigo_con_docstrings(code):
    try:
        tree = ast.parse(code)
        transformer = DocstringAdder()
        improved_tree = transformer.visit(tree)
        ast.fix_missing_locations(improved_tree)
        return astor.to_source(improved_tree)
    except Exception as e:
        return f"# Error al intentar mejorar el código: {e}\n\n" + code
