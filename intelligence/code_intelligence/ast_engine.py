"""
ast_engine.py - V2

Production-grade AST Intelligence Engine
Features:
- AST parsing
- Symbol extraction
- Import extraction
- Class/function analysis
- Call collection
- File caching
- Project indexing
- Symbol registry
- Call graph
- Import graph
- Reference search
"""

from __future__ import annotations

import ast
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


@dataclass(slots=True)
class ImportInfo:
    module: str
    imported_names: List[str]
    lineno: int


@dataclass(slots=True)
class FunctionInfo:
    name: str
    qualified_name: str
    lineno: int
    end_lineno: int
    is_async: bool
    decorators: List[str]
    arguments: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    calls: List[str] = field(default_factory=list)


@dataclass(slots=True)
class ClassInfo:
    name: str
    lineno: int
    end_lineno: int
    bases: List[str]
    decorators: List[str]
    docstring: Optional[str]
    methods: Dict[str, FunctionInfo] = field(default_factory=dict)


@dataclass(slots=True)
class SymbolInfo:
    name: str
    symbol_type: str
    file_path: Optional[str]
    qualified_name: str
    lineno: int


@dataclass(slots=True)
class FileAnalysis:
    path: str
    file_hash: str
    imports: List[ImportInfo]
    functions: Dict[str, FunctionInfo]
    classes: Dict[str, ClassInfo]
    symbols: Dict[str, SymbolInfo]
    syntax_errors: List[str]
    generated_at: float


@dataclass(slots=True)
class ProjectAnalysis:
    files: Dict[str, FileAnalysis]
    symbol_registry: Dict[str, List[SymbolInfo]]
    call_graph: Dict[str, List[str]]
    import_graph: Dict[str, List[str]]
    generated_at: float


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return type(node).__name__


class CallCollector(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        try:
            if isinstance(node.func, ast.Name):
                self.calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.calls.append(safe_unparse(node.func))
        except Exception:
            pass
        self.generic_visit(node)


class SymbolVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.functions = {}
        self.classes = {}
        self.symbols = {}
        self.current_class = None

    def visit_Import(self, node):
        self.imports.append(
            ImportInfo("", [a.name for a in node.names], node.lineno)
        )

    def visit_ImportFrom(self, node):
        self.imports.append(
            ImportInfo(node.module or "", [a.name for a in node.names], node.lineno)
        )

    def visit_ClassDef(self, node):
        cls = ClassInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=getattr(node, "end_lineno", node.lineno),
            bases=[safe_unparse(b) for b in node.bases],
            decorators=[safe_unparse(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node),
        )
        self.classes[node.name] = cls
        self.symbols[node.name] = SymbolInfo(
            node.name, "class", None, node.name, node.lineno
        )

        prev = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = prev

    def visit_FunctionDef(self, node):
        self._process_function(node, False)

    def visit_AsyncFunctionDef(self, node):
        self._process_function(node, True)

    def _process_function(self, node, is_async):
        collector = CallCollector()
        collector.visit(node)

        qn = f"{self.current_class}.{node.name}" if self.current_class else node.name

        fn = FunctionInfo(
            name=node.name,
            qualified_name=qn,
            lineno=node.lineno,
            end_lineno=getattr(node, "end_lineno", node.lineno),
            is_async=is_async,
            decorators=[safe_unparse(d) for d in node.decorator_list],
            arguments=[a.arg for a in node.args.args],
            returns=safe_unparse(node.returns) if node.returns else None,
            docstring=ast.get_docstring(node),
            calls=collector.calls,
        )

        if self.current_class:
            self.classes[self.current_class].methods[node.name] = fn
        else:
            self.functions[node.name] = fn

        self.symbols[qn] = SymbolInfo(
            node.name, "function", None, qn, node.lineno
        )


class CallGraphBuilder:
    def build(self, analyses):
        graph = defaultdict(list)
        for analysis in analyses.values():
            for fn in analysis.functions.values():
                graph[fn.qualified_name].extend(fn.calls)
            for cls in analysis.classes.values():
                for method in cls.methods.values():
                    graph[method.qualified_name].extend(method.calls)
        return dict(graph)


class ImportGraphBuilder:
    def build(self, analyses):
        graph = {}
        for path, analysis in analyses.items():
            imports = []
            for imp in analysis.imports:
                imports.extend(imp.imported_names)
                if imp.module:
                    imports.append(imp.module)
            graph[path] = imports
        return graph


class ASTEngine:
    def __init__(self):
        self.cache = {}
        self.call_graph_builder = CallGraphBuilder()
        self.import_graph_builder = ImportGraphBuilder()

    def analyze_file(self, file_path: str) -> FileAnalysis:
        source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        file_hash = compute_sha256(source)

        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return FileAnalysis(
                file_path, file_hash, [], {}, {}, {}, [str(exc)], time.time()
            )

        visitor = SymbolVisitor()
        visitor.visit(tree)

        return FileAnalysis(
            file_path,
            file_hash,
            visitor.imports,
            visitor.functions,
            visitor.classes,
            visitor.symbols,
            [],
            time.time(),
        )

    def analyze_file_cached(self, file_path):
        source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        h = compute_sha256(source)

        cached = self.cache.get(file_path)
        if cached and cached.file_hash == h:
            return cached

        result = self.analyze_file(file_path)
        self.cache[file_path] = result
        return result

    def build_symbol_registry(self, analyses):
        registry = defaultdict(list)
        for analysis in analyses.values():
            for symbol in analysis.symbols.values():
                registry[symbol.name].append(symbol)
        return dict(registry)

    def index_project(self, root_path: str) -> ProjectAnalysis:
        files = list(Path(root_path).rglob("*.py"))
        analyses = {}

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(self.analyze_file_cached, str(f)) for f in files]

            for future in futures:
                try:
                    result = future.result()
                    analyses[result.path] = result
                except Exception:
                    pass

        return ProjectAnalysis(
            files=analyses,
            symbol_registry=self.build_symbol_registry(analyses),
            call_graph=self.call_graph_builder.build(analyses),
            import_graph=self.import_graph_builder.build(analyses),
            generated_at=time.time(),
        )

    def find_symbol(self, project, symbol_name):
        return project.symbol_registry.get(symbol_name, [])

    def find_references(self, project, symbol_name):
        refs = []
        for file in project.files.values():
            for fn in file.functions.values():
                if symbol_name in fn.calls:
                    refs.append((file.path, fn.qualified_name))

            for cls in file.classes.values():
                for method in cls.methods.values():
                    if symbol_name in method.calls:
                        refs.append((file.path, method.qualified_name))
        return refs
