#!/usr/bin/env python3
"""Focused short-template regressions, differential checks, and independent oracles."""
from fractions import Fraction
from pathlib import Path
import itertools
import json
import os
import random
import re
import shlex
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parent
SHORT = ROOT / "exam/short"
checks = 0

def run(name, data):
    if isinstance(data, str): data = data.encode()
    return subprocess.run([str(bins[name])], input=data, capture_output=True, timeout=30)

def expect(name, data, output=None, error=False):
    global checks
    result = run(name, data)
    if error:
        assert result.returncode == 1 and result.stdout == b"" and result.stderr, (name, result)
    else:
        assert result.returncode == 0 and result.stderr == b"", (name, result)
        if output is not None: assert result.stdout == output.encode(), (name, result.stdout, output)
    checks += 1
    return result.stdout.decode()

def same(name, reference, data):
    global checks
    a, b = run(name, data), run(reference, data)
    assert a.returncode == b.returncode and a.stdout == b.stdout, (name, data[:300], a, b)
    assert bool(a.stderr) == bool(b.stderr), (a, b)
    checks += 1

with tempfile.TemporaryDirectory(prefix="compiler-short-") as scratch:
    bins = {}
    flags = ["-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror"]
    sanitizer = "--sanitize" in sys.argv
    flags += ["-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"] if sanitizer else ["-O2"]
    def build(name, source):
        binary = Path(scratch) / name
        subprocess.run([*shlex.split(os.environ.get("CXX", "c++")), *flags, str(source), "-o", str(binary)], check=True, timeout=120)
        bins[name] = binary
    for src in sorted(SHORT.glob("*.cpp")):
        build(src.stem, src)
        data, answer = src.with_suffix(".in").read_text(), src.with_suffix(".expected").read_text()
        for variant in [data, data.replace("\n", "\r\n"), data.rstrip("\n")]: expect(src.stem, variant, answer)
    for name in ["lexer", "stack_vm", "ll1"]:
        src = ROOT / "exam" / (name + ".cpp")
        build(name, src)
        data, answer = src.with_suffix(".in").read_text(), src.with_suffix(".expected").read_text()
        for variant in [data, data.replace("\n", "\r\n"), data.rstrip("\n")]: expect(name, variant, answer)
    for name, path in [("html_full", "exam/html_parser.cpp"), ("nfa_full", "exam/nfa_to_dfa.cpp"), ("ac_full", "ch02/ac_homework.cpp")]:
        build(name, ROOT / path)
    for mode in ["postfix", "ast"]:
        src = Path(scratch) / (mode + ".cpp")
        src.write_text((SHORT / "expression.cpp").read_text().replace('const string MODE = "eval";', 'const string MODE = "' + mode + '";'))
        build(mode, src)
    src = Path(scratch) / "hw5d.cpp"
    src.write_text((SHORT / "hw5_check.cpp").read_text().replace('HW5A = true', 'HW5A = false'))
    build("hw5d", src)
    for data in ["", "text", "<p/>", "<P>Hello</p>", "<br><img src=x>", "<p a b c='>' d=abc>t</p>",
                 "<!DOCTYPE html><html><body></body></html>", "<script>if(a<b){s='<div>';}</SCRIPT >",
                 "<textarea><b>text</b></textarea>", "<style>a>b{}</style>", "<p><!--<b>--></p>",
                 "<script>'</scriptx>'</script>", "<p a='1' b = 2></p>", "<p a=x/>hi</p>", "<p a=x />"]:
        expect("html_check", data, "VALID\n"); same("html_check", "html_full", data)
    for data in ["<a><b></a></b>", "<p>", "</p>", "<br></br>", "<!--x", '<p a="x>', '<p a="1"b="2"></p>',
                 "<p a=></p>", "<p a=1 A=2></p>", "<script>x", "<!DOCTYPE svg>", "<div / >", "a\x00b", "<p>a<p>b</p>"]:
        expect("html_check", data, "INVALID\n"); same("html_check", "html_full", data)
    expect("html_check", "<a>" * 10000 + "</a>" * 10000, "VALID\n")
    rng = random.Random(14)
    html_differential = 0
    for _ in range(200):
        data = "<" + rng.choice(["p", "P", "script", "br", "x"]) + rng.choice(["", " a", " a=1", " a='>'", " a=", " a=1 a=2", " a=x/", " a=1b=2"]) + rng.choice([">", "/>", " >", " / >"]) + rng.choice(["", "hi", "<a>", "<!--x-->", "</p>", "</SCRIPT>", "</x>"])
        same("html_check", "html_full", data); html_differential += 1
    expect("postfix", "a+b*c\n-2*-3\n", "a b c * +\n2 neg 3 neg *\n")
    expect("ast", "a+b*c\n100-30-1\n", "(+ a (* b c))\n(- (- 100 30) 1)\n")
    for mode in ["expression", "postfix", "ast"]:
        for bad in ["\n", "1+", "2(3)", "(2", "2)", "1e+", "1e", "@", "1\x00", "()", "."]: expect(mode, bad, error=True)
        expect(mode, "(" * 257 + "1" + ")" * 257, error=True)
        expect(mode, "(" * 256 + "1" + ")" * 256, "1\n")
    for bad in ["x", "1/0", "1e99999", "1e4000*1e4000", "1\n2+", "1+2abc"]: expect("expression", bad, error=True)
    expect("expression", "1+" * 10000 + "1", "10001\n")
    def expression(depth):
        if not depth or rng.random() < .3:
            n = rng.randint(1, 20); return str(n), Fraction(n)
        a, x = expression(depth - 1); b, y = expression(depth - 1)
        op = rng.choice("+-*/")
        if op == "/" and not y: op = "+"
        v = {"+": lambda: x+y, "-": lambda: x-y, "*": lambda: x*y, "/": lambda: x/y}[op]()
        return "(" + a + op + b + ")", v
    expression_oracles = 200
    for _ in range(expression_oracles):
        text, answer = expression(4)
        result = float(expect("expression", text))
        assert abs(result-float(answer)) <= 1e-12 * max(1, abs(float(answer))), (text, result, answer)
    for data in ["", "i x", "i x x=100 x=x+30+1 p x", "f b i a a=5 b=a+3.2 p b", "f b i a a=5 b=3.2+a p b",
                 "floatx x=123e-22 px", "floatx x=001.20e+2 px", "floatx x=0e-3 px", "f x x=2 px", "i x x=100-30-1 px",
                 "f b i a a=5 b=a+1+3.2+2+a p b", "floatx inty fl ix", "i x x=" + "1+"*5000 + "1 px"]:
        same("ac_dc", "ac_full", data)
    for bad in ["i x i x", "p x", "x=1", "i x x=1.2", "i x x=1e0", "i x x=", "i x x=1+", "i x x=1 i y", "i x x=1;",
                "i x x=.1", "i x x=1.", "i x x=1e", "i x x=1e+", "f x x=1e10001", "f x x=1e-10001", "i x x=1\x00", "i x x"]:
        expect("ac_dc", bad, error=True); same("ac_dc", "ac_full", bad)
    # Check the two tiny handwritten DFAs against independent regular expressions.
    fixed_words = 0
    for name, alphabet, pattern in [("hw5_check", "abcd", r"(?:a|(?:bc)*d)+"), ("hw5d", "bcd", r"(?:bc)*d")]:
        words = ["".join(w) for n in range(9) for w in itertools.product(alphabet, repeat=n)]
        expected = "".join("ACCEPT\n" if re.fullmatch(pattern, word) else "REJECT\n" for word in words)
        expect(name, "\n".join(words) + "\n", expected); fixed_words += len(words)
    # Random epsilon-NFAs: Python direct simulation is independent of C++ closure.
    nfa_words = 0
    for _ in range(12):
        n = 5; edges = [(a, rng.choice("ab#"), b) for a in range(n) for b in range(n) if rng.random()<.2]
        finals = {i for i in range(n) if rng.random()<.4}
        def closure(states):
            while True:
                more = states | {b for a,c,b in edges if c=="#" and a in states}
                if more == states: return states
                states = more
        words = ["".join(w) for length in range(6) for w in itertools.product("ab", repeat=length)] + ["z"]
        answers = []
        for word in words:
            states = closure({0})
            for c in word: states = closure({b for a,t,b in edges if t==c and a in states}) if c in "ab" else set()
            answers.append("ACCEPT" if states & finals else "REJECT")
        data = f"{n} {len(edges)} 0 {len(finals)}\n" + " ".join(map(str,sorted(finals))) + "\nab\n" + "".join(f"{a} {c} {b}\n" for a,c,b in edges) + "\n".join(words) + "\n"
        expect("nfa_check", data, "\n".join(answers)+"\n"); same("nfa_check", "nfa_full", data)
        nfa_words += len(words)
    for bad in ["0 0 0 0", "2 0 2 0\nab", "2 0 0 2\n1 1\nab", "2 1 0 0\nab\n0 z 1", "2 0 0 0\naab", "2 0 0 0\n#"]: expect("nfa_check", bad, error=True)
    report = dict(checks=checks, sanitizer=sanitizer, html_differential=html_differential, expression_oracles=expression_oracles, fixed_dfa_words=fixed_words, random_nfa_words=nfa_words)
    print("PASS:", json.dumps(report))
