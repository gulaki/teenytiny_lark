from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass(frozen=True)
class SourceLocation:
    line: int | None = None
    column: int | None = None
    start_pos: int | None = None
    end_pos: int | None = None


class Node:
    location: SourceLocation


@dataclass(frozen=True)
class Program(Node):
    statements: tuple[Stmt, ...]
    location: SourceLocation = field(default_factory=SourceLocation)


class Stmt(Node):
    pass


@dataclass(frozen=True)
class Print(Stmt):
    value: Expr | str
    is_string: bool = False
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Input(Stmt):
    name: str
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Let(Stmt):
    name: str
    value: Expr
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class If(Stmt):
    condition: Comparison
    body: tuple[Stmt, ...]
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class While(Stmt):
    condition: Comparison
    body: tuple[Stmt, ...]
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Label(Stmt):
    name: str
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Goto(Stmt):
    name: str
    location: SourceLocation = field(default_factory=SourceLocation)


class Expr(Node):
    pass


@dataclass(frozen=True)
class Number(Expr):
    value: str
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Variable(Expr):
    name: str
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Grouped(Expr):
    value: Expr
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Unary(Expr):
    operator: str
    operand: Expr
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: str
    right: Expr
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class Comparison(Expr):
    left: Expr
    operator: str
    right: Expr
    location: SourceLocation = field(default_factory=SourceLocation)


StmtType = Union[Print, Input, Let, If, While, Label, Goto]
