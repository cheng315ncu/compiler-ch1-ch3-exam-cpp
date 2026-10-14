#!/usr/bin/env python3
"""Run six exam programs: fixtures, malformed input, CRLF, deep input and independent oracles."""
from fractions import Fraction
import itertools
import math
import os
from pathlib import Path
import random
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent / "exam"
checks = 0


def run(name, data, args=(), expected=None, error=None, error_output=b""):
    global checks
    if isinstance(data, str):
        data = data.encode()
    result = subprocess.run([str(binaries[name]), *args], input=data, capture_output=True, timeout=30)
    if error:
        assert result.returncode == 1, result
        assert result.stdout == error_output, result.stdout
        assert error.encode() in result.stderr, result.stderr
    else:
        assert result.returncode == 0, result.stderr.decode()
        assert result.stderr == b"", result.stderr
        if expected is not None:
            if isinstance(expected, str):
                expected = expected.encode()
            assert result.stdout == expected, (name, data[:200], result.stdout[:1500], expected[:1500])
    checks += 1
    return result.stdout.decode()


with tempfile.TemporaryDirectory(prefix="compiler-exam-") as scratch:
    binaries = {}
    flags = ["-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror"]
    sanitize = "--sanitize" in sys.argv
    flags += ["-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"] if sanitize else ["-O2"]
    for source in sorted(ROOT.glob("*.cpp")):
        binary = Path(scratch) / source.stem
        subprocess.run([*shlex.split(os.environ.get("CXX", "c++")), *flags, str(source), "-o", str(binary)], check=True, timeout=120)
        binaries[source.stem] = binary
        data, expected = source.with_suffix(".in").read_bytes(), source.with_suffix(".expected").read_bytes()
        run(source.stem, data, expected=expected)
        run(source.stem, data.replace(b"\n", b"\r\n"), expected=expected)
        run(source.stem, data.rstrip(b"\n"), expected=expected)
    for data in ["", "text", "<p/>", "<P>Hello</p>", "<br><img src=x>", "<p a b c='>' d=abc>t</p>",
                 "<!DOCTYPE html><html><body></body></html>", "<script>if(a<b){s='<div>';}</SCRIPT >",
                 "<textarea><b>text</b></textarea>", "<style>a>b{}</style>", "<p><!--<b>--></p>",
                 "<script>'</scriptx>'</script>", "<p a='1' b = 2></p>"]:
        run("html_parser", data, expected="VALID\n")
    for data, message in [("<a><b></a></b>", "mismatched"), ("<p>", "unclosed element"),
                          ("</p>", "mismatched"), ("<br></br>", "mismatched"),
                          ("<!--x", "unclosed comment"), ('<p a="x>', "unclosed attribute"),
                          ('<p a="1"b="2"></p>', "separating whitespace"), ("<p a=></p>", "empty unquoted"),
                          ("<p a=1 A=2></p>", "duplicate"), ("<script>x", "unclosed raw"),
                          ("<!DOCTYPE svg>", "only DOCTYPE"), ("<div / >", "expected name"),
                          ("a\x00b", "invalid input"), ("<p>a<p>b</p>", "unclosed element")]:
        run("html_parser", data, expected="INVALID\n")
        run("html_parser", data, ("--tree",), error=message)
    run("html_parser", '<p a=x/>hi</p>', ("--tokens",), 'START "p" open a="x/"\nTEXT "hi"\nEND "p"\n')
    run("html_parser", '<p a=x />', ("--tokens",), 'START "p" closed a="x"\n')
    run("html_parser", '<p a="a>b">x</p>', ("--tree",), 'DOCUMENT ""\n  START "p"\n    @a="a>b"\n    TEXT "x"\n')
    run("html_parser", '<p>Hello<br>world &amp;</p><!--no-->', ("--text",), 'Helloworld &amp;')
    run("html_parser", '</p>', ("--tokens",), 'END "p"\n')  # Lexing alone does not check nesting.
    run("html_parser", '<x>' * 10000 + '</x>' * 10000, expected="VALID\n")
    for data, result in [('2+3*4', '14\n'), ('100-30-1', '69\n'), ('8/2/2', '2\n'),
                         ('-2*-3', '6\n'), ('--2', '2\n'), ('1+-2', '-1\n'), ('-(2+3)*4', '-20\n'),
                         ('1e+2+.5', '100.5\n'), ('(+3)', '3\n'), ('-0', '0\n')]:
        run("expression", data, ("--eval",), result)
    run("expression", 'a+b*c', ("--ast",), '(+ a (* b c))\n')
    run("expression", '-(x+2)', ("--postfix",), 'x 2 + neg\n')
    for data, message in [('', None), ('\n', 'empty'), ('1+', 'incomplete'), ('()', 'operand'),
                          ('1 2', 'operator'), ('2(3)', 'operator'), ('(1', "unmatched"),
                          ('1)', 'unmatched'), ('1e+', 'exponent'), ('1/**2', 'operand'),
                          ('1/0', 'division'), ('x+1', 'numeric'), ('1;2', 'invalid'), ('1e999999', 'numeric')]:
        run("expression", data, ("--eval",), expected="" if message is None else None, error=message)
    run("expression", '1+' * 10000 + '1', ("--eval",), '10001\n')
    rng = random.Random(20261014)
    def expression(depth):
        if depth == 0 or rng.randrange(4) == 0:
            value = rng.randrange(-20, 21)
            return f"({value})", Fraction(value)
        left, a = expression(depth - 1)
        right, b = expression(depth - 1)
        op = rng.choice("+-*/")
        if op == '/' and b == 0:
            op = '+'
        answer = {'+': lambda: a + b, '-': lambda: a - b, '*': lambda: a * b, '/': lambda: a / b}[op]()
        return f"({left}{op}{right})", answer
    generated = [expression(5) for _ in range(300)]
    answers = run("expression", '\n'.join(e for e, _ in generated), ("--eval",)).splitlines()
    assert len(answers) == len(generated)
    assert all(math.isclose(float(observed), float(value), rel_tol=2e-12, abs_tol=2e-10) for observed, (_, value) in zip(answers, generated))
    run("lexer", 'ifx==1 && x!=2; x<<=2;', expected='ID "ifx"\nOP "=="\nNUM "1"\nOP "&&"\nID "x"\nOP "!="\nNUM "2"\nPUNCT ";"\nID "x"\nOP "<<="\nNUM "2"\nPUNCT ";"\nEOF\n')
    run("lexer", '.5 10. 2E-3 _a__', expected='NUM ".5"\nNUM "10."\nNUM "2E-3"\nID "_a__"\nEOF\n')
    run("lexer", "'a' '\\n' /*comment*/", expected='CHAR "\'a\'"\nCHAR "\'\\\\n\'"\nEOF\n')
    run("lexer", '/*' + 'x' * 70000 + '*/int', expected='KW "int"\nEOF\n')
    for data, message in [('/*', 'block'), ('"abc', 'unclosed'), ('"x\nx"', 'newline'),
                          ("'ab'", 'one character'), ("''", 'one character'), ('12e+', 'exponent'),
                          ('@', 'invalid'), ('\x00', 'invalid'), ('"a\\', 'incomplete escape')]:
        run("lexer", data, error=message)
    grammar = '5\nS -> A B\nA -> a\nA -> #\nB -> b\nB -> #\n'
    table = run("ll1", grammar)
    assert 'FIRST(S)={#,a,b} FOLLOW(S)={$}' in table
    assert 'FIRST(A)={#,a} FOLLOW(A)={$,b}' in table
    assert 'SELECT(3)={$,b}' in table
    run("ll1", grammar + '\na\nb\na b\nb a\na a\n$\nS\n', ("--check",), 'ACCEPT\nACCEPT\nACCEPT\nACCEPT\nREJECT\nREJECT\nREJECT\nREJECT\n')
    run("ll1", '3\nS -> A\nA -> B\nB -> #\n\nx\n', ("--check",), 'ACCEPT\nREJECT\n')
    for conflicting in ['2\nS -> S a\nS -> b\n', '3\nS -> A a\nA -> a\nA -> #\n']:
        assert 'CONFLICT' in run("ll1", conflicting)
        run("ll1", conflicting, ("--check",), error="conflicts")
    for data, message in [('1\nS -> a #\n', 'epsilon'), ('1\nS ->\n', 'epsilon'),
                          ('1\nS -> a | b\n', 'alternative'), ('1\nS -> $\n', 'reserved'), ('1\n', 'missing')]:
        run("ll1", data, error=message)
    header = '3 4 0 1\n2\nab\n0 # 1\n1 # 0\n1 a 1\n1 b 2\n'
    run("nfa_to_dfa", header + '\nb\nab\naab\nba\nz\n', expected='REJECT\nACCEPT\nACCEPT\nACCEPT\nREJECT\nREJECT\n')
    run("nfa_to_dfa", '1 0 0 1\n0\na\n\na\n', expected='ACCEPT\nREJECT\n')
    run("nfa_to_dfa", header + 'ab\n', ("--trace",), '{0,1} --a--> {0,1} --b--> {2} ACCEPT\n')
    for data, message in [('2 1 0 1\n1\na\n0 b 1\n', 'edge'), ('2 0 2 0\na\n', 'start'),
                          ('2 0 0 0\naa\n', 'alphabet'), ('2 0 0 0\na#\n', 'alphabet'),
                          ('2 0 0 2\n1 1\na\n', 'final'), ('0 0 0 0\na\n', 'header')]:
        run("nfa_to_dfa", data, error=message)
    # Independent direct-NFA simulation, including epsilon cycles and nondeterminism.
    nfa_words = 0
    for _ in range(12):
        edges = {(rng.randrange(5), rng.choice('ab#'), rng.randrange(5)) for _ in range(16)}
        finals = {rng.randrange(5), rng.randrange(5)}
        def closure(states):
            while True:
                next_states = states | {t for s, c, t in edges if c == '#' and s in states}
                if next_states == states:
                    return states
                states = next_states
        words = [''.join(chars) for size in range(7) for chars in itertools.product('ab', repeat=size)]
        expected = []
        for word in words:
            active = closure({0})
            for char in word:
                active = closure({t for s, c, t in edges if c == char and s in active})
            expected.append('ACCEPT\n' if active & finals else 'REJECT\n')
        prefix = f'5 {len(edges)} 0 {len(finals)}\n' + ' '.join(map(str, sorted(finals))) + '\nab\n'
        prefix += ''.join(f'{s} {c} {t}\n' for s, c, t in sorted(edges))
        run("nfa_to_dfa", prefix + '\n'.join(words) + '\n', expected=''.join(expected))
        nfa_words += len(words)
    for source, result in [('PUSH 8\nPUSH 2\nSUB\nPRINT', '6\n'),
                           ('PUSH 8\nPUSH 2\nDIV\nPRINT', '4\n'),
                           ('PUSH 2\nDUP\nMUL\nNEG\nPRINT', '-4\n')]:
        run("stack_vm", source, expected=result)
    for data, message in [('ADD', 'underflow'), ('LOAD x', 'undefined'), ('PUSH 1\nPUSH 0\nDIV', 'division'),
                          ('PUSH', 'missing'), ('PUSH 1 2', 'extra'), ('PRINT x', 'extra'),
                          ('PUSH NaN', 'finite'), ('PUSH 1\nSTORE 1x', 'name'), ('PUSH 1\nPRINT\nBOGUS', 'unknown')]:
        run("stack_vm", data, error=message)
    print(f'PASS: {len(binaries)} C++17 programs; {checks} checks; 300 Fraction expression oracles; {nfa_words} random-NFA words; sanitizer={"on" if sanitize else "off"}')
