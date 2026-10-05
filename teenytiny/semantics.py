from __future__ import annotations

from dataclasses import dataclass, field

from .ast import Goto, If, Input, Label, Let, Print, Program, Stmt, Variable, While, Expr, Binary, Unary, Grouped, Comparison
from .errors import SemanticError


@dataclass
class Symbol:
    name: str
    kind: str = "variable"


@dataclass
class SemanticModel:
    symbols: dict[str, Symbol] = field(default_factory=dict)
    labels: set[str] = field(default_factory=set)
    gotos: list[Goto] = field(default_factory=list)


class SemanticAnalyzer:
    """Language-independent semantic checks live here, not in the emitter."""

    def analyze(self, program: Program) -> SemanticModel:
        model = SemanticModel()
        self._visit_statements(program.statements, model)

        for goto in model.gotos:
            if goto.name not in model.labels:
                raise SemanticError(
                    f"GOTO to undeclared label '{goto.name}' at "
                    f"{goto.location.line}:{goto.location.column}"
                )
        return model

    def _visit_statements(self, statements: tuple[Stmt, ...], model: SemanticModel) -> None:
        for stmt in statements:
            if isinstance(stmt, Let):
                model.symbols.setdefault(stmt.name, Symbol(stmt.name))
                self._expr(stmt.value, model)
            elif isinstance(stmt, Input):
                model.symbols.setdefault(stmt.name, Symbol(stmt.name))
            elif isinstance(stmt, Print):
                if not stmt.is_string:
                    self._expr(stmt.value, model)
            elif isinstance(stmt, If):
                self._expr(stmt.condition, model)
                self._visit_statements(stmt.body, model)
            elif isinstance(stmt, While):
                self._expr(stmt.condition, model)
                self._visit_statements(stmt.body, model)
            elif isinstance(stmt, Label):
                if stmt.name in model.labels:
                    raise SemanticError(f"duplicate label '{stmt.name}'")
                model.labels.add(stmt.name)
            elif isinstance(stmt, Goto):
                model.gotos.append(stmt)

    def _expr(self, expr: Expr, model: SemanticModel) -> None:
        if isinstance(expr, Variable):
            # Match the original compiler's permissive behavior: variables are
            # declared when assigned/input, but reading an unknown variable is
            # a semantic error. This can be relaxed later for declarations.
            if expr.name not in model.symbols:
                raise SemanticError(f"use of undeclared variable '{expr.name}'")
        elif isinstance(expr, Grouped):
            self._expr(expr.value, model)
        elif isinstance(expr, Unary):
            self._expr(expr.operand, model)
        elif isinstance(expr, Binary):
            self._expr(expr.left, model)
            self._expr(expr.right, model)
        elif isinstance(expr, Comparison):
            self._expr(expr.left, model)
            self._expr(expr.right, model)
