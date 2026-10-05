from teenytiny.compiler import Compiler
from teenytiny.errors import ParseError, SemanticError


COMPILER = Compiler()


def test_fibonacci_compiles():
    source = '''\
PRINT "How many fibonacci numbers do you want?"
INPUT nums
LET a = 0
LET b = 1
WHILE nums > 0 REPEAT
    PRINT a
    LET c = a + b
    LET a = b
    LET b = c
    LET nums = nums - 1
ENDWHILE
'''
    result = COMPILER.compile(source)
    assert "#include <stdio.h>" in result.c_source
    assert "while ((nums > 0))" in result.c_source
    assert "c = (a + b);" in result.c_source


def test_nested_if_and_while():
    source = '''\
LET x = 5
IF x >= 5 THEN
    PRINT "yes"
    WHILE x > 0 REPEAT
        LET x = x - 1
    ENDWHILE
ENDIF
'''
    result = COMPILER.compile(source)
    assert "if ((x >= 5))" in result.c_source
    assert "while ((x > 0))" in result.c_source


def test_parentheses_are_supported():
    result = COMPILER.compile("LET x = (2 + 3) * 4\nPRINT x\n")
    assert "((2 + 3) * 4)" in result.c_source


def test_undeclared_read_is_rejected():
    try:
        COMPILER.compile("PRINT x\n")
    except SemanticError as exc:
        assert "undeclared variable" in str(exc)
    else:
        raise AssertionError("expected SemanticError")


def test_undeclared_goto_is_rejected():
    try:
        COMPILER.compile("GOTO nowhere\n")
    except SemanticError as exc:
        assert "undeclared label" in str(exc)
    else:
        raise AssertionError("expected SemanticError")


def test_duplicate_label_is_rejected():
    try:
        COMPILER.compile("LABEL x\nLABEL x\n")
    except SemanticError as exc:
        assert "duplicate label" in str(exc)
    else:
        raise AssertionError("expected SemanticError")


def test_comments_and_blank_lines():
    result = COMPILER.compile("# comment\n\nLET x = 2 # inline\nPRINT x\n")
    assert "float x;" in result.c_source


def test_bad_syntax_is_rejected():
    try:
        COMPILER.compile("LET = 4\n")
    except ParseError:
        pass
    else:
        raise AssertionError("expected ParseError")
