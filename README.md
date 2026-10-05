# Teeny Tiny Compiler — Python + Lark

A modern rewrite of Austin Z. Henley's three-part Teeny Tiny compiler tutorial.

The original compiler is deliberately educational: it has a hand-written lexer, a hand-written recursive-descent parser, and an emitter that produces C. This version keeps the language and C target, but changes the architecture so that language evolution does not require rewriting the compiler front-end.

## Architecture

```text
                         ┌────────────────────┐
 source ────────────────►│ Lark LALR parser    │
                         │ contextual lexer    │
                         └─────────┬──────────┘
                                   │ parse tree
                                   ▼
                         ┌────────────────────┐
                         │ ASTBuilder         │
                         │ concrete → AST     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ SemanticAnalyzer   │
                         │ symbols / labels   │
                         └─────────┬──────────┘
                                   │
                         ┌─────────┴──────────┐
                         ▼                    ▼
                  ┌──────────────┐     ┌───────────────┐
                  │ CEmitter     │     │ future backend│
                  │ AST → C      │     │ AST → LLVM... │
                  └──────┬───────┘     └───────────────┘
                         │
                         ▼
                       C file
                         │
               ┌─────────┴──────────┐
               ▼                    ▼
             Make                 Ninja
```

## Why this structure?

### 1. Grammar is data

`teenytiny/grammar/teenytiny.lark` is the language syntax. You can change the grammar without editing a hand-written lexer or parser.

### 2. AST is the compiler contract

The parser produces a stable AST. Semantic analysis and code generation consume the AST rather than Lark's `Tree` objects. This prevents the parser library from leaking through the compiler.

### 3. Semantic analysis is separate

Variable and label checks are not mixed into parsing or C generation. This becomes important as soon as the language gets scopes, functions, classes, types, or overload resolution.

### 4. Backends are replaceable

`CEmitter` is just one backend. A future LLVM, bytecode, interpreter, or another source-language backend can consume the same AST/semantic model.

### 5. Build generation is separate from compilation

Make/Ninja support is not tangled into code generation. More build systems can be added behind `BuildSystem`.

## Install

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e .
```

## Compile

```bash
python -m teenytiny.cli examples/fibonacci.teeny -o build/fibonacci.c
```

Generate Make:

```bash
python -m teenytiny.cli examples/fibonacci.teeny \
  -o build/fibonacci.c \
  --build make \
  --build-output build/Makefile
```

Generate Ninja:

```bash
python -m teenytiny.cli examples/fibonacci.teeny \
  -o build/fibonacci.c \
  --build ninja \
  --build-output build/build.ninja
```

## Test

```bash
python -m pytest
```

## Extending the language

### Add a new syntax construct

1. Add its syntax to `grammar/teenytiny.lark`.
2. Add an AST node to `teenytiny/ast.py`.
3. Add a Transformer method in `parser.py`.
4. Add semantic checks in `semantics.py`.
5. Add code generation in the backend(s).
6. Add tests.

For example, a future function syntax could be:

```text
FUNCTION fib(n)
    IF n <= 1 THEN
        RETURN n
    ENDIF
    RETURN fib(n - 1) + fib(n - 2)
ENDFUNCTION
```

The grammar would gain `function_decl`, `parameter_list`, `return_stmt`, and `call_expr`; the AST would gain `FunctionDecl`, `Return`, and `Call`; semantic analysis would gain scopes and function signatures; the C backend would translate those nodes.

### Add classes

Classes should not be bolted directly onto `CEmitter`. Add a type/symbol layer first:

```text
ClassDecl
  ├── fields
  └── methods

TypeInfo
Scope
Symbol
FunctionSignature
```

Then choose how the target represents objects: C structs + functions, C++, LLVM IR, etc.

### Change the surface syntax

The compiler does not care whether the grammar eventually becomes BASIC-like, C-like, Python-like, or something completely custom. Change the `.lark` grammar and update the AST transformer to preserve the same semantic concepts.

For a larger syntax redesign, keep the AST stable whenever possible. That lets source syntax evolve independently from the compiler's middle-end and backends.
