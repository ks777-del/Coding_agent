# graph/code_graph_builder.py

import ast
from typing import Dict
from .project_graph import ProjectGraph


class CodeGraphBuilder:
    """
    Converts raw code into structural graph representation.
    """

    def build(self, project_files: Dict[str, str]) -> ProjectGraph:

        graph = ProjectGraph()

        for file, code in project_files.items():

            graph.add_node(file)

            try:
                tree = ast.parse(code)
            except:
                continue

            for node in ast.walk(tree):

                # function relationships
                if isinstance(node, ast.FunctionDef):
                    func_node = f"{file}:{node.name}"
                    graph.add_edge(file, func_node, "contains_function")

                # class relationships
                if isinstance(node, ast.ClassDef):
                    class_node = f"{file}:{node.name}"
                    graph.add_edge(file, class_node, "contains_class")

                # imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        graph.add_edge(file, alias.name, "imports")

                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        graph.add_edge(file, node.module, "imports_from")

        return graph