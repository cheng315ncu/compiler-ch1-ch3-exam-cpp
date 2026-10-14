# 19 模擬 ParserTest：函式呼叫鏈 Parser

| 項目 | 內容 |
|---|---|
| 程式 | [call_parser.cpp](call_parser.cpp) |
| 類型 | 模擬題（ParserTest 延伸） |
| 測例 | [call_parser.in](call_parser.in) → [call_parser.expected](call_parser.expected) |
| 相關資料夾 | [10-作業ParserTest](../10-作業ParserTest/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror call_parser.cpp -o main
./main < call_parser.in | diff -u call_parser.expected -
```

## Description

ParserTest 的延伸：加入陣列索引 `a[0]`、多個參數 `f(a, b)` 與敘述結尾的 `;`。

Please write a program to read a program source from stdin following the token definition and grammar rules below. If Yes, print each token's type and the string of token separated by a whitespace and end with a newline. If No, print only `invalid input` with a newline (don't output any token!).

※ 請使用 Recursive-Descent-Parsing 撰寫。

| Terminal | Regular Expression |
|---|---|
| ID | `[A-Za-z_][A-Za-z0-9_]*` |
| NUM | `[0-9]+` |
| STRLIT | `"[^"]*"` |
| DOT | `\.` |
| COMMA | `,` |
| SEMI | `;` |
| LBR | `\(` |
| RBR | `\)` |
| LSB | `\[` |
| RSB | `\]` |

### Productions

```text
1  program  → stmts
2  stmts    → stmt stmts
3  stmts    → λ
4  stmt     → call SEMI
5  call     → ID tail
6  tail     → DOT ID tail
7  tail     → LSB NUM RSB tail
8  tail     → LBR args RBR tail
9  tail     → λ
10 args     → arg arg_tail
11 args     → λ
12 arg_tail → COMMA arg arg_tail
13 arg_tail → λ
14 arg      → call
15 arg      → STRLIT
16 arg      → NUM
```

## Input Format

整份輸入是一段程式，token 之間可能有空白或換行。空輸入合法（stmts → λ），不輸出任何東西。

## Output Format

合法：每個 token 一行「種類 原字串」。不合法：只印 `invalid input`。

## Samples

### Sample Input 1

```text
console.log("hello", 3);
```

### Sample Output 1

```text
ID console
DOT .
ID log
LBR (
STRLIT "hello"
COMMA ,
NUM 3
RBR )
SEMI ;
```

### Sample Input 2

```text
a[0].b(c(1), "x");
init();
```

### Sample Output 2

```text
ID a
LSB [
NUM 0
RSB ]
DOT .
ID b
LBR (
ID c
LBR (
NUM 1
RBR )
COMMA ,
STRLIT "x"
RBR )
SEMI ;
ID init
LBR (
RBR )
SEMI ;
```

### Sample Input 3

```text
f(,1);
```

### Sample Output 3

```text
invalid input
```

### Sample Input 4

```text
f(1)
```

### Sample Output 4

```text
invalid input
```

### Sample Input 5

```text
a[b];
```

### Sample Output 5

```text
invalid input
```

## 解題重點

- `tail` 的三種延伸看目前 token 決定：DOT、LSB、LBR；都不是就走 λ 回到 `stmt`，再要求 SEMI。
- `args → λ` 只在下一個 token 是 RBR 時成立；因此 `f()` 合法、`f(,1)` 不合法。
- `arg → call` 讓參數可以再巢狀呼叫：`b(c(1), "x")`。
- 索引只接受 NUM：`a[b]` 不合法。
