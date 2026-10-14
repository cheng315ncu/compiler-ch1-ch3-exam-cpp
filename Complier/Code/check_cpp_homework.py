#!/usr/bin/env python3
"""Compile/run the two homework programs in scratch space. No binaries in vault.
Usage: python3 Complier/Code/check_cpp_homework.py [--sanitize]
CXX=g++ is supported; only Python stdlib is required by this checker.
"""
import itertools
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
checks = 0


def expect(binary, source, expected, *args, error=None):
    global checks
    result = subprocess.run([str(binary), *args], input=source, capture_output=True, timeout=30)
    if error:
        assert result.returncode == 1, result
        assert result.stdout == b"", result.stdout
        assert error.encode() in result.stderr, result.stderr
    else:
        assert result.returncode == 0, result.stderr.decode()
        assert result.stderr == b"", result.stderr
        assert result.stdout == expected, (args, source[:100], result.stdout[:1000], expected[:1000])
    checks += 1
    return result.stdout


with tempfile.TemporaryDirectory(prefix="compiler-cpp-") as scratch:
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    flags = ["-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror"]
    flags += ["-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"] if "--sanitize" in sys.argv else ["-O2"]
    ac, automata = Path(scratch) / "ac", Path(scratch) / "automata"
    for source, binary in [(ROOT / "ch02/ac_homework.cpp", ac), (ROOT / "ch03/automata_homework.cpp", automata)]:
        subprocess.run([*compiler, *flags, str(source), "-o", str(binary)], check=True, timeout=120)
    sample = (ROOT / "ch02/ac_homework.in").read_bytes()
    code = (ROOT / "ch02/ac_homework.expected").read_bytes()
    for data in [sample, sample.replace(b"\n", b"\r\n"), sample.rstrip(b"\n"), b"ixx=100x=x+30+1px"]:
        expect(ac, data, code)
    expect(ac, sample, b"OK\n", "--check")
    expect(ac, sample, b"(Prog intdcl x (= id x 100) (= id x (+ (+ id x 30) 1)) print x)\n", "--ast")
    folded = b"100\nsx\n0 k\nlx\n31\n+\nsx\n0 k\nlx\np\nsi\n"
    expect(ac, sample, folded, "--fold")
    expect(ac, sample, b"(Prog intdcl x (= id x 100) (= id x (+ id x 31)) print x)\n", "--ast", "--fold")
    expect(ac, b"", b"(Prog (Dcls epsilon) (Stmts epsilon) $)\n", "--parse-tree")
    parse_result = subprocess.run([str(ac), "--parse-tree"], input=sample, capture_output=True, check=True).stdout.decode()
    assert parse_result == "(Prog (Dcls (Dcl (intdcl i) (id x)) (Dcls epsilon)) (Stmts (Stmt (id x) (assign =) (Val (inum 100)) (Expr epsilon)) (Stmts (Stmt (id x) (assign =) (Val (id x)) (Expr (plus +) (Val (inum 30)) (Expr (plus +) (Val (inum 1)) (Expr epsilon)))) (Stmts (Stmt (print p) (id x)) (Stmts epsilon)))) $)\n"
    checks += 1
    for source, error in [
        (b"i x i x", "duplicate"), (b"p x", "undeclared"), (b"x=1", "undeclared"),
        (b"i x x=1.2", "cannot assign"), (b"i x x=1e0", "cannot assign"),
        (b"i x x=", "expected value"), (b"i x x=1+", "expected value"),
        (b"i x x=1 i y", "expected id"), (b"i x x=1;", "invalid byte"),
        (b"i x x=.1", "invalid byte"), (b"i x x=1.", "decimal point"),
        (b"i x x=1e", "exponent"), (b"i x x=1e+", "exponent"),
        (b"float x x=1e10001", "exceeds"), (b"float x x=1e-10001", "exceeds"),
        (b"i x x=1 p x @", "invalid byte"), (b"i x x=1\x00", "invalid byte"),
    ]:
        expect(ac, source, b"", error=error)
    expect(ac, b"floatx inty fl ix", b"floatdcl float\nid x\nintdcl int\nid y\nfloatdcl f\nid l\nintdcl i\nid x\n$\n", "--tokens")
    expect(ac, b"12 12.3 1.0e10 123e-22 12e+3", b"inum 12\nfnum 12.3\nfnum 1.0e10\nfnum 123e-22\nfnum 12e+3\n$\n", "--tokens")
    expect(ac, b"floatx x=123e-22 px", b"0.0000000000000000000123\nsx\n0 k\nlx\np\nsi\n")
    expect(ac, b"floatx x=001.20e+2 px", b"120\nsx\n0 k\nlx\np\nsi\n")
    expect(ac, b"floatx x=0e-3 px", b"0.000\nsx\n0 k\nlx\np\nsi\n")
    expect(ac, b"i x x=100 x=x-30-1 p x", b"100\nsx\n0 k\nlx\n30\n-\n1\n-\nsx\n0 k\nlx\np\nsi\n", "--fold")
    expect(ac, b"i x x=999999999999999999999999+1 p x", b"1000000000000000000000000\nsx\n0 k\nlx\np\nsi\n", "--fold")
    mixed = expect(ac, b"f b i a a=5 b=a+3.2 p b", b"5\nsa\n0 k\nla\n5 k\n3.2\n+\nsb\n0 k\nlb\np\nsi\n")
    expect(ac, b"floatx x=2 px", b"2\n5 k\nsx\n0 k\nlx\np\nsi\n")
    expect(ac, b"i x", b"", "--tokens", "--fold", error="--fold requires")
    expect(ac, b"", b"", "--unknown", error="usage")
    long_program = b"i x x=" + b"1+" * 5000 + b"1 p x"
    expect(ac, long_program, b"5001\nsx\n0 k\nlx\np\nsi\n", "--fold")
    expect(ac, b" " * 70000 + sample, code)
    words = (ROOT / "ch03/automata_homework.in").read_bytes()
    expected = (ROOT / "ch03/automata_homework.expected").read_bytes()
    expect(automata, words, expected, "5a")
    expect(automata, words.replace(b"\n", b"\r\n"), expected, "5a")
    expect(automata, b"d\nbcd\nbcbcd\n\nbc\nbd\nbcdd\ndd\na\n", b"ACCEPT\nACCEPT\nACCEPT\nREJECT\nREJECT\nREJECT\nREJECT\nREJECT\nREJECT\n", "5d")
    expect(automata, b" a\na \na\x00\nz\na", b"REJECT\nREJECT\nREJECT\nREJECT\nACCEPT\n", "5a")
    expect(automata, b"", b"", "invalid", error="usage")
    total_words = 0
    for exercise, alphabet, pattern, count in [("5d", "bcd", r"(?:bc)*d", 5), ("5a", "abcd", r"(?:a|(?:bc)*d)+", 6)]:
        cases = ["".join(chars) for length in range(9) for chars in itertools.product(alphabet, repeat=length)]
        data = ("\n".join(cases) + "\n").encode()
        wanted = "".join("ACCEPT\n" if re.fullmatch(pattern, word) else "REJECT\n" for word in cases).encode()
        expect(automata, data, wanted, exercise)
        total_words += len(cases)
        table = subprocess.run([str(automata), exercise, "--table"], capture_output=True, check=True).stdout.decode()
        assert f"DFA start=0 states={count}\n" in table
        assert "{} reject" in table
        rows = table.split(f"DFA start=0 states={count}\n")[1]
        wanted_rows = (
            "0 {1,2,5} reject b->1 c->2 d->3\n1 {3} reject b->2 c->4 d->2\n"
            "2 {} reject b->2 c->2 d->2\n3 {6} accept b->2 c->2 d->2\n4 {2,4,5} reject b->1 c->2 d->3\n"
            if exercise == "5d" else
            "0 {1,2,3,6,7,10} reject a->1 b->2 c->3 d->4\n"
            "1 {2,3,4,5,6,7,10,12} accept a->1 b->2 c->3 d->4\n"
            "2 {8} reject a->3 b->3 c->5 d->3\n3 {} reject a->3 b->3 c->3 d->3\n"
            "4 {2,3,5,6,7,10,11,12} accept a->1 b->2 c->3 d->4\n5 {7,9,10} reject a->3 b->2 c->3 d->4\n"
        )
        assert rows == wanted_rows, rows
        checks += 1
    # Independent dc execution checks emitted code, rather than only its spelling.
    dc = shutil.which("dc")
    if dc:
        for program, answer in [(code, b"131\n"), (folded, b"131\n"), (mixed, b"8.2\n")]:
            result = subprocess.run([dc], input=program, capture_output=True, check=True)
            assert result.stdout == answer, result
            assert result.stderr == b"", result.stderr
            checks += 1
    print(f"PASS: 2 C++17 builds; {checks} checks; {total_words} NFA/DFA/regex words (length <= 8); dc={'verified' if dc else 'unavailable'}; sanitizer={'on' if '--sanitize' in sys.argv else 'off'}")
